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

class MapService {
    private MAX_ZOOM = 17;
    private MIN_ZOOM = 4;
    private SATELLITE_ZOOM = 11;

    private MAX_BOUNDS = L.latLngBounds(L.latLng(180, -180), L.latLng(-90, 180));
    private GELF_COORDINATES = L.latLng(-19.43852652, -44.34155513);

    private map!: L.Map;
    private gelfTooltip!: L.Tooltip;
    private satelliteLayer!: L.TileLayer;
    private activeCityNameTooltip!: { tooltip: L.Tooltip };

    private cache: Cache = {
        geojson: new Map(),
        suppliers: null,
        currentLayer: null,
    };
    private styleCache = new Map<string, L.PathOptions>();
    private satelliteMode = false;
    private citySuppliers: CitySuppliers = {};
    private currentStateCode: number | null = null;
    private activeStateFeature: any | null = null;
    private currentMaterialType: string | null = null;

    private citiesGeojsonLayer: L.GeoJSON | null = null;
    private activeCityLayers = new Set<L.Layer>();
    private activeShapefileLayers = new Set<L.Layer>();

    constructor() {
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
        this.map.on("zoomend", this.onZoomChange);
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

    private onZoomChange = () => {
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
    };

    private enableSatelliteMode() {
        if (!this.map.hasLayer(this.satelliteLayer)) {
            this.satelliteLayer.addTo(this.map);

            this.updateGeoJSONStyleForSatelliteMode(true);
            this.addShapefileLayers(true);

            this.satelliteMode = true;
        }
    }

    private disableSatelliteMode() {
        if (this.map.hasLayer(this.satelliteLayer)) {
            this.map.removeLayer(this.satelliteLayer);

            this.updateGeoJSONStyleForSatelliteMode(false);
            this.addShapefileLayers(false);

            this.satelliteMode = false;
        }
    }

    private updateGeoJSONStyleForSatelliteMode(showSatellite: boolean) {
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

        /*
            Cores aleatórias para as camadas de
            produção florestal e uma cor fixa para
            camadas de propriedade.
        */
        const randomColor = getRandomPastelColor();
        const propertyColor = "#FFFFFF77";


        /*
            A camada principal que agrupa todas
            as sub-camadas. Ela define o estilo
            que terão as sub-camadas de acordo
            com o tipo (propriedade ou produção florestal).
        */
        const mainLayer = L.geoJSON(geojson, {
            style: (feature) => {
                if (feature?.properties?.MATRICULA) {
                    return {
                        color: propertyColor,
                        fillColor: propertyColor,
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
            /*
                Tenta pegar as propriedades da camada caso existam.
            */
            const layerProperties = (layer as any)?.feature?.properties;

            layer.bindPopup(this.createTooltipContent(layerProperties, shapefile), {
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

    private createTooltipContent(properties: any, shapefile: any) {
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
        const cityKey = getCityKey(this.currentStateCode!, feature.properties.name);
        return this.calculateCityStyle(cityKey, this.currentMaterialType);
    }

    private calculateCityStyle(cityKey: string, currentMaterialType: string | null) {
        const cacheKey = `${cityKey}-${currentMaterialType}`;

        /*
            Verifica se o estilo da cidade já está armazenado no cache.
            Caso esteja, retorna diretamente o estilo previamente calculado.
        */
        if (this.styleCache.has(cacheKey)) {
            return this.styleCache.get(cacheKey)!;
        }

        const style: L.PathOptions = {
            color: WEAK_STROKE_COLOR,
            fillColor: FILL_COLOR,
            fillOpacity: 1,
            weight: 1,
            className: "city-layer",
        };

        /*
            Obtém os fornecedores associados à cidade e verifica se
            o filtro de tipo de material está habilitado ou desabilitado.
        */
        const suppliers = this.citySuppliers[cityKey];
        const filterDisabled = currentMaterialType === DEFAULT_MATERIAL_TYPE;
        const supplierHasCurrentMaterialType = suppliers?.some((s) => s.material_type === currentMaterialType)

        if (suppliers && (filterDisabled || supplierHasCurrentMaterialType)) {
            style.fillColor = STROKE_COLOR;

            /*
                Aplica uma cor específica ao preenchimento
                com base no tipo atual de material.
            */
            switch (currentMaterialType) {
                case "Carvão Vegetal":
                    style.fillColor = GREEN_COLOR;
                    break;
                case "Minério de Ferro":
                    style.fillColor = ORANGE_COLOR;
                    break;
                case "Todos":
                    style.fillColor = ORANGE_COLOR;
            }
        }

        /*
            Se a cidade possui fornecedores, mas nenhuma cor foi atribuída,
            usa uma cor de preenchimento para indicar inatividade.
        */
        if (suppliers && style.fillColor === FILL_COLOR) {
            style.fillColor = "var(--off)";
        }

        this.styleCache.set(cacheKey, style);
        return style;
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
            this.currentStateCode = stateCode;

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

                const notInSatelliteMode = !this.satelliteMode;
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
                        supplierService.openDetails(cityKey, this.currentMaterialType);
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

    setCurrentMaterialType(type: string) {
        this.currentMaterialType = type;
        this.updateGeoJSONStyle();
    }

    setCitySuppliers(suppliers: CitySuppliers) {
        this.citySuppliers = suppliers;
    }
}

export { MapService };
