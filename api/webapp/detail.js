const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

const UI = {
  en: { language:"Language", price:"Price", type:"Type", location:"Location", area:"Area (m²)", rooms:"Rooms", geo:"Geo", desc:"Description", contact:"Contact", back:"Back" },
  ru: { language:"Язык",     price:"Цена",  type:"Тип",  location:"Локация",  area:"Площадь (м²)", rooms:"Комнаты", geo:"Гео", desc:"Описание", contact:"Написать", back:"Назад" },
  bg: { language:"Език",     price:"Цена",  type:"Тип",  location:"Локация",  area:"Площ (м²)", rooms:"Стаи", geo:"Гео", desc:"Описание", contact:"Контакт", back:"Назад" },
  he: { language:"שפה",      price:"מחיר",  type:"סוג",  location:"מיקום",   area:"שטח (מ״ר)", rooms:"חדרים", geo:"מיקום", desc:"תיאור", contact:"צור קשר", back:"חזרה" }
};

function detectLang(){
  let lang = localStorage.getItem("lang");
  if (!lang) {
    const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code || "en";
    lang = (["ru","en","bg","he"].includes(tgLang)) ? tgLang : "en";
    localStorage.setItem("lang", lang);
  }
  return lang;
}

let LANG = detectLang();

function applyLang(){
  document.getElementById("lblLanguage").textContent = UI[LANG].language;
  document.getElementById("lblPrice").textContent = UI[LANG].price;
  document.getElementById("lblType").textContent = UI[LANG].type;
  document.getElementById("lblLocation").textContent = UI[LANG].location;
  document.getElementById("lblArea").textContent = UI[LANG].area;
  document.getElementById("lblRooms").textContent = UI[LANG].rooms;
  document.getElementById("lblGeo").textContent = UI[LANG].geo;
  document.getElementById("lblDesc").textContent = UI[LANG].desc;
  document.getElementById("btnContact").textContent = UI[LANG].contact;
  document.getElementById("btnBack").textContent = UI[LANG].back;

  // RTL для иврита
  document.documentElement.dir = (LANG === "he") ? "rtl" : "ltr";
  document.documentElement.lang = LANG;

  const langSelect = document.getElementById("langSelect");
  if (langSelect.value !== LANG) langSelect.value = LANG;
}

async function apiGet(path){
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function getIdFromUrl(){
  const url = new URL(window.location.href);
  const id = url.searchParams.get("id");
  return id ? Number(id) : null;
}

function renderGallery(images){
  const gallery = document.getElementById("gallery");
  gallery.innerHTML = "";
  if (!images || images.length === 0) {
    gallery.textContent = "—";
    return;
  }
  for (const src of images) {
    const img = document.createElement("img");
    img.className = "photo";
    img.src = src;
    img.loading = "lazy";
    gallery.appendChild(img);
  }
}

function normalizeType(t){
  if (!t) return "";
  if (LANG === "ru") return (t === "House") ? "Дом" : (t === "Apartment") ? "Квартира" : t;
  if (LANG === "bg") return (t === "House") ? "Къща" : (t === "Apartment") ? "Апартамент" : t;
  if (LANG === "he") return (t === "House") ? "בית" : (t === "Apartment") ? "דירה" : t;
  return t; // EN
}

async function init(){
  const langSelect = document.getElementById("langSelect");
  langSelect.value = LANG;
  langSelect.addEventListener("change", () => {
    LANG = langSelect.value;
    localStorage.setItem("lang", LANG);
    applyLang();
    // перерисуем type (перевод)
    const curType = document.getElementById("dType").dataset.raw || "";
    document.getElementById("dType").textContent = normalizeType(curType);
  });

  applyLang();

  const id = getIdFromUrl();
  if (!id) {
    document.getElementById("dTitle").textContent = "Not Found";
    return;
  }

  const item = await apiGet(`/api/listings/${id}`);

  document.getElementById("dTitle").textContent = item.title || "—";
  document.getElementById("dPrice").textContent = `€ ${item.price ?? "—"}`;

  const typeEl = document.getElementById("dType");
  typeEl.dataset.raw = item.type || "";
  typeEl.textContent = normalizeType(item.type);

  document.getElementById("dLocation").textContent = `${item.city || ""} · ${item.district || ""}`.trim();
  document.getElementById("dArea").textContent = item.area ? `${item.area}` : "—";
  document.getElementById("dRooms").textContent = item.rooms ? `${item.rooms}` : "—";
  document.getElementById("dGeo").textContent = item.geo || "—";
  document.getElementById("dDesc").textContent = item.description || "—";
  renderGallery(item.images);

  document.getElementById("btnContact").addEventListener("click", () => {
    // позже сделаем связь с ботом
    if (tg) {
      tg.showAlert("Next step: send lead to bot 🙂");
    } else {
      alert("Next step: send lead to bot 🙂");
    }
  });

  // Кнопка назад в Telegram
  if (tg) {
    tg.BackButton.show();
    tg.BackButton.onClick(() => window.location.href = "/");
  }
}

document.addEventListener("DOMContentLoaded", init);
