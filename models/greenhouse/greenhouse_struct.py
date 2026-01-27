#===========================================================================================================================
# Greenhouse Context Structure
#===========================================================================================================================

from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class GreenhouseStruct:
    # Environment
    temperature: float
    humidity: float
    co2_ppm: float
    light_hours: float

    # Ventilation
    fan_status: str
    vent_open_pct: float

    # Irrigation
    water_available: bool
    soil_moisture: float
    last_watered_hours: float

    # Crops
    stage: str
    health: str

    # Pests
    whiteflies: bool
    thrips: bool
    aphids: bool

    # Diseases
    fungal_signs: bool
    bacterial_signs: bool
    virus_signs: bool

    # Derived buckets
    derived: Dict[str, Any]
