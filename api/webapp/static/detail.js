const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

const API_BASE = "/api";

const detailCard = document.getElementById("detailCard");
const btnBack = document.getElementById("btnBack");

function detectLang(){
  return localStorage.getItem("lang") || "en";
}
let LANG = detectLang();

function t(key){
  const dict = window.I18N?.[LANG] || window.I18N.en;
  return dict[key] ?? (window.I18N.en[key] ?? key);
}

function setRTL(){
  document.documentElement.setAttribute("dir", window.isRTL(LANG) ? "rtl" : "ltr");
}

async function apiGet(path){
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function getId(){
  const u = new URL(window.location.href);
  const id = u.searchParams.get("id");
  return id ? Number(id) : null;
}

function render(item){
  const city = item.city || "";
  const district = item.district || "";
  const typeRaw = item.type || "";

  let typeShown = typeRaw;
  const typeKey = window.normalizeTypeKey(typeRaw);
  if (typeKey) typeShown = t(typeKey);

  const title = (item.title && String(item.title).trim()) ? item.title : t("listings");
  const price = item.price ?? "";

  detailCard.innerHTML = `
    <div class="cardTitle">${title}</div>
    <div class="cardMeta">${city}${district ? " • " + district : ""}${typeShown ? " • " + typeShown : ""}</div>
    <div class="cardPrice">${price !== "" ? € ${price} : ""}</div>
  `;
}

async function init(){
  setRTL();
  document.getElementById("detailTitle").textContent = t("catalog");
  detailCard.textContent = t("loading");
  btnBack.textContent = (window.isRTL(LANG) ? "→ " : "← ") + t("back");
  btnBack.addEventListener("click", () => history.back());

  const id = getId();
  if (!id) {
    detailCard.textContent = t("notFound");
    return;
  }

  try{
    const item = await apiGet(`${API_BASE}/listings/${id}`);
    render(item);
  }catch(e){
    detailCard.textContent = t("notFound");
  }
}

document.addEventListener("DOMContentLoaded", init);
