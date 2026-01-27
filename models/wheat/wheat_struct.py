#===========================================================================================================================
# Wheat Context Data Structure
# Immutable dataclass holding all sensor data, constraints, and derived buckets for wheat rule evaluation
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from dataclasses import dataclass
from typing import Any, Dict
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Wheat context structure - Immutable snapshot of all data needed for decision rules
#----------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class WheatStruct:
    # Weather inputs
    tmax: float              # Maximum temperature in Celsius
    rain24: float            # Rainfall in last 24 hours (mm)
    rain48: float            # Forecasted rainfall in next 48 hours (mm)
    wind: float              # Wind speed (meters per second)
    humidity: float          # Relative humidity (percentage)

    # Soil inputs
    sm: float                # Soil moisture (percentage)

    # Crop inputs
    stage: str               # Crop growth stage (e.g., 'tillering', 'flowering')

    # Constraint inputs
    water_available: bool            # Whether water is available for irrigation
    irrigation_possible: bool        # Whether irrigation is operationally possible today

    # Observation inputs
    aphids: bool             # Whether aphids have been observed on the crop
    rust: bool               # Whether rust disease has been observed on the crop

    # Derived buckets (computed from raw inputs for simplified rule evaluation)
    derived: Dict[str, Any]  # Contains: moisture_bucket, weather_bucket, wet_bucket, rain_coming_48h
#----------------------------------------------------------------------------------------------------------------------------
