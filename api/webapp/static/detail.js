const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

const API_BASE = "/api";

const UI = {
  en: { title: "Detail", back: "← Back", metaSep: " • " },
  ru: { title: "Детали", back: "← Назад", metaSep: " • " },
  bg: { title: "Детайли", back: "← Назад", metaSep: " • " },
  he: { title: "פרטים", back: "← חזרה", metaSep: " • " },
};

const TYPE_TX = {
  en: { apartment: "Apartment", house: "House" },
  ru: { apartment: "Квартира", house: "Дом" },
  bg: { apartment: "Апартамент", house: "Къща" },
  he: { apartment: "דירה", house: "בית" },
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

function normalizeType(t) {
  const v = (t || "").toString().trim().toLowerCase();
  if (v === "apartment") return "apartment";
  if (v === "house") return "house";
  return v;
}

function tType(value) {
  const key = normalizeType(value);
  return (TYPE_TX[LANG] && TYPE_TX[LANG][key]) ? TYPE_TX[LANG][key] : value;
}

function applyLang() {
  document.documentElement.dir = (LANG === "he") ? "rtl" : "ltr";
  document.getElementById("titleDetail").textContent = UI[LANG].title;
  document.getElementById("btnBack").textContent = UI[LANG].back;

  const langSelect = document.getElementById("langSelect");
  if (langSelect) langSelect.value = LANG.toUpperCase();
}

async function apiGet(path) {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function getIdFromUrl() {
  const u = new URL(window.location.href);
  const id = u.searchParams.get("id");
  return id ? Number(id) : null;
}

function render(item) {
  document.getElementById("dTitle").textContent = item.title || "";
  document.getElementById("dMeta").textContent = ${item.city || ""}${UI[LANG].metaSep}${item.district || ""}${UI[LANG].metaSep}${tType(item.type)};
  document.getElementById("dPrice").textContent = € ${item.price ?? ""};
}

async function loadDetail() {
  const id = getIdFromUrl();
  if (!id) throw new Error("No id");
  const item = await apiGet(`${API_BASE}/listings/${id}`);
  render(item);
}

function init() {
  const langSelect = document.getElementById("langSelect");
  if (langSelect) {
    langSelect.addEventListener("change", async () => {
      const v = (langSelect.value || "EN").toLowerCase();
      LANG = ["ru", "en", "bg", "he"].includes(v) ? v : "en";
      localStorage.setItem("lang", LANG);
      applyLang();
      await loadDetail();
    });
  }

  document.getElementById("btnBack").addEventListener("click", () => {
    window.location.href = "/";
  });

  applyLang();
  loadDetail().catch(() => {
    // если не нашли — вернём назад
    window.location.href = "/";
  });
}

document.addEventListener("DOMContentLoaded", init);
