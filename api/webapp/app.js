// ====== НАСТРОЙКИ ======
const API_BASE = "http://127.0.0.1:8000"; // локально
// Когда будешь открывать через ngrok/телефон — поменяем на твой URL API (или сделаем через ngrok тоже)

// ====== UI ТЕКСТЫ ======
const UI = {
  ru: {
    title: "Каталог",
    lang: "Язык",
    city: "Город",
    district: "Район",
    type: "Тип",
    price: "Максимальная цена (€)",
    reset: "Сброс",
    show: "Показать",
    listings: "Объявления",
    empty: "Ничего не найдено. Попробуй изменить фильтры.",
    hintReady: "Выбери фильтры и нажми «Показать».",
    contact: "Написать",
  },
  en: {
    title: "Catalog",
    lang: "Language",
    city: "City",
    district: "District",
    type: "Type",
    price: "Max price (€)",
    reset: "Reset",
    show: "Show",
    listings: "Listings",
    empty: "No results. Try changing filters.",
    hintReady: "Select filters and tap “Show”.",
    contact: "Contact",
  },
  bg: {
    title: "Каталог",
    lang: "Език",
    city: "Град",
    district: "Район",
    type: "Тип",
    price: "Макс. цена (€)",
    reset: "Нулиране",
    show: "Покажи",
    listings: "Обяви",
    empty: "Няма резултати. Пробвай други филтри.",
    hintReady: "Избери филтри и натисни „Покажи“.",
    contact: "Пиши",
  },
  he: {
    title: "קטלוג",
    lang: "שפה",
    city: "עיר",
    district: "אזור",
    type: "סוג",
    price: "מחיר מקסימלי (€)",
    reset: "איפוס",
    show: "הצג",
    listings: "מודעות",
    empty: "לא נמצאו תוצאות. נסה לשנות מסננים.",
    hintReady: "בחר מסננים ולחץ “הצג”.",
    contact: "צור קשר",
  }
};

let catalog = null;
let botUsername = null;

const els = {
  langSelect: document.getElementById("langSelect"),
  citySelect: document.getElementById("citySelect"),
  districtSelect: document.getElementById("districtSelect"),
  typeSelect: document.getElementById("typeSelect"),
  maxPrice: document.getElementById("maxPrice"),
  btnReset: document.getElementById("btnReset"),
  btnShow: document.getElementById("btnShow"),
  cards: document.getElementById("cards"),
  count: document.getElementById("ui_count"),
  hint: document.getElementById("ui_hint"),

  ui_title: document.getElementById("ui_title"),
  ui_lang_label: document.getElementById("ui_lang_label"),
  ui_city_label: document.getElementById("ui_city_label"),
  ui_district_label: document.getElementById("ui_district_label"),
  ui_type_label: document.getElementById("ui_type_label"),
  ui_price_label: document.getElementById("ui_price_label"),
  ui_results_title: document.getElementById("ui_results_title"),
};

function setLanguageUI(lang){
  const t = UI[lang] || UI.en;
  els.ui_title.textContent = t.title;
  els.ui_lang_label.textContent = t.lang;
  els.ui_city_label.textContent = t.city;
  els.ui_district_label.textContent = t.district;
  els.ui_type_label.textContent = t.type;
  els.ui_price_label.textContent = t.price;
  els.btnReset.textContent = t.reset;
  els.btnShow.textContent = t.show;
  els.ui_results_title.textContent = t.listings;
  els.hint.textContent = t.hintReady;

  document.body.classList.toggle("rtl", lang === "he");
}

function opt(value, label){
  const o = document.createElement("option");
  o.value = value;
  o.textContent = label;
  return o;
}

function fillCities(lang){
  els.citySelect.innerHTML = "";
  const cities = catalog.cities;
  Object.keys(cities).forEach(code=>{
    els.citySelect.appendChild(opt(code, cities[code][lang] || cities[code].en || code));
  });
}

function fillDistricts(lang){
  els.districtSelect.innerHTML = "";
  const cityCode = els.citySelect.value || "varna";
  const city = catalog.cities[cityCode];
  const districts = city.districts || [];
  els.districtSelect.appendChild(opt("", "—"));
  districts.forEach(d=>{
    els.districtSelect.appendChild(opt(d.code, d[lang] || d.en || d.code));
  });
}

