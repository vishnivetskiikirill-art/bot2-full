const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

const cityEl = document.getElementById("city");
const districtEl = document.getElementById("district");
const typeEl = document.getElementById("type");
const maxPriceEl = document.getElementById("maxPrice");
const btnReset = document.getElementById("btnReset");
const btnShow = document.getElementById("btnShow");
const listingsCountEl = document.getElementById("listingsCount");
const listingsEl = document.getElementById("listings");

async function apiGet(path) {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function fillSelect(selectEl, items) {
  // очистить и добавить пустой вариант
  selectEl.innerHTML = "";
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = "—";
  selectEl.appendChild(empty);

  for (const v of items) {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    selectEl.appendChild(opt);
  }
}
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
  en: { title: "Catalog", lang: "Language", city: "City", district: "District", type: "Type", maxPrice: "Max price (€)", reset: "Reset", show: "Show", listings: "Listings" },
  ru: { title: "Каталог", lang: "Язык", city: "Город", district: "Район", type: "Тип", maxPrice: "Макс. цена (€)", reset: "Сброс", show: "Показать", listings: "Объявления" },
  bg: { title: "Каталог", lang: "Език", city: "Град", district: "Район", type: "Тип", maxPrice: "Макс. цена (€)", reset: "Нулиране", show: "Покажи", listings: "Обяви" },
  he: { title: "קטלוג", lang: "שפה", city: "עיר", district: "אזור", type: "סוג", maxPrice: "מחיר מקס׳ (€)", reset: "איפוס", show: "הצג", listings: "מודעות" },
};

function applyUILang() {
  const t = UI[LANG] || UI.en;

  const title = document.getElementById("catalogTitle");
  const langLabel = document.getElementById("langLabel");
  if (title) title.textContent = t.title;
  if (langLabel) langLabel.textContent = t.lang;

  // если у тебя есть подписи с такими id — они тоже обновятся
  const cityLbl = document.getElementById("cityLabel");
  const distLbl = document.getElementById("districtLabel");
  const typeLbl = document.getElementById("typeLabel");
  const priceLbl = document.getElementById("maxPriceLabel");
  const resetBtn = document.getElementById("resetBtn");
  const showBtn = document.getElementById("showBtn");
  const listingsTitle = document.getElementById("listingsTitle");

  if (cityLbl) cityLbl.textContent = t.city;
  if (distLbl) distLbl.textContent = t.district;
  if (typeLbl) typeLbl.textContent = t.type;
  if (priceLbl) priceLbl.textContent = t.maxPrice;
  if (resetBtn) resetBtn.textContent = t.reset;
  if (showBtn) showBtn.textContent = t.show;
  if (listingsTitle) listingsTitle.textContent = t.listings;
}

document.addEventListener("DOMContentLoaded", () => {
  const langSelect = document.getElementById("langSelect");
  if (langSelect) {
    langSelect.value = LANG;
    langSelect.addEventListener("change", () => {
      localStorage.setItem("lang", langSelect.value);
      location.reload();
    });
  }
  applyUILang();
});
function renderListings(items) {
  listingsEl.innerHTML = "";
  listingsCountEl.textContent = String(items.length);

  if (!items.length) {
    listingsEl.innerHTML = `<div class="empty">No listings</div>`;
    return;
  }

  for (const x of items) {
    const title = x.title ?? "(no title)";
    const city = x.city ?? "";
    const district = x.district ?? "";
    const type = x.type ?? "";
    const price = x.price ?? "";

    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="card-title">${title}</div>
      <div class="card-meta">${city}${district ? " • " + district : ""}${type ? " • " + type : ""}</div>
      <div class="card-price">€ ${price}</div>
    `;
    listingsEl.appendChild(card);
  }
}

async function loadFilters() {
  const data = await apiGet("/api/filters");
  fillSelect(cityEl, data.cities || []);
  fillSelect(districtEl, data.districts || []);
  fillSelect(typeEl, data.types || []);
}

async function loadListings() {
  const params = new URLSearchParams();

  if (cityEl.value) params.set("city", cityEl.value);
  if (districtEl.value) params.set("district", districtEl.value);
  if (typeEl.value) params.set("type", typeEl.value);

  const mp = (maxPriceEl.value || "").trim();
  if (mp) params.set("max_price", mp);

  const data = await apiGet("/api/listings?" + params.toString());
  renderListings(Array.isArray(data) ? data : []);
}

btnReset.addEventListener("click", async () => {
  cityEl.value = "";
  districtEl.value = "";
  typeEl.value = "";
  maxPriceEl.value = "";
  await loadListings();
});

btnShow.addEventListener("click", async () => {
  await loadListings();
});

// старт
(async function init() {
  try {
    await loadFilters();
    await loadListings();
  } catch (e) {
    listingsEl.innerHTML = `<div class="empty">Error: ${e.message}</div>`;
  }
})();

