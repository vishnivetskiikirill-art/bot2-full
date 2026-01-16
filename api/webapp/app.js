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
