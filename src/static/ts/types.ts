import L from "leaflet";

export interface Coordinates {
    lat: number;
    lng: number;
}

export interface StateCodeMapping {
    [key: string]: number;
}

export interface Config {
    geojson: {
        states: string;
        cities: string;
    };
    api: {
        suppliers: string;
    };
}

export interface Cache {
    geojson: Map<string, any>;
    suppliers: null | any;
    currentLayer: null | L.Layer;
}

export interface State {
    nome: string;
    sigla: string;
}

export interface City {
    nome: string;
}

export interface Supplier {
    razao_social: string;
    cidade: City;
    estado: State;
    cnpj: string;
    tipo_material: string;
    licenca: string;
    cadastro_tecnico_federal: string;
    registro_ief: string;
    distancia_em_metros: number | null;
    avaliacao: number;
}

export interface CitySuppliers {
    [key: string]: Supplier[];
}