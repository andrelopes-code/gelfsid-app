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
    html,
} from "./constants";

import type { Cache, CitySuppliers, ShapefileData } from "./types";
import { supplierService } from "./supplierService";
import { getCityKey, getRandomPastelColor } from "./utils";
import { StyleService } from "./styleService";

class MapService {
    private MAX_ZOOM = 17;
    private MIN_ZOOM = 4;
    private SATELLITE_ZOOM = 11;

    private MAX_BOUNDS = L.latLngBounds(L.latLng(180, -180), L.latLng(-90, 180));
    private GELF_COORDINATES = L.latLng(-19.43852652, -44.34155513);

    private styleService: StyleService;

    private map!: L.Map;
    private gelfTooltip!: L.Tooltip;
    private satelliteLayer!: L.TileLayer;
    private activeCityNameTooltip!: { tooltip: L.Tooltip };

    private cache: Cache = {
        geojson: new Map(),
        suppliers: null,
        currentLayer: null,
    };

    private inSatelliteMode = false;
    private citySuppliers: CitySuppliers = {};
    private activeStateCode: number | null = null;
    private activeStateFeature: any | null = null;
    private activeMaterialType: string | null = null;

    private citiesGeojsonLayer: L.GeoJSON | null = null;
    private activeCityLayers = new Set<L.Layer>();
    private activeShapefileLayers = new Set<L.Layer>();


    private indexedLayers: Map<string, L.Layer[]> = new Map();
    private lastSearchResults: L.Layer[] = [];
    private currentSearchIndex: number = -1;
    private lastSearchQuery: string = "";


    constructor() {
        this.styleService = new StyleService();

        this.initializeMap();
        this.initializeSatelliteLayer();
        this.initializeGelfTooltip();
    }

    private initializeMap() {
        this.map = L.map("map", {
            zoomControl: false,
            attributionControl: false,
            maxZoom: this.MAX_ZOOM,
            minZoom: this.MIN_ZOOM,
            maxBounds: this.MAX_BOUNDS,
        });

        this.map.setView(BRAZIL_COORDINATES, this.MIN_ZOOM);

        this.map.on("zoomend", () => {
            if (this.map.getZoom() > this.SATELLITE_ZOOM) {
                /*
                    Caso o zoom seja maior que this.SATELLITE_ZOOM,
                    a camada de satelite deve ser adicionada juntamente
                    com os dados das propriedades (shapefiles)
                */
                this.enableSatelliteMode();
            } else {
                /*
                    Caso o zoom seja menor que this.SATELLITE_ZOOM,
                    a camada de satelite deve ser removida juntamente
                    com os dados das propriedades (shapefiles) e as
                    camadas anteriores devem ser visíveis novamente
                */
                this.disableSatelliteMode();
            }
        });
    }

