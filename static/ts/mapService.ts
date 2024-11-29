import L from "leaflet";
import {
    BRAZIL_COORDINATES,
    CONFIG,
    FILL_COLOR,
    STROKE_COLOR,
    HOST_CITY_KEY,
    STATE_CODE_MAP,
    WEAK_STROKE_COLOR,
    DEFAULT_MATERIAL_TYPE,
    GREEN_COLOR,
    ORANGE_COLOR,
} from "./constants";
import type { Cache, CitySuppliers } from "./types";
import { supplierService } from "./supplierService";

class MapService {
    private map: L.Map;
    private cache: Cache = {
        geojson: new Map(),
        suppliers: null,
        currentLayer: null,
    };
    private geojsonLayer: L.GeoJSON | null = null;
    private currentStateCode: number | null = null;
    private currentType: string | null = null;
    private citySuppliers: CitySuppliers = {};
    private activeLayers: Set<L.Layer> = new Set();
    private styleCache: Map<string, L.PathOptions> = new Map();

    private HOST_CITY_TOOLTIP_TEXT: string = "GELF Sete Lagoas";
    private MAX_ZOOM = 18;

    constructor() {
        this.map = L.map("map", {
            zoomControl: false,
            attributionControl: false,
            maxZoom: this.MAX_ZOOM,
        }).setView(BRAZIL_COORDINATES, 4);
    }

    async loadGeoJSON(type: "states" | "cities", uf: string | null = null): Promise<any> {
        const key = uf ? `cities-${uf}` : "states";

        if (!this.cache.geojson.has(key)) {
            try {
                const url =
                    type === "states"
                        ? CONFIG.geojson.states
                        : CONFIG.geojson.cities.replace("{uf}", uf as string);

                const response = await fetch(url);
                if (!response.ok) throw new Error(`failed to load ${key}`);

                const data = await response.json();
                this.cache.geojson.set(key, data);
            } catch (error) {
                console.error(`error loading ${key}:`, error);
                throw error;
            }
        }

        return this.cache.geojson.get(key);
    }

    private calculateCityStyle(cityKey: string, currentType: string | null): L.PathOptions {
        const cacheKey = `${cityKey}-${currentType}`;
        if (this.styleCache.has(cacheKey)) {
            return this.styleCache.get(cacheKey)!;
        }

        const base: L.PathOptions = {
            color: WEAK_STROKE_COLOR,
            fillColor: FILL_COLOR,
            fillOpacity: 1,
            weight: 1,
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
                    break;
            }
        }

        if (suppliers && base.fillColor === FILL_COLOR) {
            base.fillColor = "var(--off)";
        }

        // Armazena o estilo calculado no cache
        this.styleCache.set(cacheKey, base);
        return base;
    }

    private cityStyleFunction(feature: any): L.PathOptions {
        const cityKey = this.getCityKey(this.currentStateCode!, feature.properties.name);
        return this.calculateCityStyle(cityKey, this.currentType);
    }

    async loadStates(): Promise<void> {
        try {
            const data = await this.loadGeoJSON("states");

            L.geoJSON(data, {
                style: {
                    color: WEAK_STROKE_COLOR,
                    fillColor: FILL_COLOR,
                    fillOpacity: 1,
                    weight: 1.5,
                },
                onEachFeature: (feature, layer) => {
                    layer.on({
                        mouseover: () => {},
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

    async loadCities(stateCode: number): Promise<void> {
        try {
            const data = await this.loadGeoJSON("cities", stateCode.toString());
            this.currentStateCode = stateCode;

            this.activeLayers.forEach((layer) => {
                this.map.removeLayer(layer);
                this.activeLayers.delete(layer);
            });

            this.geojsonLayer = L.geoJSON(data, {
                style: this.cityStyleFunction.bind(this),
                onEachFeature: (feature, layer) => {
                    this.activeLayers.add(layer);

                    const cityKey = this.getCityKey(stateCode, feature.properties.name);
                    const isHostCity = cityKey === HOST_CITY_KEY;

                    if (feature.properties?.name) {
                        if (isHostCity) {
                            layer.bindTooltip(this.HOST_CITY_TOOLTIP_TEXT, {
                                permanent: true,
                                direction: "top",
                                className: "custom-tooltip-gelf",
                            });
                        }
                    }
                },
            }).addTo(this.map);

            this.geojsonLayer
                .on("mouseover", (e) => {
                    const feature = e.propagatedFrom.feature;
                    if (feature.properties) {
                        const cityKey = this.getCityKey(stateCode, feature.properties.name);
                        if (cityKey === HOST_CITY_KEY) return;

                        const tooltip = L.tooltip({
                            permanent: false,
                            direction: "top",
                            className: "custom-tooltip",
                        })
                            .setLatLng(e.latlng)
                            .setContent(feature.properties.name);

                        this.map.addLayer(tooltip);
                        (e.propagatedFrom as any)._currentTooltip = tooltip;

                        // Adiciona um listener para mover o tooltip junto com o mouse
                        e.propagatedFrom.on("mousemove", (moveEvent: any) => {
                            const tooltipToUpdate = (e.propagatedFrom as any)._currentTooltip;
                            if (tooltipToUpdate) {
                                tooltipToUpdate.setLatLng(moveEvent.latlng);
                            }
                        });
                    }
                })
                .on("mouseout", (e) => {
                    const tooltip = (e.propagatedFrom as any)._currentTooltip;
                    if (tooltip) {
                        this.map.removeLayer(tooltip);
                        delete (e.propagatedFrom as any)._currentTooltip;
                    }

                    // Remove o listener de movimento do mouse
                    e.propagatedFrom.off("mousemove");
                })
                .on("click", (e) => {
                    const feature = e.propagatedFrom.feature;
                    if (feature.properties) {
                        const cityKey = this.getCityKey(stateCode, feature.properties.name);
                        supplierService.openDetails(cityKey, this.currentType);
                    }
                });
        } catch (error) {
            console.error("error loading cities:", error);
        }
    }

    updateGeoJSONStyle(): void {
        if (this.geojsonLayer) {
            this.geojsonLayer.setStyle(this.cityStyleFunction.bind(this));
        }
    }

    async preloadCities(): Promise<void> {
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

    setCurrentType(type: string): void {
        this.currentType = type;
        this.updateGeoJSONStyle();
    }

    setCitySuppliers(suppliers: CitySuppliers): void {
        this.citySuppliers = suppliers;
    }

    private getCityKey(stateCode: number, cityName: string): string {
        return `${stateCode}-${cityName}`;
    }
}

export { MapService };
