const BRAZIL_COORDINATES = [-14.235, -51.925];
const HOST_CITY_KEY = "31-Sete Lagoas";
const FILL_COLOR = "#151b25";
const STROKE_COLOR = "#4b5260";

const CARV_TYPE = "Carvão Vegetal";
const MINE_TYPE = "Minério";
const MINE_COLOR = "var(--highlight)";
const CARV_COLOR = "var(--green-highlight)";

const GOOD_RATING_COLOR = CARV_COLOR;
const BAD_RATING_COLOR = MINE_COLOR;

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
let geojsonLayer;
let currentStateCode;
let currentType = CARV_TYPE;

function generateSupplierCards(suppliers) {
    const container = document.getElementById("supplier-cards-container");
    container.innerHTML = "";

    const template = document.getElementById("supplier-card-template");

    suppliers.forEach((supplier) => {
        const card = template.cloneNode(true);
        fields = card.querySelectorAll(".field");

        fields[0].textContent = supplier.razao_social;
        fields[1].textContent = supplier.cidade.nome + " - " + supplier.estado.nome;
        fields[2].textContent = supplier.cnpj;
        fields[3].textContent = supplier.tipo_material;
        fields[4].textContent = supplier.licenca_operacao;
        fields[5].textContent = supplier.certificacao_ambiental
            ? "Com Licença Ambiental"
            : "Sem Licença Ambiental";

        fields[6].textContent =
            supplier.distancia_em_metros !== null ? supplier.distancia_em_metros / 1000 + " km" : "N/A";

        // Muda a cor da borda para refletir o tipo de material
        card.querySelector("#card").style.borderColor =
            supplier.tipo_material === CARV_TYPE ? CARV_COLOR : MINE_COLOR;

        ratingDiv = card.querySelector("#supplier-rating");
        if (supplier.avaliacao > 80) {
            ratingDiv.style.color = GOOD_RATING_COLOR;
        } else {
            ratingDiv.style.color = BAD_RATING_COLOR;
        }
        ratingDiv.querySelector(".field").textContent = supplier.avaliacao;

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
        currentStateCode = stateCode;

        map.eachLayer((layer) => {
            if (layer.options && layer.options.active) {
                map.removeLayer(layer);
            }
        });

        geojsonLayer = L.geoJSON(data, {
            style: cityStyleFunction,
            onEachFeature: function (feature, layer) {
                layer.options.active = true;
                const cityKey = getCityKey(stateCode, feature.properties.name);
                const isHostCity = cityKey === HOST_CITY_KEY;

                if (feature.properties && feature.properties.name) {
                    if (isHostCity) {
                        layer.bindTooltip("GELF Sete Lagoas", {
                            permanent: true,
                            direction: "top",
                            className: "city-tooltip custom-tooltip-gelf",
                        });
                    } else {
                        layer.bindTooltip(feature.properties.name, {
                            permanent: false,
                            direction: "top",
                            className: "city-tooltip custom-tooltip",
                        });
                    }

                    layer.on({
                        mouseover: function (e) {
                            const layer = e.target;
                            layer.openTooltip();
                        },
                        mouseout: function (e) {
                            const layer = e.target;
                            if (!isHostCity) {
                                layer.closeTooltip();
                            }
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

function cityStyleFunction(feature) {
    const cityKey = getCityKey(currentStateCode, feature.properties.name);
    const suppliers = citySuppliers[cityKey];

    const base = {
        color: STROKE_COLOR,
        weight: 1,
        fillColor: FILL_COLOR,
        fillOpacity: 1,
    };

    if (suppliers && suppliers.some((s) => s.tipo_material === currentType)) {
        base.fillColor = "var(--material)";
    }

    if (suppliers && base.fillColor === FILL_COLOR) {
        base.fillColor = "var(--material-off)";
    }

    return base;
}

function updateGeoJSONStyle() {
    if (geojsonLayer) {
        geojsonLayer.setStyle(cityStyleFunction);
    }
}

async function loadSuppliers() {
    const response = await fetch(CONFIG.api.suppliers);
    const supplierData = await response.json();

    const suppliers = {};
    for (const supplier of supplierData) {
        const cityKey = getCityKey(stateCodeMap[supplier.estado.sigla], supplier.cidade.nome);
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

async function configureFilter() {
    const filter = document.getElementById("filter");

    filter.addEventListener("change", function () {
        if (this.checked) {
            currentType = MINE_TYPE;
            document.documentElement.style.setProperty("--material", "#d68367");
        } else {
            currentType = CARV_TYPE;
            document.documentElement.style.setProperty("--material", "#98e089");
        }
        updateGeoJSONStyle();
    });
}

async function init() {
    try {
        await configureFilter();
        await loadSuppliers();
        await loadStates();
        await preloadCities();
    } catch (error) {
        console.error("Error:", error);
    }
}

document.addEventListener("DOMContentLoaded", init);
