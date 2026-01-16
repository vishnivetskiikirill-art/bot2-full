const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

const API = {
  status: "/api/status",
  meta: "/api/meta",
  listings: "/api/listings",
};

const UI = {
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
    any: "—",
    types: { Apartment: "Apartment", House: "House" },
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
    any: "—",
    types: { Apartment: "Квартира", House: "Дом" },
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
    any: "—",
    types: { Apartment: "Апартамент", House: "Къща" },
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
    any: "—",
    types: { Apartment: "דירה", House: "בית" },
  },
};

function detectLang() {
  let lang = localStorage.getItem("lang");
  if (!lang) {
    const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code || "en";
    lang = ["ru", "en", "bg", "he"].includes(tgLang) ? tgLang : "en";
    localStorage.setItem("lang", lang);
  }
  return lang;
}

let LANG = detectLang();
const T = () => UI[LANG] || UI.en;

// элементы
const langSelect = document.getElementById("langSelect");
const cityEl = document.getElementById("city");
const districtEl = document.getElementById("district");
const typeEl = document.getElementById("type");
const maxPriceEl = document.getElementById("maxPrice");
const btnReset = document.getElementById("btnReset");
const btnShow = document.getElementById("btnShow");
const listingsCountEl = document.getElementById("listingsCount");
const listingsEl = document.getElementById("listings");

// заголовки/лейблы
const titleCatalog = document.getElementById("titleCatalog");
const labelLanguage = document.getElementById("labelLanguage");
const lblCity = document.getElementById("lblCity");
const lblDistrict = document.getElementById("lblDistrict");
const lblType = document.getElementById("lblType");
const lblMaxPrice = document.getElementById("lblMaxPrice");
const lblListings = document.getElementById("lblListings");

async function apiGet(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function fillSelect(selectEl, items) {
  selectEl.innerHTML = "";
  const optEmpty = document.createElement("option");
  optEmpty.value = "";
  optEmpty.textContent = T().any;
  selectEl.appendChild(optEmpty);

  for (const v of items) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    selectEl.appendChild(opt);
  }
}

function applyLangUI() {
  const t = T();

  // RTL для иврита
  document.documentElement.dir = (LANG === "he") ? "rtl" : "ltr";

  titleCatalog.textContent = t.catalog;
  labelLanguage.textContent = t.language;
  lblCity.textContent = t.city;
  lblDistrict.textContent = t.district;
  lblType.textContent = t.type;
  lblMaxPrice.textContent = t.maxPrice;
  btnReset.textContent = t.reset;
  btnShow.textContent = t.show;
  lblListings.textContent = t.listings;

  // чтобы в селектах "—" тоже был правильный язык:
  // просто перезаполним селекты текущими значениями
}

function translateType(typeValue) {
  const dict = T().types || {};
  return dict[typeValue] || typeValue || "";
}

function renderListings(items) {
  listingsEl.innerHTML = "";
  listingsCountEl.textContent = String(items.length);

  for (const it of items) {
    const card = document.createElement("div");
    card.className = "card";
    card.addEventListener("click", () => {
  localStorage.setItem("selectedListing", JSON.stringify(item));
  window.location.href = "detail.html";
});

    const title = document.createElement("div");
    title.style.fontSize = "18px";
    title.style.marginBottom = "6px";
    title.textContent = it.title || "";

    const meta = document.createElement("div");
    meta.className = "muted";
    meta.textContent = `${it.city || ""} • ${it.district || ""} • ${translateType(it.type)}`;

    const price = document.createElement("div");
    price.style.marginTop = "6px";
    price.textContent = `€ ${it.price ?? ""}`;

    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(price);

    listingsEl.appendChild(card);
  }
}

function getFilters() {
  return {
    city: cityEl.value || null,
    district: districtEl.value || null,
    type: typeEl.value || null,
    max_price: maxPriceEl.value ? Number(maxPriceEl.value) : null,
  };
}

function buildListingsUrl() {
  const f = getFilters();
  const qs = new URLSearchParams();
  if (f.city) qs.set("city", f.city);
  if (f.district) qs.set("district", f.district);
  if (f.type) qs.set("type", f.type);
  if (f.max_price !== null && !Number.isNaN(f.max_price)) qs.set("max_price", String(f.max_price));
  return `${API.listings}?${qs.toString()}`;
}

async function loadMetaAndInitSelects() {
  const meta = await apiGet(API.meta);

  fillSelect(cityEl, meta.cities || []);
  fillSelect(districtEl, meta.districts || []);
  fillSelect(typeEl, meta.types || []);

  // язык селекта
  langSelect.value = LANG;
}

async function loadAndRender() {
  const url = buildListingsUrl();
  const items = await apiGet(url);
  renderListings(items);
}

function resetFilters() {
  cityEl.value = "";
  districtEl.value = "";
  typeEl.value = "";
  maxPriceEl.value = "100000";
}

async function init() {
  // проверка бэка (не обязательно, но полезно)
  await apiGet(API.status);

  applyLangUI();
  await loadMetaAndInitSelects();
  await loadAndRender();
}

langSelect.addEventListener("change", async () => {
  LANG = langSelect.value;
  localStorage.setItem("lang", LANG);
  applyLangUI();
  // перезагрузка данных не нужна, просто перерисуем карточки на текущем языке:
  await loadMetaAndInitSelects();
  await loadAndRender();
});

btnReset.addEventListener("click", async () => {
  resetFilters();
  await loadAndRender();
});

btnShow.addEventListener("click", async () => {
  await loadAndRender();
});

document.addEventListener("DOMContentLoaded", init);

