#===========================================================================================================================
# Backend Data Schemas
# Defines Pydantic models and dataclasses for request/response validation and data access
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from dataclasses import dataclass
from typing import Any, Dict, List
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Model output structure - Contains recommendations, not-recommended actions, and derived buckets
#----------------------------------------------------------------------------------------------------------------------------
@dataclass
class ModelOutput:
    derived: Dict[str, Any]                    # Derived buckets (e.g., moisture_bucket, weather_bucket)
    recommendations: List[Dict[str, Any]]      # List of recommended actions with reasons
    not_recommended: List[Dict[str, Any]]      # List of not-recommended actions with reasons
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Base scenario data wrapper - Generic accessor for all farm types
# Provides flexible nested dictionary access without hardcoded properties
#----------------------------------------------------------------------------------------------------------------------------
@dataclass
class BaseScenarioData:
    decision_inputs: Dict[str, Any]

    #----------------------------------------------------------------------------------------------------------------------------
    # Generic nested accessor for any farm type
    # Usage: data.get('weather', 't_max_c') or data.get('livestock', 'feed_kg')
    #----------------------------------------------------------------------------------------------------------------------------
    def get(self, *keys, default: Any = None) -> Any:
        """
        Get nested value from decision_inputs using dot-notation keys.

        Args:
            *keys: Path to the value (e.g., 'weather', 't_max_c')
            default: Default value if key path not found

        Returns:
            Value at the key path, or default if not found

        Example:
            >>> data.get('weather', 't_max_c', default=0)
            >>> data.get('soil', 'moisture_pct', default=20)
        """
        result = self.decision_inputs
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
                if result is None:
                    return default
            else:
                return default
        return result if result is not None else default
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Wheat-specific scenario data with typed property accessors
# Extends BaseScenarioData with wheat-specific convenience properties
#----------------------------------------------------------------------------------------------------------------------------
@dataclass
class WheatScenarioData(BaseScenarioData):

    #----------------------------------------------------------------------------------------------------------------------------
    # Weather properties - Temperature, rainfall, wind, humidity
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def tmax(self) -> float:
        """Maximum temperature in Celsius"""
        return float(self.get("weather", "t_max_c", default=0))

    @property
    def rain24(self) -> float:
        """Rainfall in last 24 hours (mm)"""
        return float(self.get("weather", "rain_mm_24h", default=0))

    @property
    def rain48(self) -> float:
        """Forecasted rainfall in next 48 hours (mm)"""
        return float(self.get("weather", "forecast_rain_mm_48h", default=0))

    @property
    def wind(self) -> float:
        """Wind speed in meters per second"""
        return float(self.get("weather", "wind_mps", default=0))

    @property
    def humidity(self) -> float:
        """Relative humidity percentage"""
        return float(self.get("weather", "humidity_pct", default=0))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Soil properties
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def soil_moisture(self) -> float:
        """Soil moisture percentage"""
        return float(self.get("soil", "soil_moisture_pct", default=0))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Crop properties
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def stage(self) -> str:
        """Current crop growth stage (e.g., 'tillering', 'flowering')"""
        return str(self.get("crop", "stage_code", default="unknown"))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Constraint properties - Resource availability
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def water_available(self) -> bool:
        """Whether water is available for irrigation"""
        return bool(self.get("constraints", "water_available", default=True))

    @property
    def irrigation_possible_today(self) -> bool:
        """Whether irrigation is operationally possible today"""
        return bool(self.get("constraints", "irrigation_possible_today", default=True))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Observation properties - Pest and disease detection
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def aphids_seen(self) -> bool:
        """Whether aphids have been observed on the crop"""
        return bool(self.get("observations", "pest_aphids_seen", default=False))

    @property
    def rust_seen(self) -> bool:
        """Whether rust disease has been observed on the crop"""
        return bool(self.get("observations", "disease_rust_seen", default=False))
    #----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Livestock-specific scenario data with typed property accessors
