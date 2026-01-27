#===========================================================================================================================
# Mixed Farm Context Structure
#===========================================================================================================================

from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class MixedStruct:
    # Crops
    soil_moisture: float
    crop_stage: str
    crop_health: str
    pest_pressure: str

    # Livestock
    animal_count: int
    feed_kg: float
    water_liters: float
    sick_count: int

    # Resources
    labor_hours: float
    water_available: bool
    budget_available: bool

    # Weather
    temperature: float
    rain24: float
    rain48_forecast: float

    # Derived buckets
    derived: Dict[str, Any]
