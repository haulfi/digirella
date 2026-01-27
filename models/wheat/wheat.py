#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from typing import Any, Dict
from models.base import BaseModel
from models.registry import register_model
from backend.schema import WheatScenarioData
from .wheat_struct import WheatStruct
from ..rules_catalog import reason
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Wheat model class - Auto-registered via decorator
@register_model("wheat")
class WheatModel(BaseModel):
    name = "wheat"
    scenario_data_class = WheatScenarioData

    #----------------------------------------------------------------------------------------------------------------------------
    # Build wheat context structure from scenario data and derived buckets
    # Creates an immutable dataclass with all necessary data for rule evaluation
    def _build_struct(self, di, derived):
        # Initialize wheat context with all sensor data and derived buckets
        return WheatStruct(
            tmax=di.tmax,
            rain24=di.rain24,
            rain48=di.rain48,
            wind=di.wind,
            humidity=di.humidity,
            sm=di.soil_moisture,
            stage=di.stage,
            water_available=di.water_available,
            irrigation_possible=di.irrigation_possible_today,
            aphids=di.aphids_seen,
            rust=di.rust_seen,
            derived=derived,
        )    
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Derive decision buckets from raw sensor values
    # Simplifies complex continuous values into categorical buckets for rule evaluation
    def _derive(self, di) -> Dict[str, Any]:
        moisture_bucket = "low" if di.soil_moisture < 20 else ("adequate" if di.soil_moisture <= 32 else "high")
        weather_bucket = "hot" if di.tmax >= 35 else ("warm" if di.tmax >= 28 else "mild")
        wet_bucket = (di.rain24 >= 5) or (di.humidity >= 85)
        rain_coming = di.rain48 >= 6
        return {
            "moisture_bucket": moisture_bucket,
            "weather_bucket": weather_bucket,
            "wet_bucket": wet_bucket,
            "rain_coming_48h": rain_coming,
        }
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Irrigation decision rule
    # Determines whether to irrigate based on soil moisture, weather, and constraints
    def _rule_irrigation(self, ctx: WheatStruct, recs, not_recs) -> None:
        if not (ctx.irrigation_possible and ctx.water_available):
            self._add_not(
                not_recs,
                "IRRIGATE_TODAY",
                [reason(
                    "irrigation_not_possible",
                    irrigation_possible=ctx.irrigation_possible,
                    water_available=ctx.water_available,
                )]
            )
            return
        moisture_bucket = ctx.derived["moisture_bucket"]
        wet_bucket = ctx.derived["wet_bucket"]
        rain_coming = ctx.derived["rain_coming_48h"]

        # Irrigate with high priority if soil is dry and no rain expected
        if moisture_bucket == "low" and not rain_coming and ctx.rain24 == 0 and not wet_bucket:
            self._add_rec(
                recs,
                "IRRIGATE_TODAY",
                "high",
                [
                    reason("soil_moisture_low", sm=ctx.sm),
                    reason("dry_conditions", rain24=ctx.rain24, humidity=ctx.humidity),
                    reason("no_rain_expected_48h"),
                ]
            )
        # Rain expected soon - delay or reduce irrigation to conserve water
        elif moisture_bucket == "low" and rain_coming:
            self._add_rec(
                recs,
                "IRRIGATE_REDUCED_OR_DELAY",
                "medium",
                [
                    reason("soil_moisture_low_rain_expected", sm=ctx.sm, rain48=ctx.rain48),
                    reason("delay_or_reduce_irrigation"),
                ]
            )
        # Irrigation is not recommended - soil is already wet or has high moisture
        elif wet_bucket or moisture_bucket == "high":
            self._add_not(
                not_recs,
                "IRRIGATE_TODAY",
                [
                    reason("wet_conditions", humidity=ctx.humidity, rain24=ctx.rain24),
                    reason("soil_moisture_level", sm=ctx.sm, moisture_bucket=moisture_bucket),
                ]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Fertilization decision rule
    # Determines optimal timing for fertilization based on crop stage, soil moisture, and weather
    def _rule_fertilize(self, ctx: WheatStruct, recs, not_recs) -> None:
        moisture_bucket = ctx.derived["moisture_bucket"]
        wet_bucket = ctx.derived["wet_bucket"]

        if ctx.stage == "tillering" and moisture_bucket == "adequate" and (ctx.tmax <= 30) and not wet_bucket:
            self._add_rec(
                recs,
                "FERTILIZE_TODAY",
                "medium",
                [
                    reason("stage_is", stage=ctx.stage),
                    reason("soil_moisture_adequate", sm=ctx.sm),
                    reason("weather_suitable", tmax=ctx.tmax, humidity=ctx.humidity),
                ]
            )
        elif wet_bucket or ctx.rain24 >= 10:
            self._add_not(
                not_recs,
                "FERTILIZE_TODAY",
                [
                    reason("high_rain_humidity_runoff"),
                    reason("rain_humidity_values", rain24=ctx.rain24, humidity=ctx.humidity),
                ]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Pest and disease monitoring rule
    # Alerts for aphid sightings and rust disease risk based on observations and weather
    def _rule_pest_disease(self, ctx: WheatStruct, recs) -> None:
        if ctx.aphids:
            self._add_rec(recs, "SCOUT_APHIDS", "medium", [reason("aphids_observed")])

        if ctx.rust or (ctx.humidity >= 90 and ctx.rain24 >= 2):
            self._add_rec(
                recs,
                "RUST_RISK_ALERT",
                "high" if ctx.rust else "medium",
                [
                    reason("rust_signs_observed") if ctx.rust else reason("rust_risk_weather"),
                    reason("humidity_rain_values", humidity=ctx.humidity, rain24=ctx.rain24),
                ]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Spray safety rule
    # Warns against midday spraying when wind or heat conditions reduce effectiveness
    def _rule_spray_safety(self, ctx: WheatStruct, recs) -> None:
        if (ctx.wind >= 6) or (ctx.tmax >= 35):
            self._add_rec(
                recs,
                "AVOID_SPRAY_MIDDAY",
                "low",
                [
                    reason("wind_heat_reduce_spray", wind=ctx.wind, tmax=ctx.tmax),
                    reason("prefer_morning_evening"),
                ]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Apply all wheat decision rules
    # Evaluates all rule categories and populates recommendations and not-recommended lists
    def _apply_rules(self, ctx, recs, not_recs):
        # Check if irrigation is required
        self._rule_irrigation(ctx, recs, not_recs)
        # Check if fertilization is needed
        self._rule_fertilize(ctx, recs, not_recs)
        # Check for pest and disease risks
        self._rule_pest_disease(ctx, recs)
        # Check spray safety conditions
        self._rule_spray_safety(ctx, recs)
