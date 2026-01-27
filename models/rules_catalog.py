#===========================================================================================================================
# Rules Catalog and Localization System
# Provides multi-language templates and formatters for model output
# Organized by farm type for easy extensibility
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from __future__ import annotations
from typing import Any, Dict, Iterable, List
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Type aliases for better code readability
#----------------------------------------------------------------------------------------------------------------------------
Reason = Dict[str, Any]
Action = Dict[str, Any]
ModelOutput = Dict[str, Any]
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Language templates organized by farm type
# Structure: {farm_type: {language: {reason_key: template}}}
# Makes it easy to add new farm types without touching existing templates
#----------------------------------------------------------------------------------------------------------------------------
_TEMPLATES = {
    "wheat": {
        "az": {
            # Irrigation reasons
            "irrigation_not_possible": "Bu gün suvarma mümkün deyil (mümkün={irrigation_possible}, su mövcudluğu={water_available}).",
            "soil_moisture_low": "Torpaq rütubəti aşağıdır ({sm}%).",
            "dry_conditions": "Quru şərait var (son 24 saat yağış={rain24} mm, rütubət={humidity}%).",
            "no_rain_expected_48h": "Növbəti 48 saatda əhəmiyyətli yağış gözlənilmir.",
            "soil_moisture_low_rain_expected": "Torpaq rütubəti aşağıdır ({sm}%), amma 48 saatda yağış gözlənilir ({rain48} mm).",
            "delay_or_reduce_irrigation": "Suva qənaət üçün suvarmanı gecikdirin və ya azaldın.",
            "wet_conditions": "Şərait rütubətlidir (rütubət={humidity}%, son 24 saat yağış={rain24} mm).",
            "soil_moisture_level": "Torpaq rütubəti {moisture_bucket} səviyyədədir ({sm}%).",

            # Fertilization reasons
            "stage_is": "Mərhələ: {stage}.",
            "soil_moisture_adequate": "Torpaq rütubəti kafi səviyyədədir ({sm}%).",
            "weather_suitable": "Hava şəraiti uyğundur (maks. temp={tmax} C, rütubət={humidity}%).",
            "high_rain_humidity_runoff": "Yüksək yağış və rütubət gübrənin axıb getmə riskini artırır.",
            "rain_humidity_values": "Son 24 saat yağış={rain24} mm, rütubət={humidity}%.",

            # Pest and disease reasons
            "aphids_observed": "Yarpaq biti müşahidə olunub: müşahidə edin və həddə görə tədbir görün.",
            "rust_signs_observed": "Pas xəstəliyinin əlamətləri müşahidə olunub.",
            "rust_risk_weather": "Yüksək rütubət və yağış pas riskini artırır.",
            "humidity_rain_values": "Rütubət={humidity}%, son 24 saat yağış={rain24} mm.",

            # Spray safety reasons
            "wind_heat_reduce_spray": "Külək/isti hava səpinin keyfiyyətini azalda bilər (külək={wind} m/s, maks. temp={tmax} C).",
            "prefer_morning_evening": "Əgər səpin lazımdırsa, səhər erkən və ya axşam edin.",
        },
    },
    "livestock": {
        "az": {
            # Feeding management
            "feed_critical": "Yem kritik səviyyədədir (heyvan başına {per_animal} kq).",
            "feed_shortage_impact": "Yem çatışmazlığı {count} heyvan üçün təhlükəlidir.",
            "feed_low": "Yem az səviyyədədir (heyvan başına {per_animal} kq).",
            "plan_feed_delivery": "Yem çatdırılmasını planlaşdırın.",
            "feed_adequate_delivery_expected": "Yem kafi səviyyədədir və çatdırılma gözlənilir.",

            # Health monitoring
            "disease_detected": "Xəstəlik aşkar edilib - təcili veterinar müdaxiləsi.",
            "multiple_sick_animals": "{count} heyvan xəstədir - təcili yoxlama.",
            "isolate_sick_animals": "Xəstə heyvanları ({count} ədəd) təcrid edin.",
            "sick_animals_present": "{count} xəstə heyvan var.",
            "daily_health_check": "Gündəlik sağlamlıq yoxlaması aparın.",
            "vet_unavailable_emergency": "Veterinar əlçatmazdır - təcili əlaqə saxlayın.",
            "prevent_disease_spread": "Xəstəliyin yayılmasının qarşısını alın.",

            # Heat stress
            "heat_stress_risk": "İsti stress riski (temp={temp}°C).",
            "increase_water_access": "Su çıxışını artırın.",
            "provide_shade": "Kölgə təmin edin.",
            "heat_stress_avoid_movement": "İsti vaxtı heyvanları hərəkət etdirməyin (temp={temp}°C).",

            # Milking and production
            "milk_yield_low": "Süd məhsuldarlığı aşağıdır ({yield_val} litr).",
            "review_feed_quality": "Yem keyfiyyətini yoxlayın.",

            # Water management
            "water_critical": "Su kritik səviyyədədir (heyvan başına {per_animal} litr).",
            "dehydration_risk": "Susuzlaşma riski var.",
            "water_low": "Su az səviyyədədir (heyvan başına {per_animal} litr).",
        }
    },
    "orchard": {
        "az": {
            # Irrigation
            "no_water_available": "Su mövcud deyil.",
            "soil_moisture_critical": "Torpaq rütubəti kritik səviyyədədir ({sm}%).",
            "critical_growth_stage": "Kritik böyümə mərhələsi: {stage}.",
            "soil_moisture_low": "Torpaq rütubəti aşağıdır ({sm}%).",
            "soil_too_wet": "Torpaq çox rütubətlidir (rütubət={sm}%, yağış={rain24}mm).",

            # Frost protection
            "frost_warning": "Şaxta xəbərdarlığı (temp={temp}°C).",
            "frost_sensitive_stage": "Şaxtaya həssas mərhələ: {stage}.",
            "frost_protection_methods": "Şaxta qoruma tədbirləri tətbiq edin (su səpin, qızdırıcılar).",

            # Pest management
            "codling_moth_detected": "Alma güvəsi aşkar edilib.",
            "fruit_damage_risk": "Meyvə zərər riski yüksəkdir.",
            "aphids_present": "Yarpaq bitləri mövcuddur - izləyin.",
            "mites_detected": "Gənələr aşkar edilib.",

            # Disease management
            "fire_blight_detected": "Yanğın yanığı aşkar edilib!",
            "prune_infected_branches": "Yoluxmuş budaqları kəsin və məhv edin.",
            "scab_signs_present": "Qabıq xəstəliyi əlamətləri var.",
            "mildew_detected": "Küf aşkar edilib.",
            "wet_conditions_disease_risk": "Rütubətli şərait xəstəlik riskini artırır (rütubət={humidity}%, yağış={rain24}mm).",

            # Fruit management
            "heavy_fruit_load": "Ağır meyvə yükü - seyrəltmə lazımdır.",
            "improve_fruit_quality": "Meyvə keyfiyyətini artırmaq üçün seyrəldin.",

            # Fertilization
            "spring_growth_stage": "Bahar böyüməsi mərhələsi - gübrələmə vaxtıdır.",
            "soil_moisture_adequate": "Torpaq rütubəti kafi səviyyədədir ({sm}%).",
            "too_wet_for_fertilizer": "Gübrə üçün torpaq çox rütubətlidir.",

            # Harvest
            "harvest_ready_no_labor": "Yığım hazırdır, lakin işçi qüvvəsi yoxdur.",
            "fruit_ready_harvest": "Meyvələr yığıma hazırdır.",

            # Storm preparation
            "high_wind_warning": "Güclü külək xəbərdarlığı ({wind} km/saat).",
            "protect_trees_fruit": "Ağacları və meyvələri qoruyun.",
            "high_wind_no_spray": "Güclü küləkdə ({wind} km/saat) səpin etməyin.",
        }
    },
    "greenhouse": {
        "az": {
            # Temperature
            "temperature_too_high": "Temperatur çox yüksəkdir ({temp}°C).",
            "increase_ventilation": "Ventilyasiyanı artırın və kölgələyin.",
            "temperature_too_low": "Temperatur çox aşağıdır ({temp}°C).",
            "close_vents": "Havalandırmaları bağlayın və istiliyi artırın.",

            # Humidity
            "humidity_too_high": "Rütubət çox yüksəkdir ({humidity}%).",
            "disease_risk_high_humidity": "Yüksək rütubət xəstəlik riskini artırır.",
            "humidity_too_low": "Rütubət çox aşağıdır ({humidity}%).",

            # Ventilation & CO2
            "co2_too_high": "CO2 səviyyəsi çox yüksəkdir ({co2} ppm).",
            "air_quality_poor": "Hava keyfiyyəti pisdir - ventilyasiyanı yaxşılaşdırın.",

            # Irrigation
            "no_water_available": "Su mövcud deyil.",
            "soil_moisture_low": "Torpaq rütubəti aşağıdır ({sm}%).",
            "last_watered": "Son suvarma: {hours} saat əvvəl.",

            # Pests
            "whiteflies_detected": "Ağ milçəklər aşkar edilib.",
            "thrips_detected": "Trips aşkar edilib.",
            "aphids_detected": "Yarpaq bitləri aşkar edilib.",

            # Diseases
            "fungal_infection_detected": "Göbələk infeksiyası aşkar edilib!",
            "reduce_humidity_disease": "Rütubəti azaldın və havalandırmanı artırın.",
            "bacterial_infection_detected": "Bakterial infeksiya aşkar edilib!",
            "virus_detected_remove": "Virus aşkar edilib - yoluxmuş bitkiləri çıxarın.",

            # Crop management
            "seedlings_ready": "Şitillər köçürmə üçün hazırdır.",
            "crop_health_poor": "Bitki sağlamlığı pis - qida maddələrini yoxlayın.",
        }
    },
    "mixed": {
        "az": {
            # Crops
            "no_water_mixed": "Su mövcud deyil - bitkiləri suvarma mümkün deyil.",
            "crop_critical_stage": "Kritik mərhələ: {stage} - təcili suvarma lazım.",
            "crop_needs_irrigation": "Bitkilər suvarma tələb edir (torpaq rütubəti={sm}%).",

            # Livestock feeding
            "feed_critical_mixed": "Yem kritik səviyyədədir (heyvan başına {per_animal} kq).",
            "animal_welfare_risk": "{count} heyvan üçün yem çatışmazlığı riski.",
            "feed_low_mixed": "Yem az səviyyədədir (heyvan başına {per_animal} kq).",

            # Livestock watering
            "water_critical_animals": "Heyvanlar üçün su kritik səviyyədədir (başına {per_animal} litr).",
            "dehydration_risk": "Susuzlaşma riski.",

            # Health
            "sick_animals_mixed": "{count} xəstə heyvan var.",
            "isolate_if_needed": "Lazım gələrsə təcrid edin.",

            # Pests
            "high_pest_pressure": "Yüksək zərərverici təzyiqi - müdaxilə lazımdır.",
            "moderate_pest_pressure": "Orta zərərverici təzyiqi - izləyin.",

            # Harvest
            "crops_ready_harvest": "Məhsul yığıma hazırdır.",
            "timely_harvest_quality": "Vaxtında yığım keyfiyyəti təmin edir.",

            # Resource allocation
            "limited_labor": "Məhdud işçi qüvvəsi ({hours} saat).",
            "multiple_operations_needed": "Çoxlu əməliyyat tələb olunur.",
            "prioritize_animals_first": "Əvvəlcə heyvanların ehtiyaclarına prioritet verin.",
            "budget_constraint_critical": "Büdcə məhdudiyyəti kritik vəziyyətdə - təcili maliyyə lazımdır.",

            # Weather planning
            "rain_forecast_mixed": "48 saata yağış gözlənilir ({rain} mm).",
            "save_water_resources": "Su resurslarını qənaət edin.",
            "heavy_rain_runoff": "Güclü yağış ({rain} mm) - gübrə axıb gedə bilər.",
        }
    },
}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Boolean value translations for different languages
#----------------------------------------------------------------------------------------------------------------------------
_BOOL_STRINGS = {
    "az": {True: "bəli", False: "xeyr"},
}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Value translations for bucket/category names
# Translates technical terms to human-readable local language
#----------------------------------------------------------------------------------------------------------------------------
_VALUE_STRINGS = {
    "az": {
        # Moisture/wetness levels
        "low": "aşağı",
        "adequate": "kafi",
        "medium": "orta",
        "high": "yüksək",

        # Temperature levels
        "hot": "çox isti",
        "warm": "isti",
        "mild": "mülayim",

        # Crop stages
        "tillering": "kolların çoxalması",
    },
}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Create a structured reason object with key and parameters
#----------------------------------------------------------------------------------------------------------------------------
def reason(key: str, **params: Any) -> Reason:
    """
    Creates a structured reason dictionary for localization.

    Args:
        key: Template key for the reason message
        **params: Parameters to fill into the template

    Returns:
        Dictionary with 'key' and 'params' fields
    """
    return {"key": key, "params": params}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Normalize parameter values by translating booleans and categorical values
