const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

const API_BASE = "/api";

const el = (id) => document.getElementById(id);

const langSelect = el("langSelect");
const cityEl = el("city");
const districtEl = el("district");
const typeEl = el("type");
const maxPriceEl = el("maxPrice");
const btnReset = el("btnReset");
const btnShow = el("btnShow");
const listingsCountEl = el("listingsCount");
const listingsEl = el("listings");

const titleCatalogEl = el("titleCatalog");
const labelLanguageEl = el("labelLanguage");
const labelCityEl = el("labelCity");
const labelDistrictEl = el("labelDistrict");
const labelTypeEl = el("labelType");
const labelMaxPriceEl = el("labelMaxPrice");
const listingsTitleEl = el("listingsTitle");

async function apiGet(path){
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function detectLang(){
  let lang = localStorage.getItem("lang");
  if (!lang) {
    const tgLang = tg?.initDataUnsafe?.user?.language_code || "en";
    lang = ["ru","en","bg","he"].includes(tgLang) ? tgLang : "en";
    localStorage.setItem("lang", lang);
  }
  return lang;
}

let LANG = detectLang();

function t(key){
  const dict = window.I18N?.[LANG] || window.I18N.en;
  return dict[key] ?? (window.I18N.en[key] ?? key);
}

function applyLang(){
  // RTL switch
  document.documentElement.setAttribute("dir", window.isRTL(LANG) ? "rtl" : "ltr");

  // UI labels
  titleCatalogEl.textContent = t("title");
  labelLanguageEl.textContent = t("language");
  labelCityEl.textContent = t("city");
  labelDistrictEl.textContent = t("district");
  labelTypeEl.textContent = t("type");
  labelMaxPriceEl.textContent = t("maxPrice");
  btnReset.textContent = t("reset");
  btnShow.textContent = t("show");
  listingsTitleEl.textContent = t("listings");

  // placeholders
  setPlaceholder(cityEl, t("any"));
  setPlaceholder(districtEl, t("any"));
  setPlaceholder(typeEl, t("any"));
}

function setPlaceholder(selectEl, text){
  // первая опция — пустая
  if (!selectEl) return;
  selectEl.innerHTML = "";
  const opt = document.createElement("option");
  opt.value = "";
  opt.textContent = text;
  selectEl.appendChild(opt);
}

function addOptions(selectEl, items){
  for (const v of items) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    selectEl.appendChild(opt);
  }
}

async function loadFilters(){
  const data = await apiGet(`${API_BASE}/filters`);

  setPlaceholder(cityEl, t("any"));
  setPlaceholder(districtEl, t("any"));
  setPlaceholder(typeEl, t("any"));

  addOptions(cityEl, data.cities || []);
  addOptions(districtEl, data.districts || []);
  addOptions(typeEl, data.types || []);
}

function getCurrentFilters(){
  const city = cityEl.value || "";
  const district = districtEl.value || "";
  const type = typeEl.value || "";
  const maxPrice = Number(maxPriceEl.value || 0);

  return { city, district, type, maxPrice };
}

async function loadListings(){
  const { city, district, type, maxPrice } = getCurrentFilters();

  const params = new URLSearchParams();
  if (city) params.set("city", city);
  if (district) params.set("district", district);
  if (type) params.set("type", type);
  if (maxPrice) params.set("max_price", String(maxPrice));

  const url = `${API_BASE}/listings?${params.toString()}`;
  const items = await apiGet(url);

  renderListings(items || []);
}

function renderListings(items){
  listingsCountEl.textContent = String(items.length);
  listingsEl.innerHTML = "";

  for (const item of items) {
    const card = document.createElement("div");
    card.className = "card";

    // title (если нет — соберем из меты)
    const title = (item.title && String(item.title).trim()) ? item.title : "";

    const city = item.city || "";
    const district = item.district || "";
    const typeRaw = item.type || "";

    // локализация типа (Apartment/House)
    let typeShown = typeRaw;
    const typeKey = window.normalizeTypeKey(typeRaw);
    if (typeKey) typeShown = t(typeKey);

    const price = item.price ?? "";

    const titleEl = document.createElement("div");
    titleEl.className = "cardTitle";
    titleEl.textContent = title || `${city}${district ? " • " + district : ""}`;

    const metaEl = document.createElement("div");
    metaEl.className = "cardMeta";
    metaEl.textContent = `${city}${district ? " • " + district : ""}${typeShown ? " • " + typeShown : ""}`;

    const priceEl = document.createElement("div");
    priceEl.className = "cardPrice";
    priceEl.textContent = price !== "" ? `€ ${price}` : "";

    card.appendChild(titleEl);
    card.appendChild(metaEl);
    card.appendChild(priceEl);

    listingsEl.appendChild(card);
  }
}

function resetFilters(){
  cityEl.value = "";
  districtEl.value = "";
  typeEl.value = "";
  maxPriceEl.value = "100000";
}

function bindEvents(){
  langSelect.addEventListener("change", async () => {
    LANG = langSelect.value;
    localStorage.setItem("lang", LANG);
    applyLang();
    await loadFilters();
    await loadListings();
  });

  btnReset.addEventListener("click", async () => {
    resetFilters();
    await loadListings();
  });

  btnShow.addEventListener("click", async () => {
    await loadListings();
  });
}

async function init(){
  // set initial select value
  langSelect.value = LANG;

  applyLang();
  bindEvents();

  await loadFilters();
  await loadListings();
}

document.addEventListener("DOMContentLoaded", init);
