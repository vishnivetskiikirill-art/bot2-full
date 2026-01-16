window.I18N = {
  en: {
    title: "Catalog",
    language: "Language",
    city: "City",
    district: "District",
    type: "Type",
    maxPrice: "Max price (€)",
    reset: "Reset",
    show: "Show",
    listings: "Listings",
    any: "—",
    type_apartment: "Apartment",
    type_house: "House",
  },
  ru: {
    title: "Каталог",
    language: "Язык",
    city: "Город",
    district: "Район",
    type: "Тип",
    maxPrice: "Макс. цена (€)",
    reset: "Сброс",
    show: "Показать",
    listings: "Объявления",
    any: "—",
    type_apartment: "Квартира",
    type_house: "Дом",
  },
  bg: {
    title: "Каталог",
    language: "Език",
    city: "Град",
    district: "Район",
    type: "Тип",
    maxPrice: "Макс. цена (€)",
    reset: "Нулиране",
    show: "Покажи",
    listings: "Обяви",
    any: "—",
    type_apartment: "Апартамент",
    type_house: "Къща",
  },
  he: {
    title: "קטלוג",
    language: "שפה",
    city: "עיר",
    district: "אזור",
    type: "סוג",
    maxPrice: "מחיר מקס' (€)",
    reset: "איפוס",
    show: "הצג",
    listings: "מודעות",
    any: "—",
    type_apartment: "דירה",
    type_house: "בית",
  },
};

window.normalizeTypeKey = function(type) {
  const t = String(type || "").toLowerCase();
  if (t.includes("apart")) return "type_apartment";
  if (t.includes("house")) return "type_house";
  return null;
};

window.isRTL = function(lang){
  return lang === "he";
};
