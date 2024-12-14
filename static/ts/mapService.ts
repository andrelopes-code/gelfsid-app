import L from "leaflet";
import {
    BRAZIL_COORDINATES,
    APP_CONFIG,
    FILL_COLOR,
    STROKE_COLOR,
    HOST_CITY_KEY,
    STATE_CODE_MAP,
    WEAK_STROKE_COLOR,
    DEFAULT_MATERIAL_TYPE,
    GREEN_COLOR,
    ORANGE_COLOR,
    HOST_CITY_TOOLTIP_TEXT,
} from "./constants";
import type { Cache, CitySuppliers } from "./types";
import { supplierService } from "./supplierService";
import { getCityKey } from "./utils";

class MapService {
    private map: L.Map;

    private cache: Cache = {
        geojson: new Map(),
        suppliers: null,
        currentLayer: null,
    };

    private styleCache: Map<string, L.PathOptions> = new Map();

    private inSatetelliteMode = false;
    private citySuppliers: CitySuppliers = {};
    private citiesGeojsonLayer: L.GeoJSON | null = null;
    private currentStateCode: number | null = null;
    private currentType: string | null = null;

    private activeCityLayers: Set<L.Layer> = new Set();
    private activeShapefileLayers: Set<L.Layer> = new Set();

    private MAX_ZOOM = 18;
    private MIN_ZOOM = 4;
    private MAX_BOUNDS = L.latLngBounds(L.latLng(180, -180), L.latLng(-90, 180));
    private GELF_COORDINATES = L.latLng(-19.43852652, -44.34155513);

    private satelliteLayer: L.TileLayer | null = null;

    constructor() {
        this.map = L.map("map", {
            zoomControl: false,
            attributionControl: false,
            maxZoom: this.MAX_ZOOM,
            minZoom: this.MIN_ZOOM,
            maxBounds: this.MAX_BOUNDS,
        });

        this.satelliteLayer = L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            {
                attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
            }
        );

