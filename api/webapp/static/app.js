const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

const API_BASE = "/api";

// элементы
const cityEl = document.getElementById("city");
const districtEl = document.getElementById("district");
const typeEl = document.getElementById("type");
const maxPriceEl = document.getElementById("maxPrice");
const btnReset = document.getElementById("btnReset");
const btnShow = document.getElementById("btnShow");
const listingsCountEl = document.getElementById("listingsCount");
const listingsBadgeEl = document.getElementById("listingsCountBadge");
const listingsEl = document.getElementById("listings");
const langSelect = document.getElementById("langSelect");

// i18n
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

const UI = {
  en: { title: "Catalog", lang: "Language", city: "City", district: "District", type: "Type", maxPrice: "Max price (€)", reset: "Reset", show: "Show", listings: "Listings", any: "—" },
  ru: { title: "Каталог", lang: "Язык", city: "Город", district: "Район", type: "Тип", maxPrice: "Макс. цена (€)", reset: "Сброс", show: "Показать", listings: "Объявления", any: "—" },
  bg: { title: "Каталог", lang: "Език", city: "Град", district: "Район", type: "Тип", maxPrice: "Макс. цена (€)", reset: "Нулиране", show: "Покажи", listings: "Обяви", any: "—" },
  he: { title: "קטלוג", lang: "שפה", city: "עיר", district: "אזור", type: "סוג", maxPrice: "מחיר מקס׳ (€)", reset: "איפוס", show: "הצג", listings: "מודעות", any: "—" },
};

const TYPE_TX = {
  en: { apartment: "Apartment", house: "House" },
  ru: { apartment: "Квартира", house: "Дом" },
  bg: { apartment: "Апартамент", house: "Къща" },
  he: { apartment: "דירה", house: "בית" },
};

function normalizeType(t) {
  const v = (t || "").toString().trim().toLowerCase();
  if (v === "apartment") return "apartment";
  if (v === "house") return "house";
  return v;
}
function tType(value) {
  const key = normalizeType(value);
  return (TYPE_TX[LANG] && TYPE_TX[LANG][key]) ? TYPE_TX[LANG][key] : (value || "");
}

function safeSetText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function applyLangToUI() {
  document.documentElement.dir = (LANG === "he") ? "rtl" : "ltr";

  safeSetText("titleCatalog", UI[LANG].title);
  safeSetText("labelLanguage", UI[LANG].lang);
  safeSetText("labelCity", UI[LANG].city);
  safeSetText("labelDistrict", UI[LANG].district);
  safeSetText("labelType", UI[LANG].type);
  safeSetText("labelMaxPrice", UI[LANG].maxPrice);
  safeSetText("listingsTitle", UI[LANG].listings);

  if (btnReset) btnReset.textContent = UI[LANG].reset;
  if (btnShow) btnShow.textContent = UI[LANG].show;
}

async function apiGet(path) {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function fillSelect(selectEl, items, withTranslateType = false) {
  if (!selectEl) return;

  selectEl.innerHTML = "";

  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = UI[LANG].any;
  selectEl.appendChild(empty);

  for (const v of items) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = withTranslateType ? tType(v) : v;
    selectEl.appendChild(opt);
  }
}

function buildQuery() {
  const params = new URLSearchParams();

  const city = cityEl?.value || "";
  const district = districtEl?.value || "";
  const type = typeEl?.value || "";
  const maxPrice = Number(maxPriceEl?.value || 0);

  if (city) params.set("city", city);
  if (district) params.set("district", district);
  if (type) params.set("type", type);
  if (maxPrice > 0) params.set("max_price", String(maxPrice));

  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

function openDetail(id) {
  window.location.href = `/detail?id=${encodeURIComponent(id)}`;
}

function renderListings(items) {
  if (listingsEl) listingsEl.innerHTML = "";

  if (listingsBadgeEl) listingsBadgeEl.textContent = String(items.length);
  if (listingsCountEl) listingsCountEl.textContent = String(items.length);

  for (const it of items) {
    const card = document.createElement("div");
    card.className = "card";
    card.style.cursor = "pointer";
    card.addEventListener("click", () => openDetail(it.id));

    const line1 = document.createElement("div");
    line1.className = "cardTitle";
    line1.textContent = it.title || "";

    const line2 = document.createElement("div");
    line2.className = "cardMeta";
    line2.textContent = `${it.city || ""} • ${it.district || ""} • ${tType(it.type)}`;

    const line3 = document.createElement("div");
    line3.className = "cardPrice";
    line3.textContent = `€ ${it.price ?? ""}`;

    card.appendChild(line1);
    card.appendChild(line2);
    card.appendChild(line3);

    listingsEl.appendChild(card);
  }
}

async function loadFilters() {
  const f = await apiGet(`${API_BASE}/filters`);
  fillSelect(cityEl, f.cities || []);
  fillSelect(districtEl, f.districts || []);
  fillSelect(typeEl, f.types || [], true);
}

async function loadListings() {
  const qs = buildQuery();
  const items = await apiGet(`${API_BASE}/listings${qs}`);
  renderListings(items);
}

function resetFilters() {
  if (cityEl) cityEl.value = "";
  if (districtEl) districtEl.value = "";
  if (typeEl) typeEl.value = "";
  if (maxPriceEl) maxPriceEl.value = "100000";
}

async function init() {
  // язык
  if (langSelect) {
    langSelect.value = LANG.toUpperCase();
    langSelect.addEventListener("change", async () => {
      const v = (langSelect.value || "EN").toLowerCase();
      LANG = ["ru", "en", "bg", "he"].includes(v) ? v : "en";
      localStorage.setItem("lang", LANG);

      applyLangToUI();
      await loadFilters();
      await loadListings();
    });
  }

  applyLangToUI();
  await loadFilters();
  await loadListings();

  btnReset?.addEventListener("click", async () => {
    resetFilters();
    await loadListings();
  });

  btnShow?.addEventListener("click", async () => {
    await loadListings();
  });
}

document.addEventListener("DOMContentLoaded", init);
