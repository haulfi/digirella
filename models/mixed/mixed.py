#===========================================================================================================================
# Mixed Farm Model - Balancing crops and small livestock operations
#===========================================================================================================================

from typing import Any, Dict
from models.base import BaseModel
from models.registry import register_model
from backend.schema import MixedScenarioData
from .mixed_struct import MixedStruct
from ..rules_catalog import reason

@register_model("mixed")
class MixedModel(BaseModel):
    name = "mixed"
    scenario_data_class = MixedScenarioData

    def _build_struct(self, di, derived):
        return MixedStruct(
            soil_moisture=di.soil_moisture,
            crop_stage=di.crop_stage,
            crop_health=di.crop_health,
            pest_pressure=di.pest_pressure,
            animal_count=di.animal_count,
            feed_kg=di.feed_kg,
            water_liters=di.water_liters,
            sick_count=di.sick_count,
            labor_hours=di.labor_hours,
            water_available=di.water_available,
            budget_available=di.budget_available,
            temperature=di.temperature,
            rain24=di.rain24,
            rain48_forecast=di.rain48_forecast,
            derived=derived,
        )

    def _derive(self, di) -> Dict[str, Any]:
        # Crop status
        crop_needs_water = di.soil_moisture < 20
        crop_critical = di.crop_stage in ["flowering", "fruit_development"] and di.soil_moisture < 18

        # Livestock status
        feed_per_animal = di.feed_kg / di.animal_count if di.animal_count > 0 else 0
        feed_critical = feed_per_animal < 3
        water_per_animal = di.water_liters / di.animal_count if di.animal_count > 0 else 0
        water_critical = water_per_animal < 8

        # Resource constraints
        labor_limited = di.labor_hours < 6
        multiple_needs = sum([crop_needs_water, feed_critical, water_critical, di.sick_count > 0]) >= 2

        return {
            "crop_needs_water": crop_needs_water,
            "crop_critical": crop_critical,
            "feed_per_animal": round(feed_per_animal, 1),
            "feed_critical": feed_critical,
            "water_per_animal": round(water_per_animal, 1),
            "water_critical": water_critical,
            "labor_limited": labor_limited,
            "multiple_needs": multiple_needs,
        }

    def _rule_crop_irrigation(self, ctx: MixedStruct, recs, not_recs) -> None:
        if not ctx.water_available:
            self._add_not(not_recs, "IRRIGATE_CROPS", [reason("no_water_mixed")])
            return

        if ctx.derived["crop_critical"]:
            self._add_rec(
                recs,
                "IRRIGATE_CROPS_URGENT",
                "high",
                [
                    reason("crop_critical_stage", stage=ctx.crop_stage),
                    reason("soil_moisture_low", sm=ctx.soil_moisture),
                ]
            )
        elif ctx.derived["crop_needs_water"] and not ctx.derived["water_critical"]:
            self._add_rec(
                recs,
                "IRRIGATE_CROPS",
                "medium",
                [reason("crop_needs_irrigation", sm=ctx.soil_moisture)]
            )

    def _rule_livestock_feeding(self, ctx: MixedStruct, recs, not_recs) -> None:
        if ctx.derived["feed_critical"]:
            self._add_rec(
                recs,
                "FEED_ANIMALS_URGENT",
                "high",
                [
                    reason("feed_critical_mixed", per_animal=ctx.derived["feed_per_animal"]),
                    reason("animal_welfare_risk", count=ctx.animal_count),
                ]
            )
        elif ctx.derived["feed_per_animal"] < 5:
            self._add_rec(
                recs,
                "ORDER_FEED_MIXED",
                "medium",
                [reason("feed_low_mixed", per_animal=ctx.derived["feed_per_animal"])]
            )

    def _rule_livestock_watering(self, ctx: MixedStruct, recs, not_recs) -> None:
        if ctx.derived["water_critical"]:
            priority = "high" if not ctx.water_available else "high"
            self._add_rec(
                recs,
                "WATER_ANIMALS_URGENT",
                priority,
                [
                    reason("water_critical_animals", per_animal=ctx.derived["water_per_animal"]),
                    reason("dehydration_risk"),
                ]
            )

    def _rule_health_management(self, ctx: MixedStruct, recs, not_recs) -> None:
        if ctx.sick_count > 0:
            priority = "high" if ctx.sick_count >= 3 else "medium"
            self._add_rec(
                recs,
                "CHECK_SICK_ANIMALS",
                priority,
                [
                    reason("sick_animals_mixed", count=ctx.sick_count),
                    reason("isolate_if_needed"),
                ]
            )

    def _rule_pest_management(self, ctx: MixedStruct, recs, not_recs) -> None:
        if ctx.pest_pressure == "high":
            self._add_rec(
                recs,
                "TREAT_CROP_PESTS",
                "medium",
                [reason("high_pest_pressure")]
            )
        elif ctx.pest_pressure == "medium":
            self._add_rec(
                recs,
                "MONITOR_PEST_LEVELS",
                "low",
                [reason("moderate_pest_pressure")]
            )

    def _rule_harvest_management(self, ctx: MixedStruct, recs, not_recs) -> None:
        if ctx.crop_stage == "harvest_ready":
            self._add_rec(
                recs,
                "HARVEST_CROPS",
                "high",
                [
                    reason("crops_ready_harvest"),
                    reason("timely_harvest_quality"),
                ]
            )

    def _rule_resource_allocation(self, ctx: MixedStruct, recs, not_recs) -> None:
        if ctx.derived["labor_limited"] and ctx.derived["multiple_needs"]:
            self._add_rec(
                recs,
                "PRIORITIZE_TASKS",
                "high",
                [
                    reason("limited_labor", hours=ctx.labor_hours),
                    reason("multiple_operations_needed"),
                    reason("prioritize_animals_first"),
                ]
            )

        if not ctx.budget_available and (ctx.derived["feed_critical"] or ctx.derived["crop_critical"]):
            self._add_rec(
                recs,
                "SECURE_EMERGENCY_FUNDS",
                "high",
                [reason("budget_constraint_critical")]
            )

    def _rule_weather_planning(self, ctx: MixedStruct, recs, not_recs) -> None:
        if ctx.rain48_forecast >= 10 and ctx.derived["crop_needs_water"]:
            self._add_rec(
                recs,
                "DELAY_IRRIGATION_RAIN",
                "low",
                [
                    reason("rain_forecast_mixed", rain=ctx.rain48_forecast),
                    reason("save_water_resources"),
                ]
            )

        if ctx.rain24 >= 15:
            self._add_not(
                not_recs,
                "APPLY_FERTILIZER",
                [reason("heavy_rain_runoff", rain=ctx.rain24)]
            )

    def _apply_rules(self, ctx, recs, not_recs):
        # Priority order: health, water, feed, crops, pests, harvest, resources
        self._rule_health_management(ctx, recs, not_recs)
        self._rule_livestock_watering(ctx, recs, not_recs)
        self._rule_livestock_feeding(ctx, recs, not_recs)
        self._rule_crop_irrigation(ctx, recs, not_recs)
        self._rule_pest_management(ctx, recs, not_recs)
        self._rule_harvest_management(ctx, recs, not_recs)
        self._rule_resource_allocation(ctx, recs, not_recs)
        self._rule_weather_planning(ctx, recs, not_recs)