# Extends BaseScenarioData with livestock-specific convenience properties
#----------------------------------------------------------------------------------------------------------------------------
@dataclass
class LivestockScenarioData(BaseScenarioData):

    #----------------------------------------------------------------------------------------------------------------------------
    # Environment properties - Temperature and humidity
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def temperature_c(self) -> float:
        """Ambient temperature in Celsius"""
        return float(self.get("environment", "temperature_c", default=20))

    @property
    def humidity_pct(self) -> float:
        """Relative humidity percentage"""
        return float(self.get("environment", "humidity_pct", default=60))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Resource properties - Feed and water availability
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def feed_kg(self) -> float:
        """Available feed in kilograms"""
        return float(self.get("resources", "feed_kg", default=0))

    @property
    def water_liters(self) -> float:
        """Available water in liters"""
        return float(self.get("resources", "water_liters", default=0))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Production properties - Milk yield
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def milk_liters(self) -> float:
        """Current milk production in liters"""
        return float(self.get("production", "milk_liters", default=0))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Livestock properties - Animal count
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def animal_count(self) -> int:
        """Total number of animals"""
        return int(self.get("livestock", "animal_count", default=0))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Health properties - Disease and stress indicators
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def sick_count(self) -> int:
        """Number of sick animals"""
        return int(self.get("health", "sick_count", default=0))

    @property
    def disease_detected(self) -> bool:
        """Whether disease has been detected in the herd"""
        return bool(self.get("health", "disease_detected", default=False))

    @property
    def stress_signs(self) -> bool:
        """Whether stress signs have been observed"""
        return bool(self.get("health", "stress_signs", default=False))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Constraint properties - Resource availability
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def vet_available(self) -> bool:
        """Whether veterinary services are available"""
        return bool(self.get("constraints", "vet_available", default=True))

    @property
    def feed_delivery_expected(self) -> bool:
        """Whether feed delivery is expected today"""
        return bool(self.get("constraints", "feed_delivery_expected", default=False))
    #----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Orchard-specific scenario data with typed property accessors
#----------------------------------------------------------------------------------------------------------------------------
@dataclass
class OrchardScenarioData(BaseScenarioData):

    #----------------------------------------------------------------------------------------------------------------------------
    # Weather properties
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def temperature(self) -> float:
        """Temperature in Celsius"""
        return float(self.get("weather", "temperature_c", default=20))

    @property
    def humidity(self) -> float:
        """Humidity percentage"""
        return float(self.get("weather", "humidity_pct", default=60))

    @property
    def wind(self) -> float:
        """Wind speed in km/h"""
        return float(self.get("weather", "wind_kph", default=0))

    @property
    def rain24(self) -> float:
        """Rainfall in last 24 hours (mm)"""
        return float(self.get("weather", "rain_mm_24h", default=0))

    @property
    def frost_forecast(self) -> bool:
        """Whether frost is forecast"""
        return bool(self.get("weather", "forecast_frost", default=False))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Soil properties
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def soil_moisture(self) -> float:
        """Soil moisture percentage"""
        return float(self.get("soil", "moisture_pct", default=0))

    @property
    def soil_temp(self) -> float:
        """Soil temperature in Celsius"""
        return float(self.get("soil", "soil_temp_c", default=0))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Tree properties
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def stage(self) -> str:
        """Current growth stage"""
        return str(self.get("trees", "stage", default="unknown"))

    @property
    def fruit_load(self) -> str:
        """Fruit load level (none/normal/heavy)"""
        return str(self.get("trees", "fruit_load", default="normal"))

    @property
    def health_status(self) -> str:
        """Tree health status"""
        return str(self.get("trees", "health_status", default="good"))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Pest properties
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def codling_moth(self) -> bool:
        """Whether codling moth detected"""
        return bool(self.get("pests", "codling_moth_detected", default=False))

    @property
    def aphids(self) -> bool:
        """Whether aphids detected"""
        return bool(self.get("pests", "aphids_detected", default=False))

    @property
    def mites(self) -> bool:
        """Whether mites detected"""
        return bool(self.get("pests", "mites_detected", default=False))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Disease properties
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def fire_blight(self) -> bool:
        """Whether fire blight signs present"""
        return bool(self.get("diseases", "fire_blight_signs", default=False))

    @property
    def scab(self) -> bool:
        """Whether scab signs present"""
        return bool(self.get("diseases", "scab_signs", default=False))

    @property
    def mildew(self) -> bool:
        """Whether mildew signs present"""
        return bool(self.get("diseases", "mildew_signs", default=False))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Resource properties
    #----------------------------------------------------------------------------------------------------------------------------
    @property
    def water_available(self) -> bool:
        """Whether water is available"""
        return bool(self.get("resources", "water_available", default=True))

    @property
    def labor_available(self) -> bool:
        """Whether labor is available"""
        return bool(self.get("resources", "labor_available", default=True))
    #----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------------------------------------------
