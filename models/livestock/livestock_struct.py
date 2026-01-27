#===========================================================================================================================
# Livestock Context Data Structure
# Immutable dataclass for dairy cattle management decision rules
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from dataclasses import dataclass
from typing import Any, Dict
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Livestock context structure - Immutable snapshot for dairy cattle decisions
#----------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class LivestockStruct:
    # Environmental inputs
    temperature: float       # Current temperature (Celsius)
    humidity: float          # Relative humidity (percentage)

    # Resource inputs
    feed_kg: float           # Available feed in kilograms
    water_liters: float      # Available water in liters

    # Production inputs
    milk_yield: float        # Daily milk yield in liters
    animal_count: int        # Total number of animals

    # Health observations
    sick_count: int          # Number of sick animals
    disease_detected: bool   # Whether disease has been observed
    stress_signs: bool       # Signs of heat stress or distress

    # Constraints
    vet_available: bool      # Veterinary service availability
    feed_delivery_today: bool  # Whether feed delivery expected

    # Derived buckets (computed from raw inputs)
    derived: Dict[str, Any]  # Contains: feed_status, health_bucket, temp_stress, milk_bucket
#----------------------------------------------------------------------------------------------------------------------------
