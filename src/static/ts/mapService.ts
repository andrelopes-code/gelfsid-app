import L from "leaflet";
import {
    BRAZIL_COORDINATES,
    CONFIG,
    FILL_COLOR,
    STROKE_COLOR,
    HOST_CITY_KEY,
    STATE_CODE_MAP,
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
    private currentType: string;
    private citySuppliers: CitySuppliers = {};
    private satelliteLayer: L.TileLayer;

    constructor(currentType: string) {
        this.map = L.map("map", {
            zoomControl: false,
            attributionControl: false,
            maxZoom: 17,
        }).setView(BRAZIL_COORDINATES, 4);
        this.currentType = currentType;
        this.satelliteLayer = this.setSatelliteLayer();
    }

    setSatelliteLayer() {
        return L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            {
                attribution:
                    "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
                maxZoom: 19,
            }
        );
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
                if (!response.ok) throw new Error(`Failed to load ${key}`);
                const data = await response.json();
                this.cache.geojson.set(key, data);
            } catch (error) {
                console.error(`Error loading ${key}:`, error);
                throw error;
            }
        }
        return this.cache.geojson.get(key);
    }

    private cityStyleFunction(feature: any): L.PathOptions {
        const cityKey = this.getCityKey(this.currentStateCode!, feature.properties.name);
        const suppliers = this.citySuppliers[cityKey];

        const base: L.PathOptions = {
            color: STROKE_COLOR,
            weight: 1,
            fillColor: FILL_COLOR,
            fillOpacity: 1,
        };

        if (suppliers && suppliers.some((s) => s.tipo_material === this.currentType)) {
            base.fillColor = "var(--material)";
        }

        if (suppliers && base.fillColor === FILL_COLOR) {
            base.fillColor = "var(--material-off)";
        }

        return base;
    }

    async loadStates(): Promise<void> {
        try {
            const data = await this.loadGeoJSON("states");

            L.geoJSON(data, {
                style: {
                    weight: 1,
                    fillOpacity: 1,
                    color: STROKE_COLOR,
                    fillColor: FILL_COLOR,
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
            console.error("Error loading states:", error);
        }
    }

    async loadCities(stateCode: number): Promise<void> {
        try {
            const data = await this.loadGeoJSON("cities", stateCode.toString());
            this.currentStateCode = stateCode;

            this.map.eachLayer((layer) => {
                if ((layer as any).options?.active) {
                    this.map.removeLayer(layer);
                }
            });

            this.geojsonLayer = L.geoJSON(data, {
                style: this.cityStyleFunction.bind(this),
                onEachFeature: (feature, layer) => {
                    (layer.options as any).active = true;
                    const cityKey = this.getCityKey(stateCode, feature.properties.name);
                    const isHostCity = cityKey === HOST_CITY_KEY;

                    if (feature.properties?.name) {
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
                            mouseover: (e) => {
                                const layer = e.target;
                                layer.openTooltip();
                            },
                            mouseout: (e) => {
                                const layer = e.target;
                                if (!isHostCity) {
                                    layer.closeTooltip();
                                }
                            },
                            click: () => {
                                supplierService.openDetails(cityKey);
                            },
                        });
                    }
                },
            }).addTo(this.map);
        } catch (error) {
            console.error("Error loading cities:", error);
        }
    }

    updateGeoJSONStyle(): void {
        if (this.geojsonLayer) {
            this.geojsonLayer.setStyle(this.cityStyleFunction.bind(this));
        }
    }

    async preloadCities(): Promise<void> {
        const promises = Object.keys(STATE_CODE_MAP).map((uf) =>
            this.loadGeoJSON("cities", STATE_CODE_MAP[uf].toString())
        );
        await Promise.all(promises);
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