# Greenhouse-specific scenario data
#----------------------------------------------------------------------------------------------------------------------------
@dataclass
class GreenhouseScenarioData(BaseScenarioData):
    @property
    def temperature(self) -> float:
        return float(self.get("environment", "temperature_c", default=20))
    @property
    def humidity(self) -> float:
        return float(self.get("environment", "humidity_pct", default=60))
    @property
    def co2_ppm(self) -> float:
        return float(self.get("environment", "co2_ppm", default=400))
    @property
    def light_hours(self) -> float:
        return float(self.get("environment", "light_hours", default=12))
    @property
    def fan_status(self) -> str:
        return str(self.get("ventilation", "fan_status", default="off"))
    @property
    def vent_open_pct(self) -> float:
        return float(self.get("ventilation", "vent_open_pct", default=0))
    @property
    def water_available(self) -> bool:
        return bool(self.get("irrigation", "water_available", default=True))
    @property
    def soil_moisture(self) -> float:
        return float(self.get("irrigation", "soil_moisture_pct", default=0))
    @property
    def last_watered_hours(self) -> float:
        return float(self.get("irrigation", "last_watered_hours", default=24))
    @property
    def stage(self) -> str:
        return str(self.get("crops", "stage", default="unknown"))
    @property
    def health(self) -> str:
        return str(self.get("crops", "health", default="good"))
    @property
    def whiteflies(self) -> bool:
        return bool(self.get("pests", "whiteflies", default=False))
    @property
    def thrips(self) -> bool:
        return bool(self.get("pests", "thrips", default=False))
    @property
    def aphids(self) -> bool:
        return bool(self.get("pests", "aphids", default=False))
    @property
    def fungal_signs(self) -> bool:
        return bool(self.get("diseases", "fungal_signs", default=False))
    @property
    def bacterial_signs(self) -> bool:
        return bool(self.get("diseases", "bacterial_signs", default=False))
    @property
    def virus_signs(self) -> bool:
        return bool(self.get("diseases", "virus_signs", default=False))
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Mixed farm scenario data
#----------------------------------------------------------------------------------------------------------------------------
@dataclass
class MixedScenarioData(BaseScenarioData):
    @property
    def soil_moisture(self) -> float:
        return float(self.get("crops", "soil_moisture_pct", default=0))
    @property
    def crop_stage(self) -> str:
        return str(self.get("crops", "stage", default="unknown"))
    @property
    def crop_health(self) -> str:
        return str(self.get("crops", "health", default="good"))
    @property
    def pest_pressure(self) -> str:
        return str(self.get("crops", "pest_pressure", default="low"))
    @property
    def animal_count(self) -> int:
        return int(self.get("livestock", "animal_count", default=0))
    @property
    def feed_kg(self) -> float:
        return float(self.get("livestock", "feed_kg", default=0))
    @property
    def water_liters(self) -> float:
        return float(self.get("livestock", "water_liters", default=0))
    @property
    def sick_count(self) -> int:
        return int(self.get("livestock", "sick_count", default=0))
    @property
    def labor_hours(self) -> float:
        return float(self.get("resources", "labor_hours", default=8))
    @property
    def water_available(self) -> bool:
        return bool(self.get("resources", "water_available", default=True))
    @property
    def budget_available(self) -> bool:
        return bool(self.get("resources", "budget_available", default=True))
    @property
    def temperature(self) -> float:
        return float(self.get("weather", "temperature_c", default=20))
    @property
    def rain24(self) -> float:
        return float(self.get("weather", "rain_mm_24h", default=0))
    @property
    def rain48_forecast(self) -> float:
        return float(self.get("weather", "forecast_rain_48h", default=0))
#----------------------------------------------------------------------------------------------------------------------------