        this.map.setView(BRAZIL_COORDINATES, this.MIN_ZOOM);
        this.map.on("zoomend", this.onZoomChange);
    }

    private onZoomChange = () => {
        if (this.map.getZoom() > 10) {
            if (!this.map.hasLayer(this.satelliteLayer!)) {
                this.satelliteLayer!.addTo(this.map);
                this.updateGeoJSONStyleForSatellite(true);
                this.addAdditionalLayers(true);
                this.inSatetelliteMode = true;
            }
        } else {
            if (this.map.hasLayer(this.satelliteLayer!)) {
                this.map.removeLayer(this.satelliteLayer!);
                this.updateGeoJSONStyleForSatellite(false);
                this.addAdditionalLayers(false);
                this.inSatetelliteMode = false;
            }
        }
    };

    private updateGeoJSONStyleForSatellite(showSatellite: boolean) {
        if (this.citiesGeojsonLayer) {
            this.citiesGeojsonLayer.setStyle((feature: any) => {
                const cityKey = getCityKey(this.currentStateCode!, feature.properties.name);
                if (showSatellite) {
                    return {
                        color: "transparent",
                        interactive: false,
                        weight: 0,
                        fillOpacity: 0,
                        className: "",
                    };
                } else {
                    return this.cityStyleFunction(feature);
                }
            });
        }
    }

    private async addAdditionalLayers(showSatellite: boolean) {
        if (showSatellite) {
            // Adiciona shapefiles
        } else {
            // Remove shapefiles
        }
    }

    async loadGeoJSON(type: "states" | "cities", uf: string | null = null) {
        const key = uf ? `cities-${uf}` : "states";

        if (!this.cache.geojson.has(key)) {
            try {
                const url =
                    type === "states"
                        ? APP_CONFIG.geojson.states
                        : APP_CONFIG.geojson.cities.replace("{uf}", uf as string);

                const response = await fetch(url);
                if (!response.ok) throw new Error(`failed to load ${key}`);

                const geojsonData = await response.json();
                this.cache.geojson.set(key, geojsonData);
            } catch (error) {
                console.error(`error loading ${key}:`, error);
                throw error;
            }
        }

        return this.cache.geojson.get(key);
    }

    private calculateCityStyle(cityKey: string, currentType: string | null) {
        const cacheKey = `${cityKey}-${currentType}`;

        if (this.styleCache.has(cacheKey)) {
            return this.styleCache.get(cacheKey)!;
        }

        const base: L.PathOptions = {
            color: WEAK_STROKE_COLOR,
            fillColor: FILL_COLOR,
            fillOpacity: 1,
            weight: 1,
            className: "city-layer",
        };

        const suppliers = this.citySuppliers[cityKey];
        const filterDisabled = currentType === DEFAULT_MATERIAL_TYPE;

        if (suppliers && (filterDisabled || suppliers.some((s) => s.material_type === currentType))) {
            base.fillColor = STROKE_COLOR;

            switch (currentType) {
                case "Carvão Vegetal":
                    base.fillColor = GREEN_COLOR;
                    break;
                case "Minério de Ferro":
                    base.fillColor = ORANGE_COLOR;
                    break;
                case "Todos":
                    base.fillColor = ORANGE_COLOR;
            }
        }

        if (suppliers && base.fillColor === FILL_COLOR) {
            base.fillColor = "var(--off)";
        }

        // Armazena o estilo calculado no cache
        this.styleCache.set(cacheKey, base);
        return base;
    }

    private cityStyleFunction(feature: any) {
        const cityKey = getCityKey(this.currentStateCode!, feature.properties.name);
        return this.calculateCityStyle(cityKey, this.currentType);
    }

    async loadStates() {
        try {
            const data = await this.loadGeoJSON("states");

            L.geoJSON(data, {
                style: {
                    color: WEAK_STROKE_COLOR,
                    fillColor: FILL_COLOR,
                    weight: 2,
                    className: "state-layer",
                },
                onEachFeature: (feature, layer) => {
                    layer.on({
                        click: async () => {
                            await this.loadCities(STATE_CODE_MAP[feature.id as string]);
                        },
                    });
                },
            }).addTo(this.map);
        } catch (error) {
            console.error("error loading states:", error);
        }
    }

    async loadCities(stateCode: number) {
        try {
            // Caso tenha uma camada de cidades carregada,
            // remove os event listeners e a camada do mapa
            if (this.citiesGeojsonLayer) {
                this.citiesGeojsonLayer.off("mouseover mouseout click");
                this.map.removeLayer(this.citiesGeojsonLayer);
            }

            // Remove os event listeners das camadas anteriores
            // e limpa o Set que armazena essas camadas
            this.activeCityLayers.forEach((layer) => {
                layer.off();
            });
            this.activeCityLayers.clear();

            // Carrega o novo geoJSON para o estado
            //  selecionado e o adiciona ao mapa
            const data = await this.loadGeoJSON("cities", stateCode.toString());
            this.currentStateCode = stateCode;

            this.citiesGeojsonLayer = L.geoJSON(data, {
                style: this.cityStyleFunction.bind(this),
                onEachFeature: (feature, layer) => {
                    const cityKey = getCityKey(stateCode, feature.properties.name);
                    const isHostCity = cityKey === HOST_CITY_KEY;

                    if (isHostCity) {
                        const tooltipLatLng = this.GELF_COORDINATES;

                        const tooltip = L.tooltip({
                            permanent: true,
                            direction: "top",
                            className: "custom-tooltip-gelf",
                        }).setContent(HOST_CITY_TOOLTIP_TEXT);

                        tooltip.setLatLng(tooltipLatLng).addTo(this.map);
                        (layer as any).tooltip = tooltip;
                    }

                    this.activeCityLayers.add(layer);
                },
            }).addTo(this.map);

            const handleMouseInteraction = (e: L.LeafletMouseEvent) => {
                const layer = e.propagatedFrom;
                const feature = layer.feature;
                const cityKey = getCityKey(stateCode, feature.properties.name);

                if (e.type === "mouseover" && feature.properties) {
                    if (cityKey === HOST_CITY_KEY || this.inSatetelliteMode) return;

                    const tooltip = L.tooltip({
                        permanent: false,
                        direction: "top",
                        className: "custom-tooltip",
                    })
                        .setLatLng(e.latlng)
                        .setContent(feature.properties.name);

                    this.map.addLayer(tooltip);

                    layer._managedTooltip = {
                        tooltip: tooltip,
                        moveHandler: (moveEvent: L.LeafletMouseEvent) => {
                            tooltip.setLatLng(moveEvent.latlng);
                        },
                    };

                    layer.on("mousemove", layer._managedTooltip.moveHandler);
                } else if (e.type === "mouseout") {
                    if (layer._managedTooltip) {
                        this.map.removeLayer(layer._managedTooltip.tooltip);
                        layer.off("mousemove", layer._managedTooltip.moveHandler);
                        delete layer._managedTooltip;
                    }
                } else if (e.type === "click") {
                    if (feature.properties) {
                        layer._managedTooltip.tooltip.addTo(this.map);
                        supplierService.openDetails(cityKey, this.currentType);
                    }
                }
            };

            this.citiesGeojsonLayer
                .on("mouseover", handleMouseInteraction)
                .on("mouseout", handleMouseInteraction)
                .on("click", handleMouseInteraction);
        } catch (error) {
            console.error("error loading cities:", error);
        }
    }

    updateGeoJSONStyle() {
        if (this.citiesGeojsonLayer) {
            this.citiesGeojsonLayer.setStyle(this.cityStyleFunction.bind(this));
        }
    }

    async preloadCities() {
        const states = Object.keys(STATE_CODE_MAP);
        const maxConcurrent = 5;
        const pool = [];

        for (let i = 0; i < states.length; i++) {
            const state = states[i];
            pool.push(this.loadGeoJSON("cities", STATE_CODE_MAP[state].toString()));

            if (pool.length >= maxConcurrent || i === states.length - 1) {
                await Promise.all(pool);
                pool.length = 0;
            }
        }
    }

    setCurrentType(type: string) {
        this.currentType = type;
        this.updateGeoJSONStyle();
    }

    setCitySuppliers(suppliers: CitySuppliers) {
        this.citySuppliers = suppliers;
    }
}

export { MapService };
