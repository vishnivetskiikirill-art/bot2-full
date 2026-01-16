window.I18N = {
  en: {
    catalog: "Catalog",
    language: "Language",
    city: "City",
    district: "District",
    type: "Type",
    maxPrice: "Max price (€)",
    reset: "Reset",
    show: "Show",
    listings: "Listings",
    back: "Back",
    loading: "Loading...",
    notFound: "Not found",
    any: "—",
    apartment: "Apartment",
    house: "House",
  },
  ru: {
    catalog: "Каталог",
    language: "Язык",
    city: "Город",
    district: "Район",
    type: "Тип",
    maxPrice: "Макс. цена (€)",
    reset: "Сброс",
    show: "Показать",
    listings: "Объявления",
    back: "Назад",
    loading: "Загрузка...",
    notFound: "Не найдено",
    any: "—",
    apartment: "Квартира",
    house: "Дом",
  },
  bg: {
    catalog: "Каталог",
    language: "Език",
    city: "Град",
    district: "Район",
    type: "Тип",
    maxPrice: "Макс. цена (€)",
    reset: "Нулиране",
    show: "Покажи",
    listings: "Обяви",
    back: "Назад",
    loading: "Зареждане...",
    notFound: "Няма резултати",
    any: "—",
    apartment: "Апартамент",
    house: "Къща",
  },
  he: {
    catalog: "קטלוג",
    language: "שפה",
    city: "עיר",
    district: "אזור",
    type: "סוג",
    maxPrice: "מחיר מקס׳ (€)",
    reset: "איפוס",
    show: "הצג",
    listings: "מודעות",
    back: "חזרה",
    loading: "טוען...",
    notFound: "לא נמצא",
    any: "—",
    apartment: "דירה",
    house: "בית",
  },
};

window.isRTL = (lang) => lang === "he";

window.normalizeTypeKey = (raw) => {
  if (!raw) return null;
  const v = String(raw).trim().toLowerCase();
  if (v === "apartment" || v === "flat") return "apartment";
  if (v === "house" || v === "villa") return "house";
  return null;
};
