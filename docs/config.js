//===========================================================================================================================
// DigiRella Frontend Configuration
// Contains all configuration constants, labels, and default settings
//===========================================================================================================================

//----------------------------------------------------------------------------------------------------------------------------
// Farm Type Labels - Azerbaijani translations
//----------------------------------------------------------------------------------------------------------------------------
const FARM_LABELS = {
  wheat: "taxıl",
  greenhouse: "istixana",
  livestock: "heyvandarlıq",
  mixed: "qarışıq",
  orchard: "bağ",
};

//----------------------------------------------------------------------------------------------------------------------------
// Action Code Labels - Human-readable descriptions for recommendation codes
//----------------------------------------------------------------------------------------------------------------------------
const ACTION_LABELS = {
  // Wheat actions
  IRRIGATE_TODAY: "Bu gün sahəni suvar!",
  IRRIGATE_REDUCED_OR_DELAY: "Suvarmanı azalt və yaxud gecikdir",
  FERTILIZE_TODAY: "Bu gün sahəni gübrələ!",
  SCOUT_APHIDS: "Yarpaqbiti müşahidəsi var",
  RUST_RISK_ALERT: "Pas riski xəbərdarlığı",
  AVOID_SPRAY_MIDDAY: "Günortadan sonra səpin etmək olmaz!",
  MONITOR_IRRIGATION : "Suvarmağı planlaşdır",

  // Livestock actions
  ORDER_FEED_URGENT: "Təcili yem sifariş et!",
  ORDER_FEED_TODAY: "Bu gün yem sifariş et",
  VET_CHECK_URGENT: "Təcili veterinar yoxlaması!",
  MONITOR_HEALTH: "Sağlamlığı izlə",
  CONTACT_EMERGENCY_VET: "Təcili veterinarla əlaqə saxla!",
  ACTIVATE_COOLING: "Soyutma sistemini aktivləşdir!",
  MOVE_ANIMALS: "Heyvanları köçür",
  CHECK_NUTRITION: "Qidalanmanı yoxla",
  SANITIZE_MILKING_EQUIPMENT: "Sağım avadanlığını dezinfeksiya et!",
  REFILL_WATER_URGENT: "Təcili su doldur!",
  REFILL_WATER_TODAY: "Bu gün su doldur",

  // Orchard actions
  IRRIGATE_ORCHARD: "Bağı suvar",
  ACTIVATE_FROST_PROTECTION: "Şaxta qorumasını aktivləşdir!",
  TREAT_CODLING_MOTH: "Alma güvəsinə qarşı müalicə et!",
  MONITOR_APHIDS: "Yarpaq bitlərini izlə",
  TREAT_MITES: "Gənələrə qarşı müalicə et",
  TREAT_FIRE_BLIGHT: "Yanğın yanığını müalicə et!",
  APPLY_FUNGICIDE_SCAB: "Qabıq xəstəliyinə qarşı fungisid tətbiq et!",
  TREAT_MILDEW: "Küfə qarşı müalicə et",
  MONITOR_DISEASE: "Xəstəlikləri izlə",
  THIN_FRUIT: "Meyvələri seyrəlt",
  FERTILIZE_ORCHARD: "Bağı gübrələ",
  ARRANGE_HARVEST_LABOR: "Yığım işçiləri təşkil et!",
  BEGIN_HARVEST: "Yığıma başla!",
  SECURE_ORCHARD: "Bağı qoruyun - fırtına hazırlığı!",
  SPRAY_PESTICIDES: "Pestisid səpin",

  // Greenhouse actions
  ACTIVATE_HEATING: "İsitmə sistemini aktivləşdir!",
  INCREASE_VENTILATION: "Ventilyasiyanı artır!",
  INCREASE_HUMIDITY: "Rütubəti artır",
  IMPROVE_VENTILATION: "Ventilyasiyanı yaxşılaşdır",
  WATER_CROPS: "Bitkiləri suvar",
  TREAT_WHITEFLIES: "Ağ milçəklərə qarşı müalicə et!",
  TREAT_THRIPS: "Tripsə qarşı müalicə et!",
  TREAT_APHIDS: "Yarpaq bitlərinə qarşı müalicə et",
  APPLY_FUNGICIDE: "Fungisid tətbiq et!",
  TREAT_BACTERIAL_DISEASE: "Bakterial xəstəliyə qarşı müalicə et!",
  REMOVE_INFECTED_PLANTS: "Yoluxmuş bitkiləri çıxar!",
  TRANSPLANT_SEEDLINGS: "Şitilləri köçür",
  CHECK_NUTRIENT_LEVELS: "Qida səviyyələrini yoxla",

  // Mixed farm actions
  IRRIGATE_CROPS_URGENT: "Təcili bitkiləri suvar!",
  IRRIGATE_CROPS: "Bitkiləri suvar",
  FEED_ANIMALS_URGENT: "Təcili heyvanları yemləyin!",
  ORDER_FEED_MIXED: "Yem sifariş et",
  WATER_ANIMALS_URGENT: "Təcili heyvanlara su verin!",
  CHECK_SICK_ANIMALS: "Xəstə heyvanları yoxla",
  TREAT_CROP_PESTS: "Bitki zərərvericilərini müalicə et",
  MONITOR_PEST_LEVELS: "Zərərverici səviyyələrini izlə",
  HARVEST_CROPS: "Məhsulu yığ!",
  PRIORITIZE_TASKS: "Tapşırıqları prioritetləşdir!",
  SECURE_EMERGENCY_FUNDS: "Təcili maliyyə təmin et!",
  DELAY_IRRIGATION_RAIN: "Yağışa görə suvarmanı gecikdir",
  APPLY_FERTILIZER: "Gübrə tətbiq et"
};

//----------------------------------------------------------------------------------------------------------------------------
// Default API Configuration
//----------------------------------------------------------------------------------------------------------------------------
const DEFAULT_API_BASE = "http://127.0.0.1:8000";
const DEFAULT_LANGUAGE = "az";

//----------------------------------------------------------------------------------------------------------------------------
// Helper function to get farm label by key
//----------------------------------------------------------------------------------------------------------------------------
function farmLabel(key) {
  return FARM_LABELS[key] || key;
}

//----------------------------------------------------------------------------------------------------------------------------
// Helper function to get action label by code
//----------------------------------------------------------------------------------------------------------------------------
function actionLabel(code) {
  return ACTION_LABELS[code] || code;
}