#----------------------------------------------------------------------------------------------------------------------------
def _normalize_params(params: Dict[str, Any], language: str = "az") -> Dict[str, Any]:
    """
    Translates parameter values to localized strings.

    Args:
        params: Dictionary of parameter names and values
        language: Target language code (default: 'az')

    Returns:
        Dictionary with translated parameter values
    """
    out: Dict[str, Any] = {}
    value_map = _VALUE_STRINGS.get(language, {})
    bool_map = _BOOL_STRINGS.get(language, {})

    for name, value in params.items():
        # Translate boolean values
        if isinstance(value, bool) and bool_map:
            out[name] = bool_map[value]
            continue
        # Translate categorical string values
        if isinstance(value, str):
            out[name] = value_map.get(value, value)
            continue
        # Keep numeric values as-is
        out[name] = value
    return out
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Format a single reason using farm-specific template and parameters
#----------------------------------------------------------------------------------------------------------------------------
def format_reason(reason_item: Any, farm_type: str = "wheat", language: str = "az") -> str:
    """
    Formats a structured reason into a localized human-readable string.

    Args:
        reason_item: Reason dictionary with 'key' and 'params', or raw string
        farm_type: Farm type for template lookup (default: 'wheat')
        language: Target language code (default: 'az')

    Returns:
        Formatted localized string
    """
    # Handle raw strings
    if isinstance(reason_item, str):
        return reason_item
    if not isinstance(reason_item, dict):
        return str(reason_item)

    key = reason_item.get("key", "")
    params = reason_item.get("params", {}) or {}

    # Get template for the farm type and language
    farm_templates = _TEMPLATES.get(farm_type, {})
    templates = farm_templates.get(language) or farm_templates.get("az") or {}

    # Fallback to wheat templates if farm type not found
    if not templates:
        templates = _TEMPLATES.get("wheat", {}).get(language, {})

    template = templates.get(key, key)

    # Normalize parameters and fill template
    normalized = _normalize_params(params, language)
    try:
        return template.format(**normalized)
    except (KeyError, ValueError):
        return template
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Format a list of reasons for a specific farm type
#----------------------------------------------------------------------------------------------------------------------------
def format_reasons(reasons: Iterable[Any], farm_type: str = "wheat", language: str = "az") -> List[str]:
    """
    Formats multiple reasons into localized strings.

    Args:
        reasons: List of reason dictionaries or strings
        farm_type: Farm type for template lookup (default: 'wheat')
        language: Target language code (default: 'az')

    Returns:
        List of formatted localized strings
    """
    return [format_reason(reason_item, farm_type, language) for reason_item in reasons]
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Format actions with localized reasons for a specific farm type
#----------------------------------------------------------------------------------------------------------------------------
def format_actions(actions: Iterable[Action], farm_type: str = "wheat", language: str = "az") -> List[Action]:
    """
    Formats actions by localizing their reasons while preserving structure.

    Args:
        actions: List of action dictionaries with 'code', 'priority', and 'reasons'
        farm_type: Farm type for template lookup (default: 'wheat')
        language: Target language code (default: 'az')

    Returns:
        List of actions with both localized reasons and original structured reasons
    """
    formatted: List[Action] = []
    for action in actions:
        reasons_structured = action.get("reasons", [])
        localized = format_reasons(reasons_structured, farm_type, language)

        # Create new action with both formats
        new_action = dict(action)
        new_action["reasons"] = localized                      # Human-readable localized strings
        new_action["reasons_structured"] = reasons_structured  # Original structured format for LLM/chat

        # Translate priority if present
        priority = action.get("priority")
        if priority is not None:
            new_action["priority"] = _normalize_params({"priority": priority}, language).get("priority", priority)

        formatted.append(new_action)
    return formatted
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Generic formatter factory - Creates farm-specific formatters
# Use this to create formatters for any farm type
#----------------------------------------------------------------------------------------------------------------------------
def create_formatter(farm_type: str):
    """
    Factory function to create a farm-specific formatter.

    Args:
        farm_type: Type of farm (e.g., 'wheat', 'livestock', 'orchard')

    Returns:
        Formatter function for the specified farm type

    Example:
        >>> format_livestock = create_formatter('livestock')
        >>> output = format_livestock(model_output, 'az')
    """
    def formatter(output: ModelOutput, language: str = "az") -> ModelOutput:
        formatted = dict(output)
        formatted["recommendations"] = format_actions(output.get("recommendations", []), farm_type, language)
        formatted["not_recommended"] = format_actions(output.get("not_recommended", []), farm_type, language)
        return formatted
    return formatter
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Wheat model output formatter - Uses generic formatter with 'wheat' farm type
#----------------------------------------------------------------------------------------------------------------------------
format_wheat_model_output = create_formatter("wheat")
#----------------------------------------------------------------------------------------------------------------------------