function fillTypes(lang){
  els.typeSelect.innerHTML = "";
  els.typeSelect.appendChild(opt("", "—"));
  (catalog.property_types || []).forEach(t=>{
    els.typeSelect.appendChild(opt(t.code, t[lang] || t.en || t.code));
  });
}

function translateDistrict(code, lang){
  const cityCode = els.citySelect.value || "varna";
  const list = catalog.cities[cityCode].districts || [];
  const f = list.find(x=>x.code===code);
  return f ? (f[lang] || f.en || code) : code;
}

function translateType(code, lang){
  const list = catalog.property_types || [];
  const f = list.find(x=>x.code===code);
  return f ? (f[lang] || f.en || code) : code;
}

function buildContactLink(listingId){
  // Покупатель нажимает -> открывается чат с ботом и подставляется текст
  const text = encodeURIComponent(`Здравствуйте! Интересует объект: ${listingId}`);
  return `https://t.me/${botUsername}?text=${text}`;
}

function renderCards(items, lang){
  els.cards.innerHTML = "";
  els.count.textContent = String(items.length);

  const t = UI[lang] || UI.en;

  if (!items.length){
    const div = document.createElement("div");
    div.className = "empty";
    div.textContent = t.empty;
    els.cards.appendChild(div);
    return;
  }

  items.forEach(x=>{
    const card = document.createElement("div");
    card.className = "card";

    const title = document.createElement("div");
    title.className = "title";
    title.textContent = x.title;

    const meta = document.createElement("div");
    meta.className = "meta";
    const districtName = translateDistrict(x.district, lang);
    const typeName = translateType(x.property_type, lang);
    meta.textContent = `${districtName} • ${typeName}`;

    const desc = document.createElement("div");
    desc.className = "desc";
    desc.textContent = x.description;

    const bottom = document.createElement("div");
    bottom.className = "bottom";

    const price = document.createElement("div");
    price.className = "price";
    price.textContent = `€ ${Number(x.price_eur).toLocaleString()}`;

    const a = document.createElement("a");
    a.className = "contact";
    a.href = buildContactLink(x.id);
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = t.contact;

    bottom.appendChild(price);
    bottom.appendChild(a);

    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(desc);
    card.appendChild(bottom);

    els.cards.appendChild(card);
  });
}

async function loadCatalog(){
  const r = await fetch(`${API_BASE}/catalog`);
  if(!r.ok) throw new Error("Catalog load failed");
  const data = await r.json();
  catalog = data.catalog;
  botUsername = data.bot_username || "your_bot";

  const lang = els.langSelect.value;
  setLanguageUI(lang);
  fillCities(lang);
  fillDistricts(lang);
  fillTypes(lang);
}

async function loadListings(){
  const lang = els.langSelect.value;

  const params = new URLSearchParams();
  params.set("city", els.citySelect.value || "varna");
  if (els.districtSelect.value) params.set("district", els.districtSelect.value);
  if (els.typeSelect.value) params.set("property_type", els.typeSelect.value);
  if (els.maxPrice.value) params.set("max_price", els.maxPrice.value);

  els.hint.textContent = "…";

  const r = await fetch(`${API_BASE}/listings?${params.toString()}`);
  if(!r.ok) {
    els.hint.textContent = "API error";
    return;
  }
  const items = await r.json();
  els.hint.textContent = UI[lang].hintReady;
  renderCards(items, lang);
}

function resetFilters(){
  els.districtSelect.value = "";
  els.typeSelect.value = "";
  els.maxPrice.value = "100000";
  loadListings();
}

els.langSelect.addEventListener("change", ()=>{
  const lang = els.langSelect.value;
  setLanguageUI(lang);
  fillCities(lang);
  fillDistricts(lang);
  fillTypes(lang);
  loadListings();
});

els.citySelect.addEventListener("change", ()=>{
  fillDistricts(els.langSelect.value);
  loadListings();
});

els.districtSelect.addEventListener("change", loadListings);
els.typeSelect.addEventListener("change", loadListings);

els.btnShow.addEventListener("click", loadListings);
els.btnReset.addEventListener("click", resetFilters);

(async ()=>{
  try{
    await loadCatalog();
    await loadListings();
  }catch(e){
    els.hint.textContent = "Cannot connect to API. Make sure uvicorn is running on 127.0.0.1:8000";
  }
})();