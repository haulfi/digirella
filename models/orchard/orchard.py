#===========================================================================================================================
# Orchard (Fruit Trees) Model
# Decision rules for daily orchard management operations
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from typing import Any, Dict
from models.base import BaseModel
from models.registry import register_model
from backend.schema import OrchardScenarioData
from .orchard_struct import OrchardStruct
from ..rules_catalog import reason
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Orchard model class - Auto-registered via decorator
@register_model("orchard")
class OrchardModel(BaseModel):
    name = "orchard"
    scenario_data_class = OrchardScenarioData

    #----------------------------------------------------------------------------------------------------------------------------
    # Build orchard context structure from scenario data and derived buckets
    def _build_struct(self, di, derived):
        return OrchardStruct(
            temperature=di.temperature,
            humidity=di.humidity,
            wind=di.wind,
            rain24=di.rain24,
            frost_forecast=di.frost_forecast,
            soil_moisture=di.soil_moisture,
            soil_temp=di.soil_temp,
            stage=di.stage,
            fruit_load=di.fruit_load,
            health_status=di.health_status,
            codling_moth=di.codling_moth,
            aphids=di.aphids,
            mites=di.mites,
            fire_blight=di.fire_blight,
            scab=di.scab,
            mildew=di.mildew,
            water_available=di.water_available,
            labor_available=di.labor_available,
            derived=derived,
        )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Derive decision buckets from raw sensor values
    def _derive(self, di) -> Dict[str, Any]:
        # Moisture bucket
        moisture_bucket = "low" if di.soil_moisture < 20 else ("adequate" if di.soil_moisture <= 32 else "high")

        # Temperature stress
        temp_stress = "heat" if di.temperature >= 32 else ("cold" if di.temperature <= 5 else "normal")

        # Wet conditions
        wet_conditions = (di.rain24 >= 10) or (di.humidity >= 80)

        # Wind risk
        high_wind = di.wind >= 40

        return {
            "moisture_bucket": moisture_bucket,
            "temp_stress": temp_stress,
            "wet_conditions": wet_conditions,
            "high_wind": high_wind,
        }
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Irrigation rule for orchard
    def _rule_irrigation(self, ctx: OrchardStruct, recs, not_recs) -> None:
        if not ctx.water_available:
            self._add_not(not_recs, "IRRIGATE_ORCHARD", [reason("no_water_available")])
            return

        moisture_bucket = ctx.derived["moisture_bucket"]

        # Critical irrigation need
        if moisture_bucket == "low" and ctx.stage in ["fruit_development", "flowering"]:
            self._add_rec(
                recs,
                "IRRIGATE_ORCHARD",
                "high",
                [
                    reason("soil_moisture_critical", sm=ctx.soil_moisture),
                    reason("critical_growth_stage", stage=ctx.stage),
                ]
            )
        # Regular irrigation needed
        elif moisture_bucket == "low":
            self._add_rec(
                recs,
                "IRRIGATE_ORCHARD",
                "medium",
                [reason("soil_moisture_low", sm=ctx.soil_moisture)]
            )
        # Too wet - don't irrigate
        elif ctx.derived["wet_conditions"] or moisture_bucket == "high":
            self._add_not(
                not_recs,
                "IRRIGATE_ORCHARD",
                [reason("soil_too_wet", sm=ctx.soil_moisture, rain24=ctx.rain24)]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Frost protection rule
    def _rule_frost_protection(self, ctx: OrchardStruct, recs, not_recs) -> None:
        if ctx.frost_forecast and ctx.stage in ["flowering", "early_growth"]:
            self._add_rec(
                recs,
                "ACTIVATE_FROST_PROTECTION",
                "high",
                [
                    reason("frost_warning", temp=ctx.temperature),
                    reason("frost_sensitive_stage", stage=ctx.stage),
                    reason("frost_protection_methods"),
                ]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Pest management rule
    def _rule_pest_management(self, ctx: OrchardStruct, recs, not_recs) -> None:
        if ctx.codling_moth:
            self._add_rec(
                recs,
                "TREAT_CODLING_MOTH",
                "high",
                [
                    reason("codling_moth_detected"),
                    reason("fruit_damage_risk"),
                ]
            )

        if ctx.aphids:
            self._add_rec(
                recs,
                "MONITOR_APHIDS",
                "medium",
                [reason("aphids_present")]
            )

        if ctx.mites:
            self._add_rec(
                recs,
                "TREAT_MITES",
                "medium",
                [reason("mites_detected")]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Disease management rule
    def _rule_disease_management(self, ctx: OrchardStruct, recs, not_recs) -> None:
        if ctx.fire_blight:
            self._add_rec(
                recs,
                "TREAT_FIRE_BLIGHT",
                "high",
                [
                    reason("fire_blight_detected"),
                    reason("prune_infected_branches"),
                ]
            )

        if ctx.scab:
            self._add_rec(
                recs,
                "APPLY_FUNGICIDE_SCAB",
                "high",
                [reason("scab_signs_present")]
            )

        if ctx.mildew:
            self._add_rec(
                recs,
                "TREAT_MILDEW",
                "medium",
                [reason("mildew_detected")]
            )

        # Preventive measures in wet conditions
        if ctx.derived["wet_conditions"] and not (ctx.fire_blight or ctx.scab or ctx.mildew):
            self._add_rec(
                recs,
                "MONITOR_DISEASE",
                "low",
                [reason("wet_conditions_disease_risk", humidity=ctx.humidity, rain24=ctx.rain24)]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Fruit thinning rule
    def _rule_fruit_thinning(self, ctx: OrchardStruct, recs, not_recs) -> None:
        if ctx.fruit_load == "heavy" and ctx.stage == "fruit_development":
            self._add_rec(
                recs,
                "THIN_FRUIT",
                "medium",
                [
                    reason("heavy_fruit_load"),
                    reason("improve_fruit_quality"),
                ]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Fertilization rule
    def _rule_fertilization(self, ctx: OrchardStruct, recs, not_recs) -> None:
        if ctx.stage == "early_growth" and ctx.derived["moisture_bucket"] == "adequate":
            self._add_rec(
                recs,
                "FERTILIZE_ORCHARD",
                "medium",
                [
                    reason("spring_growth_stage"),
                    reason("soil_moisture_adequate", sm=ctx.soil_moisture),
                ]
            )
        elif ctx.derived["wet_conditions"]:
            self._add_not(
                not_recs,
                "FERTILIZE_ORCHARD",
                [reason("too_wet_for_fertilizer")]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Harvest timing rule
    def _rule_harvest(self, ctx: OrchardStruct, recs, not_recs) -> None:
        if ctx.stage == "harvest_ready":
            if not ctx.labor_available:
                self._add_rec(
                    recs,
                    "ARRANGE_HARVEST_LABOR",
                    "high",
                    [reason("harvest_ready_no_labor")]
                )
            else:
                self._add_rec(
                    recs,
                    "BEGIN_HARVEST",
                    "high",
                    [reason("fruit_ready_harvest")]
                )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Storm preparation rule
    def _rule_storm_preparation(self, ctx: OrchardStruct, recs, not_recs) -> None:
        if ctx.derived["high_wind"]:
            self._add_rec(
                recs,
                "SECURE_ORCHARD",
                "high",
                [
                    reason("high_wind_warning", wind=ctx.wind),
                    reason("protect_trees_fruit"),
                ]
            )

            # Don't spray in high wind
            self._add_not(
                not_recs,
                "SPRAY_PESTICIDES",
                [reason("high_wind_no_spray", wind=ctx.wind)]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Apply all orchard decision rules
    def _apply_rules(self, ctx, recs, not_recs):
        self._rule_irrigation(ctx, recs, not_recs)
        self._rule_frost_protection(ctx, recs, not_recs)
        self._rule_pest_management(ctx, recs, not_recs)
        self._rule_disease_management(ctx, recs, not_recs)
        self._rule_fruit_thinning(ctx, recs, not_recs)
        self._rule_fertilization(ctx, recs, not_recs)
        self._rule_harvest(ctx, recs, not_recs)
        self._rule_storm_preparation(ctx, recs, not_recs)
    #----------------------------------------------------------------------------------------------------------------------------
