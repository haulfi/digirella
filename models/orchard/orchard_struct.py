#===========================================================================================================================
# Orchard Context Structure
# Immutable dataclass containing all necessary data for orchard decision rules
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from dataclasses import dataclass
from typing import Any, Dict
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Orchard context dataclass - Contains all sensor data and derived buckets
# Used as input to all orchard rule functions
#----------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class OrchardStruct:
    # Weather data
    temperature: float
    humidity: float
    wind: float
    rain24: float
    frost_forecast: bool

    # Soil data
    soil_moisture: float
    soil_temp: float

    # Tree data
    stage: str
    fruit_load: str
    health_status: str

    # Pest data
    codling_moth: bool
    aphids: bool
    mites: bool

    # Disease data
    fire_blight: bool
    scab: bool
    mildew: bool

    # Resources
    water_available: bool
    labor_available: bool

    # Derived buckets from _derive() method
    derived: Dict[str, Any]
#----------------------------------------------------------------------------------------------------------------------------
