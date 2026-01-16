const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

const API_BASE = "/api";

const cityEl = document.getElementById("city");
const districtEl = document.getElementById("district");
const typeEl = document.getElementById("type");
const maxPriceEl = document.getElementById("maxPrice");

const btnReset = document.getElementById("btnReset");
const btnShow = document.getElementById("btnShow");

const listingsCountEl = document.getElementById("listingsCount");
const listingsEl = document.getElementById("listings");

const langSelect = document.getElementById("langSelect");

function detectLang() {
  let lang = localStorage.getItem("lang");
  if (!lang) {
    const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code || "en";
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

function setRTL(){
  document.documentElement.setAttribute("dir", window.isRTL(LANG) ? "rtl" : "ltr");
}

async function apiGet(path) {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function fillSelect(selectEl, items) {
  selectEl.innerHTML = "";
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = t("any");
  selectEl.appendChild(empty);

  for (const v of items) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    selectEl.appendChild(opt);
  }
}

function applyLanguageUI(){
  setRTL();

  document.getElementById("titleCatalog").textContent = t("catalog");
  document.getElementById("labelLanguage").textContent = t("language");
  document.getElementById("labelCity").textContent = t("city");
  document.getElementById("labelDistrict").textContent = t("district");
  document.getElementById("labelType").textContent = t("type");
  document.getElementById("labelMaxPrice").textContent = t("maxPrice");
  document.getElementById("labelListings").textContent = t("listings");

  btnReset.textContent = t("reset");
  btnShow.textContent = t("show");
}

function renderListings(items){
  listingsCountEl.textContent = String(items.length);
  listingsEl.innerHTML = "";

  for (const item of items) {
    const card = document.createElement("div");
    card.className = "cardItem";

    const city = item.city || "";
    const district = item.district || "";
    const typeRaw = item.type || "";

    let typeShown = typeRaw;
    const typeKey = window.normalizeTypeKey(typeRaw);
    if (typeKey) typeShown = t(typeKey);

    const title = (item.title && String(item.title).trim())
      ? item.title
      : (city || t("listings"));

    const price = item.price ?? "";

    card.innerHTML = `
      <div class="cardTitle">${title}</div>
      <div class="cardMeta">${city}${district ? " • " + district : ""}${typeShown ? " • " + typeShown : ""}</div>
      <div class="cardPrice">${price !== "" ? `€ ${price}` : ""}</div>
    `;

    // КЛИК → detail
    card.addEventListener("click", () => {
      if (!item.id) return;
      window.location.href = `/detail.html?id=${encodeURIComponent(item.id)}`;
    });

    listingsEl.appendChild(card);
  }
}

function getFilters(){
  return {
    city: cityEl.value || "",
    district: districtEl.value || "",
    type: typeEl.value || "",
    maxPrice: maxPriceEl.value || ""
  };
}

async function loadFilters(){
  const f = await apiGet(`${API_BASE}/filters`);
  fillSelect(cityEl, f.cities || []);
  fillSelect(districtEl, f.districts || []);
  fillSelect(typeEl, f.types || []);
}

async function loadListings(){
  const f = getFilters();
  const qs = new URLSearchParams();
  if (f.city) qs.set("city", f.city);
  if (f.district) qs.set("district", f.district);
  if (f.type) qs.set("type", f.type);
  if (f.maxPrice) qs.set("max_price", f.maxPrice);

  const url = `${API_BASE}/listings${qs.toString() ? "?" + qs.toString() : ""}`;
  const items = await apiGet(url);
  renderListings(items);
}

function resetFilters(){
  cityEl.value = "";
  districtEl.value = "";
  typeEl.value = "";
  maxPriceEl.value = "100000";
}

async function init(){
  langSelect.value = LANG;

  applyLanguageUI();
  await loadFilters();
  await loadListings();

  langSelect.addEventListener("change", async () => {
    LANG = langSelect.value;
    localStorage.setItem("lang", LANG);
    applyLanguageUI();
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

document.addEventListener("DOMContentLoaded", init);
