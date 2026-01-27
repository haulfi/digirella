#===========================================================================================================================
# Livestock (Dairy Cattle) Model
# Decision rules for daily dairy farm management operations
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from typing import Any, Dict
from models.base import BaseModel
from models.registry import register_model
from backend.schema import LivestockScenarioData
from .livestock_struct import LivestockStruct
from ..rules_catalog import reason
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Livestock model class - Auto-registered via decorator
@register_model("livestock")
class LivestockModel(BaseModel):
    name = "livestock"
    scenario_data_class = LivestockScenarioData

    #----------------------------------------------------------------------------------------------------------------------------
    # Build livestock context structure from scenario data and derived buckets
    # Creates an immutable dataclass with all necessary data for rule evaluation
    def _build_struct(self, di, derived):
        # Initialize livestock context with all sensor data and derived buckets
        return LivestockStruct(
            temperature=di.temperature_c,
            humidity=di.humidity_pct,
            feed_kg=di.feed_kg,
            water_liters=di.water_liters,
            milk_yield=di.milk_liters,
            animal_count=di.animal_count,
            sick_count=di.sick_count,
            disease_detected=di.disease_detected,
            stress_signs=di.stress_signs,
            vet_available=di.vet_available,
            feed_delivery_today=di.feed_delivery_expected,
            derived=derived,
        )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Derive decision buckets from raw sensor values
    # Simplifies complex continuous values into categorical buckets for rule evaluation
    def _derive(self, di) -> Dict[str, Any]:
        # Feed status bucket
        feed_per_animal = di.feed_kg / di.animal_count if di.animal_count > 0 else 0
        feed_status = "critical" if feed_per_animal < 15 else ("low" if feed_per_animal < 25 else "adequate")

        # Health bucket
        health_bucket = "critical" if di.sick_count > 3 else ("warning" if di.sick_count > 0 else "good")

        # Temperature stress bucket
        temp_stress = di.temperature_c >= 28  # Heat stress threshold for dairy cattle

        # Milk production bucket
        expected_yield = di.animal_count * 20  # Expected ~20L per cow per day
        milk_bucket = "low" if di.milk_liters < expected_yield * 0.7 else ("adequate" if di.milk_liters < expected_yield * 0.9 else "good")

        return {
            "feed_status": feed_status,
            "health_bucket": health_bucket,
            "temp_stress": temp_stress,
            "milk_bucket": milk_bucket,
            "feed_per_animal": round(feed_per_animal, 1),
        }
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Feeding management rule
    # Determines feeding schedule and feed ordering based on availability
    def _rule_feeding(self, ctx: LivestockStruct, recs, not_recs) -> None:
        feed_status = ctx.derived["feed_status"]
        feed_per_animal = ctx.derived["feed_per_animal"]

        # Critical feed shortage - urgent action needed
        if feed_status == "critical":
            self._add_rec(
                recs,
                "ORDER_FEED_URGENT",
                "high",
                [
                    reason("feed_critical", per_animal=feed_per_animal),
                    reason("feed_shortage_impact", count=ctx.animal_count),
                ]
            )

        # Low feed - order soon
        elif feed_status == "low" and not ctx.feed_delivery_today:
            self._add_rec(
                recs,
                "ORDER_FEED_TODAY",
                "medium",
                [
                    reason("feed_low", per_animal=feed_per_animal),
                    reason("plan_feed_delivery"),
                ]
            )

        # Feed adequate but delivery expected - don't order
        elif feed_status == "adequate" and ctx.feed_delivery_today:
            self._add_not(
                not_recs,
                "ORDER_FEED_TODAY",
                [reason("feed_adequate_delivery_expected")]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Health monitoring and disease alert rule
    # Triggers veterinary checks and disease management protocols
    def _rule_health_monitoring(self, ctx: LivestockStruct, recs, not_recs) -> None:
        health_bucket = ctx.derived["health_bucket"]

        # Disease detected or critical health situation
        if ctx.disease_detected or health_bucket == "critical":
            priority = "high" if ctx.disease_detected else "high"
            self._add_rec(
                recs,
                "VET_CHECK_URGENT",
                priority,
                [
                    reason("disease_detected") if ctx.disease_detected else reason("multiple_sick_animals", count=ctx.sick_count),
                    reason("isolate_sick_animals", count=ctx.sick_count),
                ]
            )

        # Some animals sick but manageable
        elif health_bucket == "warning":
            self._add_rec(
                recs,
                "MONITOR_HEALTH",
                "medium",
                [
                    reason("sick_animals_present", count=ctx.sick_count),
                    reason("daily_health_check"),
                ]
            )

        # Vet not available but needed
        if (ctx.disease_detected or health_bucket == "critical") and not ctx.vet_available:
            self._add_rec(
                recs,
                "CONTACT_EMERGENCY_VET",
                "high",
                [reason("vet_unavailable_emergency")]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Heat stress management rule
    # Manages cooling and stress prevention during hot weather
    def _rule_heat_stress(self, ctx: LivestockStruct, recs, not_recs) -> None:
        temp_stress = ctx.derived["temp_stress"]

        # High temperature - heat stress risk
        if temp_stress or ctx.stress_signs:
            self._add_rec(
                recs,
                "ACTIVATE_COOLING",
                "high",
                [
                    reason("heat_stress_risk", temp=ctx.temperature),
                    reason("increase_water_access"),
                    reason("provide_shade"),
                ]
            )

            # Don't move animals during heat
            self._add_not(
                not_recs,
                "MOVE_ANIMALS",
                [reason("heat_stress_avoid_movement", temp=ctx.temperature)]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Milking schedule optimization rule
    # Adjusts milking schedule based on production and health
    def _rule_milking_schedule(self, ctx: LivestockStruct, recs, not_recs) -> None:
        milk_bucket = ctx.derived["milk_bucket"]
        health_bucket = ctx.derived["health_bucket"]

        # Low milk production - investigate causes
        if milk_bucket == "low":
            self._add_rec(
                recs,
                "CHECK_NUTRITION",
                "medium",
                [
                    reason("milk_yield_low", yield_val=ctx.milk_yield),
                    reason("review_feed_quality"),
                ]
            )

        # Health issues - adjust milking protocol
        if health_bucket != "good":
            self._add_rec(
                recs,
                "SANITIZE_MILKING_EQUIPMENT",
                "high",
                [reason("prevent_disease_spread")]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Water management rule
    # Ensures adequate water supply for dairy cattle
    def _rule_water_management(self, ctx: LivestockStruct, recs, not_recs) -> None:
        # Calculate required water (dairy cows need ~80-100L per day)
        required_water = ctx.animal_count * 80
        water_per_animal = ctx.water_liters / ctx.animal_count if ctx.animal_count > 0 else 0

        # Critical water shortage
        if ctx.water_liters < required_water * 0.5:
            self._add_rec(
                recs,
                "REFILL_WATER_URGENT",
                "high",
                [
                    reason("water_critical", per_animal=round(water_per_animal, 1)),
                    reason("dehydration_risk"),
                ]
            )

        # Low water supply
        elif ctx.water_liters < required_water:
            self._add_rec(
                recs,
                "REFILL_WATER_TODAY",
                "medium",
                [reason("water_low", per_animal=round(water_per_animal, 1))]
            )
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Apply all livestock decision rules
    # Evaluates all rule categories and populates recommendations and not-recommended lists
    def _apply_rules(self, ctx, recs, not_recs):
        # Check feeding needs
        self._rule_feeding(ctx, recs, not_recs)
        # Monitor health and disease
        self._rule_health_monitoring(ctx, recs, not_recs)
        # Manage heat stress
        self._rule_heat_stress(ctx, recs, not_recs)
        # Optimize milking schedule
        self._rule_milking_schedule(ctx, recs, not_recs)
        # Ensure water supply
        self._rule_water_management(ctx, recs, not_recs)
    #----------------------------------------------------------------------------------------------------------------------------