    private initializeSatelliteLayer() {
        this.satelliteLayer = L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            {
                attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
            }
        );
    }

    private initializeGelfTooltip() {
        this.gelfTooltip = L.tooltip({
            permanent: true,
            direction: "top",
            className: "custom-tooltip custom-tooltip-gelf",
        });

        this.gelfTooltip.setContent(HOST_CITY_TOOLTIP_TEXT);
        this.gelfTooltip.setLatLng(this.GELF_COORDINATES);
    }

    private enableSatelliteMode() {
        if (!this.map.hasLayer(this.satelliteLayer)) {
            this.satelliteLayer.addTo(this.map);

            this.updateStyleForSateliteMode(true);
            this.addShapefileLayers(true);

            this.inSatelliteMode = true;

            // Mostra os controles de pesquisa de shapefiles
            document.getElementById("shapes-search-controls")?.classList.remove("hidden");

            // Fecha os detalhes de fornecedores caso estejam abertos.
            supplierService.closeDetails();
        }
    }

    private disableSatelliteMode() {
        if (this.map.hasLayer(this.satelliteLayer)) {
            this.map.removeLayer(this.satelliteLayer);

            this.updateStyleForSateliteMode(false);
            this.addShapefileLayers(false);

            this.inSatelliteMode = false;

            // Oculta os controles de pesquisa de shapefiles
            document.getElementById("shapes-search-controls")?.classList.add("hidden");
        }
    }

    private updateStyleForSateliteMode(showSatellite: boolean) {
        if (this.citiesGeojsonLayer) {
            this.citiesGeojsonLayer.setStyle((feature: any) => {
                if (showSatellite) {
                    /*
                        Remove o ultimo tooltip de nome de
                        cidade ativo ao trocar para satélite.
                    */
                    this.activeCityNameTooltip.tooltip.close();

                    /*
                        muda o estilo das camadas de cidade,
                        ocultando-as para mostrar a camada
                        de satélite.
                    */
                    return {
                        color: "transparent",
                        interactive: false,
                        weight: 0,
                        fillOpacity: 0,
                        className: "",
                    };
                } else {
                    /*
                        Caso contrário, retoma os estilos anteriores.
                    */
                    return this.cityStyleFunction(feature);
                }
            });
        }
    }

    private async addShapefileLayers(showSatellite: boolean) {
        const currentState = this.activeStateFeature?.id;

        if (showSatellite && currentState) {
            const shapefiles: ShapefileData[] = await this.loadGeoJSON("shapefiles", currentState);
            shapefiles.forEach((shapefile) => this.addShapefileLayer(shapefile));
        } else {
            /*
                Caso showSatellite seja falso, limpa as
                camadas de shapefiles adicionadas.
            */
            this.clearShapefileLayers();
        }
    }

    private addShapefileLayer(shapefile: ShapefileData) {
        const geojson = JSON.parse(shapefile.geojson);
        const randomColor = getRandomPastelColor();

        const mainLayer = L.geoJSON(geojson, {
            style: (feature: any) => {
                const isProperty = feature?.properties?.MATRICULA;

                if (isProperty) {
                    return {
                        color: "#FFFFFF33",
                        fillColor: "#FFFFFF33",
                        fillOpacity: 0.1,
                        weight: 2,
                        className: "shapefile-layer",
                    };
                } else {
                    return {
                        color: randomColor,
                        fillColor: randomColor,
                        fillOpacity: 0.1,
                        weight: 2,
                        className: "shapefile-layer",
                    };
                }
            },
        });

        const subLayers = mainLayer.getLayers();

        subLayers.forEach((layer) => {
            const layerProperties = (layer as any)?.feature?.properties;

            layer.bindPopup(this.createShapefileTooltipContent(layerProperties, shapefile), {
                closeButton: true,
                closeOnEscapeKey: true,
                interactive: true,
                className: "shapefile-popup",
            });

            layer.on("click", () => {
                layer.openPopup();
            });

            layer.on("remove", () => {
                layer.closePopup();
            });

            // Adiciona as propriedades do shapefile nas propriedades da camada.
            (layer as any).feature.properties.supplier_name = shapefile.supplier_name;
            (layer as any).feature.properties.name = shapefile.name;

            this.activeShapefileLayers.add(layer);
        });

        this.map.addLayer(mainLayer);
    }

    private clearShapefileLayers() {
        /*
            Limpa as camadas de shapefiles ativas
            e remove os event listeners.
        */
        this.activeShapefileLayers.forEach((layer) => {
            this.map.removeLayer(layer);
            layer.off();
        });

        this.activeShapefileLayers.clear();
    }

    private searchShapefileLayers(query: string): Array<L.Layer> {
        const results: L.Layer[] = [];
        query = query.toLowerCase();

        /*
            Percorre todas as camadas de shapefile ativas
            e verifica se algum deles contém o termo de
            busca, armazenando-as na lista de resultados.
        */
        this.activeShapefileLayers.forEach((layer) => {
            const layerProperties = (layer as any)?.feature?.properties;

            if (layerProperties) {
                const searchableAttributes = [
                    layerProperties.supplier_name?.toLowerCase(),
                    layerProperties?.name?.toLowerCase(),
                    layerProperties?.TALHAO?.toString().toLowerCase(),
                ];

                if (searchableAttributes.some((attr) => attr && attr.includes(query))) {
                    results.push(layer);
                }
            }
        });

        return results;
    }

    public searchShapefilesAndNavigate(query: string, direction: "next" | "prev") {
        if (this.inSatelliteMode) {
            if (query !== this.lastSearchQuery) {
                this.lastSearchResults = this.searchShapefileLayers(query);
                this.currentSearchIndex = -1;
                this.lastSearchQuery = query;
            }

            if (this.lastSearchResults.length === 0) {
                return;
            }

            if (direction === "next") {
                this.currentSearchIndex = (this.currentSearchIndex + 1) % this.lastSearchResults.length;
            } else if (direction === "prev") {
                this.currentSearchIndex =
                    (this.currentSearchIndex - 1 + this.lastSearchResults.length) %
                    this.lastSearchResults.length;
            }

            const layer = this.lastSearchResults[this.currentSearchIndex];
            this.focusLayer(layer);
        }
    }

    private focusLayer(layer: L.Layer) {
        /**
        Função que centra o mapa na camada de informada,
        abre a popup e configura o zoom máximo para 16.
        */
        const bounds = (layer as any).getBounds?.();

        layer.openPopup();

        if (bounds) {
            this.map.fitBounds(bounds, {
                padding: [50, 50],
                maxZoom: 16,
            });
        }
    }

    private createShapefileTooltipContent(properties: any, shapefile: any) {
        const propertiesMapping = {
            PLANTIO: "Plantio",
            EXECUCAO: "Execução",
            DATAPLANTI: "Data do Plantio",
            TALHAO: "Talhão",
            CNPJ_CPF: "CNPJ/CPF",
            AREA: "Área",
            MUNICIPIO: "Municipio",
            PROPRIETAR: "Proprietário",
            MATRICULA: "Matricula",
            CARTORIO: "Cartório",
            IDENTIFICA: "Identificação",
        };

        const dynamicContent = Object.entries(propertiesMapping)
            .map(([key, label]) => {
                const value = properties[key];

                if (value) {
                    const displayValue = value || "Não informado";

                    return `
                        <div style="margin-bottom: 6px;" class="flex gap-4 justify-between w-full">
                            <strong>${label}:</strong> ${displayValue}
                        </div>
                    `;
                }

                return "";
            })
            .join("");

        return `
            <div class="text-nowrap" style="font-size: 12px;" class="text-center">
                <div class="text-center" style="font-weight: bold; font-size: 14px; margin-bottom: 16px;">
                    ${shapefile.name} (${shapefile.id})
                </div>
                <div style="margin-bottom: 6px;" class="flex gap-4 justify-between w-full">
                    <strong>Fornecedor:</strong> ${shapefile.supplier_name || "Não informado"}
                </div>
                ${dynamicContent}
            </div>
        `;
    }

    private async loadGeoJSON(type: "states" | "cities" | "shapefiles", uf: string | null = null) {
        const cacheKey = type === "states" ? type : `${type}-${uf}`;

        /*
            Verifica se o GeoJSON já está em cache.
            Caso contrário, faz a requisição e o armazena.
        */
        if (!this.cache.geojson.has(cacheKey)) {
            try {
                let url = "";

                /*
                    Define a URL do recurso com base no tipo
                    e no estado (se aplicável).
                */
                if (type === "shapefiles") {
                    url = APP_CONFIG.api.shapefiles(uf as string);
                } else if (type === "states") {
                    url = APP_CONFIG.geojson.states;
                } else if (type === "cities") {
                    url = APP_CONFIG.geojson.cities.replace("{uf}", uf as string);
                }

                /*
                    Faz a requisição ao recurso e lança uma exceção
                    em caso de erro na resposta.
                */
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`failed to load ${cacheKey}`);
                }

                /*
                    Parseia os dados GeoJSON e os armazena em cache
                    para evitar futuras requisições.
                */
                const geojsonData = await response.json();
                this.cache.geojson.set(cacheKey, geojsonData);
            } catch (error) {
                console.error(`error loading ${cacheKey}:`, error);
                throw error;
            }
        }

        return this.cache.geojson.get(cacheKey);
    }

    private cityStyleFunction(feature: any) {
        /*
            Calcula e retorna o estilo da cidade com base na
            chave gerada e no tipo de exibição atual.
        */
        const cityKey = getCityKey(this.activeStateCode!, feature.properties.name);
        return this.styleService.getCityStyle(cityKey, this.activeMaterialType, this.citySuppliers);
    }

    async loadStates() {
        try {
            const statesGeojsonData = await this.loadGeoJSON("states");

            L.geoJSON(statesGeojsonData, {
                style: {
                    color: WEAK_STROKE_COLOR,
                    fillColor: FILL_COLOR,
                    weight: 2,
                    className: "state-layer",
                },
                onEachFeature: (feature, layer) => {
                    layer.on({
                        click: async () => {
                            this.activeStateFeature = feature;
                            await this.loadStateCities(STATE_CODE_MAP[feature.id as string]);
                        },
                    });
                },
            }).addTo(this.map);
        } catch (error) {
            console.error("error loading states:", error);
        }
    }

    async loadStateCities(stateCode: number) {
        try {
            if (this.citiesGeojsonLayer) {
                this.map.removeLayer(this.citiesGeojsonLayer);
            }

            this.activeCityLayers.forEach((layer) => {
                layer.off();
            });
            this.activeCityLayers.clear();

            const data = await this.loadGeoJSON("cities", stateCode.toString());
            this.activeStateCode = stateCode;

            this.citiesGeojsonLayer = L.geoJSON(data, {
                style: this.cityStyleFunction.bind(this),
                onEachFeature: (feature, layer) => {
                    this.activeCityLayers.add(layer);
                },
            }).addTo(this.map);

            /*
                Exibe ou remove o tooltip da GELF com base no estado selecionado.
                (GELF é exibido apenas em Minas Gerais, código 31).
            */
            stateCode == 31 ? this.gelfTooltip.addTo(this.map) : this.gelfTooltip.remove();

            /*
                Define o comportamento de interação com o mouse
                nas camadas de cidade (mouseover, mouseout e click).
            */
            const handleMouseInteraction = (e: L.LeafletMouseEvent) => {
                const layer = e.propagatedFrom;
                const feature = layer.feature;
                const cityKey = getCityKey(stateCode, feature.properties.name);

                const notInSatelliteMode = !this.inSatelliteMode;
                const isNotHostCity = cityKey !== HOST_CITY_KEY;

                if (e.type === "mouseover" && feature.properties && isNotHostCity && notInSatelliteMode) {
                    const tooltip = L.tooltip({
                        permanent: false,
                        direction: "top",
                        className: "custom-tooltip",
                    })
                        .setLatLng(e.latlng)
                        .setContent(feature.properties.name);

                    this.map.addLayer(tooltip);

                    layer._activeTooltip = {
                        tooltip: tooltip,
                        moveHandler: (moveEvent: L.LeafletMouseEvent) => {
                            tooltip.setLatLng(moveEvent.latlng);
                        },
                    };

                    this.activeCityNameTooltip = layer._activeTooltip;
                    layer.on("mousemove", layer._activeTooltip.moveHandler);
                } else if (e.type === "mouseout") {
                    if (layer._activeTooltip) {
                        this.map.removeLayer(layer._activeTooltip.tooltip);
                        layer.off("mousemove", layer._activeTooltip.moveHandler);
                        delete layer._activeTooltip;
                    }
                } else if (e.type === "click" && notInSatelliteMode) {
                    if (feature.properties) {
                        layer._activeTooltip?.tooltip.addTo(this.map);
                        supplierService.openDetails(cityKey, this.activeMaterialType);
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

    async preloadCities() {
        const states = Object.keys(STATE_CODE_MAP);
        const maxConcurrent = 5;
        const pool = [];

        for (let i = 0; i < states.length; i++) {
            const state = states[i];

            /*
                Adiciona o carregamento assíncrono de GeoJSON
                para as cidades de cada estado na "pool".
                A pool controla os carregamentos simultâneos.
            */
            pool.push(this.loadGeoJSON("cities", STATE_CODE_MAP[state].toString()));

            /*
                Quando o limite máximo de carregamentos simultâneos
                é alcançado ou todos os estados foram processados,
                aguarda a conclusão dos carregamentos na pool
                e a esvazia para continuar.
            */
            if (pool.length >= maxConcurrent || i === states.length - 1) {
                await Promise.all(pool);
                pool.length = 0;
            }
        }
    }

    updateGeoJSONStyle() {
        if (this.citiesGeojsonLayer) {
            this.citiesGeojsonLayer.setStyle(this.cityStyleFunction.bind(this));
        }
    }

    setActiveMaterialType(type: string) {
        this.activeMaterialType = type;
        this.updateGeoJSONStyle();
    }

    setCitySuppliers(suppliers: CitySuppliers) {
        this.citySuppliers = suppliers;
    }
}

export { MapService };
