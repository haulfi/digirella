#===========================================================================================================================
# Greenhouse Model - Decision rules for controlled environment agriculture
#===========================================================================================================================

from typing import Any, Dict
from models.base import BaseModel
from models.registry import register_model
from backend.schema import GreenhouseScenarioData
from .greenhouse_struct import GreenhouseStruct
from ..rules_catalog import reason

@register_model("greenhouse")
class GreenhouseModel(BaseModel):
    name = "greenhouse"
    scenario_data_class = GreenhouseScenarioData

    def _build_struct(self, di, derived):
        return GreenhouseStruct(
            temperature=di.temperature,
            humidity=di.humidity,
            co2_ppm=di.co2_ppm,
            light_hours=di.light_hours,
            fan_status=di.fan_status,
            vent_open_pct=di.vent_open_pct,
            water_available=di.water_available,
            soil_moisture=di.soil_moisture,
            last_watered_hours=di.last_watered_hours,
            stage=di.stage,
            health=di.health,
            whiteflies=di.whiteflies,
            thrips=di.thrips,
            aphids=di.aphids,
            fungal_signs=di.fungal_signs,
            bacterial_signs=di.bacterial_signs,
            virus_signs=di.virus_signs,
            derived=derived,
        )

    def _derive(self, di) -> Dict[str, Any]:
        # Temperature status
        temp_status = "too_hot" if di.temperature >= 32 else ("too_cold" if di.temperature <= 15 else "optimal")

        # Humidity status
        humidity_status = "too_high" if di.humidity >= 85 else ("too_low" if di.humidity <= 45 else "optimal")

        # CO2 level
        co2_status = "high" if di.co2_ppm >= 1000 else ("low" if di.co2_ppm <= 350 else "optimal")

        # Irrigation need
        needs_water = di.soil_moisture < 22 or di.last_watered_hours >= 24

        return {
            "temp_status": temp_status,
            "humidity_status": humidity_status,
            "co2_status": co2_status,
            "needs_water": needs_water,
        }

    def _rule_temperature_control(self, ctx: GreenhouseStruct, recs, not_recs) -> None:
        temp_status = ctx.derived["temp_status"]

        if temp_status == "too_hot":
            self._add_rec(
                recs,
                "ACTIVATE_COOLING",
                "high",
                [
                    reason("temperature_too_high", temp=ctx.temperature),
                    reason("increase_ventilation"),
                ]
            )
        elif temp_status == "too_cold":
            self._add_rec(
                recs,
                "ACTIVATE_HEATING",
                "high",
                [
                    reason("temperature_too_low", temp=ctx.temperature),
                    reason("close_vents"),
                ]
            )

    def _rule_humidity_control(self, ctx: GreenhouseStruct, recs, not_recs) -> None:
        humidity_status = ctx.derived["humidity_status"]

        if humidity_status == "too_high":
            self._add_rec(
                recs,
                "INCREASE_VENTILATION",
                "high",
                [
                    reason("humidity_too_high", humidity=ctx.humidity),
                    reason("disease_risk_high_humidity"),
                ]
            )
        elif humidity_status == "too_low":
            self._add_rec(
                recs,
                "INCREASE_HUMIDITY",
                "medium",
                [reason("humidity_too_low", humidity=ctx.humidity)]
            )

    def _rule_ventilation(self, ctx: GreenhouseStruct, recs, not_recs) -> None:
        co2_status = ctx.derived["co2_status"]

        if co2_status == "high":
            self._add_rec(
                recs,
                "IMPROVE_VENTILATION",
                "medium",
                [
                    reason("co2_too_high", co2=ctx.co2_ppm),
                    reason("air_quality_poor"),
                ]
            )

    def _rule_irrigation(self, ctx: GreenhouseStruct, recs, not_recs) -> None:
        if not ctx.water_available:
            self._add_not(not_recs, "WATER_CROPS", [reason("no_water_available")])
            return

        if ctx.derived["needs_water"]:
            self._add_rec(
                recs,
                "WATER_CROPS",
                "high",
                [
                    reason("soil_moisture_low", sm=ctx.soil_moisture),
                    reason("last_watered", hours=ctx.last_watered_hours),
                ]
            )

    def _rule_pest_management(self, ctx: GreenhouseStruct, recs, not_recs) -> None:
        if ctx.whiteflies:
            self._add_rec(
                recs,
                "TREAT_WHITEFLIES",
                "high",
                [reason("whiteflies_detected")]
            )

        if ctx.thrips:
            self._add_rec(
                recs,
                "TREAT_THRIPS",
                "high",
                [reason("thrips_detected")]
            )

        if ctx.aphids:
            self._add_rec(
                recs,
                "TREAT_APHIDS",
                "medium",
                [reason("aphids_detected")]
            )

    def _rule_disease_management(self, ctx: GreenhouseStruct, recs, not_recs) -> None:
        if ctx.fungal_signs:
            self._add_rec(
                recs,
                "APPLY_FUNGICIDE",
                "high",
                [
                    reason("fungal_infection_detected"),
                    reason("reduce_humidity_disease"),
                ]
            )

        if ctx.bacterial_signs:
            self._add_rec(
                recs,
                "TREAT_BACTERIAL_DISEASE",
                "high",
                [reason("bacterial_infection_detected")]
            )

        if ctx.virus_signs:
            self._add_rec(
                recs,
                "REMOVE_INFECTED_PLANTS",
                "high",
                [reason("virus_detected_remove")]
            )

    def _rule_crop_management(self, ctx: GreenhouseStruct, recs, not_recs) -> None:
        if ctx.stage == "transplant_ready":
            self._add_rec(
                recs,
                "TRANSPLANT_SEEDLINGS",
                "medium",
                [reason("seedlings_ready")]
            )

        if ctx.health == "poor":
            self._add_rec(
                recs,
                "CHECK_NUTRIENT_LEVELS",
                "medium",
                [reason("crop_health_poor")]
            )

    def _apply_rules(self, ctx, recs, not_recs):
        self._rule_temperature_control(ctx, recs, not_recs)
        self._rule_humidity_control(ctx, recs, not_recs)
        self._rule_ventilation(ctx, recs, not_recs)
        self._rule_irrigation(ctx, recs, not_recs)
        self._rule_pest_management(ctx, recs, not_recs)
        self._rule_disease_management(ctx, recs, not_recs)
        self._rule_crop_management(ctx, recs, not_recs)
