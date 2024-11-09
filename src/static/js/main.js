const BRAZIL_COORDINATES = [-14.235, -51.925];
const FILL_COLOR = "#151b25";
const STROKE_COLOR = "#4b5260";
const MIN_COLOR = "#f7a399";
const CV_COLOR = "#B8DFD0";

const CONFIG = {
    geojson: {
        states: "static/data/geojson/br_states.json",
        cities: "static/data/geojson/mun/geojs-{uf}-mun.json",
    },
    api: {
        suppliers: "http://localhost:8000/fornecedores/",
    },
};

const map = L.map("map", { zoomControl: false, attributionControl: false }).setView(BRAZIL_COORDINATES, 4);

const stateCodeMap = {
    RO: 11,
    AC: 12,
    AM: 13,
    RR: 14,
    PA: 15,
    AP: 16,
    TO: 17,
    MA: 21,
    PI: 22,
    CE: 23,
    RN: 24,
    PB: 25,
    PE: 26,
    AL: 27,
    SE: 28,
    BA: 29,
    MG: 31,
    ES: 32,
    RJ: 33,
    SP: 35,
    PR: 41,
    SC: 42,
    RS: 43,
    MS: 50,
    MT: 51,
    GO: 52,
    DF: 53,
};

const cache = {
    geojson: new Map(),
    suppliers: null,
    currentLayer: null,
};

let citySuppliers;

function generateSupplierCards(suppliers) {
    const container = document.getElementById("supplier-cards-container");
    container.innerHTML = "";

    const template = document.getElementById("supplier-card-template");

    suppliers.forEach((supplier) => {
        const card = template.cloneNode(true);
        container.appendChild(card);
    });
}

function getCityKey(stateCode, cityName) {
    return `${stateCode}-${cityName}`;
}

function openDetails(cityKey) {
    const suppliers = citySuppliers[cityKey];
    if (!suppliers) {
        return;
    }

    const detailsTitle = document.querySelector("#details-title");
    const detailsElement = document.getElementById("details");

    detailsTitle.textContent = suppliers[0].cidade.nome;
    generateSupplierCards(suppliers);

    detailsElement.classList.remove("translate-x-full");
    detailsElement.classList.add("translate-x-0");
}

function closeDetails() {
    const detailsElement = document.getElementById("details");
    detailsElement.classList.remove("translate-x-0");
    detailsElement.classList.add("translate-x-full");
}

async function loadGeoJSON(type, uf = null) {
    const key = uf ? `cities-${uf}` : "states";

    if (!cache.geojson.has(key)) {
        try {
            const url = type === "states" ? CONFIG.geojson.states : CONFIG.geojson.cities.replace("{uf}", uf);

            const response = await fetch(url);
            if (!response.ok) throw new Error(`Failed to load ${key}`);
            const data = await response.json();
            cache.geojson.set(key, data);
        } catch (error) {
            console.error(`Error loading ${key}:`, error);
            throw error;
        }
    }
    return cache.geojson.get(key);
}

async function loadStates() {
    try {
        const data = await loadGeoJSON("states");

        L.geoJSON(data, {
            style: {
                weight: 1,
                fillOpacity: 1,
                color: STROKE_COLOR,
                fillColor: FILL_COLOR,
            },
            onEachFeature: function (feature, layer) {
                layer.on("mouseover", function () {});
                layer.on("click", async function () {
                    loadCities(stateCodeMap[feature.id]);
                });
            },
        }).addTo(map);
    } catch (error) {
        console.error("Error loading states:", error);
    }
}

async function loadCities(stateCode) {
    try {
        const data = await loadGeoJSON("cities", stateCode);

        map.eachLayer((layer) => {
            if (layer.options && layer.options.active) {
                map.removeLayer(layer);
            }
        });

        L.geoJSON(data, {
            style: function (feature) {
                const cityKey = getCityKey(stateCode, feature.properties.name);
                const supplier = citySuppliers[cityKey];

                return {
                    color: STROKE_COLOR,
                    weight: 1,
                    fillColor: supplier ? CV_COLOR : FILL_COLOR,
                    fillOpacity: 1,
                };
            },
            onEachFeature: function (feature, layer) {
                layer.options.active = true;
                const cityKey = getCityKey(stateCode, feature.properties.name);

                if (feature.properties && feature.properties.name) {
                    layer.bindTooltip(feature.properties.name, {
                        permanent: false,
                        direction: "top",
                        className: "city-tooltip custom-tooltip",
                    });

                    layer.on({
                        mouseover: function (e) {
                            const layer = e.target;
                            layer.openTooltip();
                        },
                        mouseout: function (e) {
                            const layer = e.target;
                            layer.closeTooltip();
                        },
                        click: function (e) {
                            openDetails(cityKey);
                        },
                    });
                }
            },
        }).addTo(map);
    } catch (error) {
        console.error("Error loading cities:", error);
    }
}

async function loadSuppliers() {
    const response = await fetch(CONFIG.api.suppliers);
    const supplierData = await response.json();

    const suppliers = {};
    for (const supplier of supplierData) {
        const cityKey = `${stateCodeMap[supplier.estado.sigla]}-${supplier.cidade.nome}`;
        if (!suppliers[cityKey]) {
            suppliers[cityKey] = [];
        }
        suppliers[cityKey].push(supplier);
    }

    citySuppliers = suppliers;
}

async function preloadCities() {
    const promises = Object.keys(stateCodeMap).map((uf) => loadGeoJSON("cities", stateCodeMap[uf]));
    await Promise.all(promises);
}

async function init() {
    try {
        await loadSuppliers();
        await loadStates();
        await preloadCities();
    } catch (error) {
        console.error("Error:", error);
    }
}

init();
