import L from "leaflet";

export interface Coordinates {
    lat: number;
    lng: number;
}

export interface StateCodeMapping {
    [key: string]: number;
}

export interface Cache {
    geojson: Map<string, any>;
    suppliers: null | any;
    currentLayer: null | L.Layer;
}

export interface State {
    name: string;
    abbr: string;
}

export interface City {
    name: string;
}

export interface Document {
    document: string;
    filepath?: string;
    validity?: string;
    status: string;
    type: string;
}

export interface Supplier {
    corporate_name: string;
    city: City;
    state: State;
    cpf_cnpj: string;
    material_type: string;
    distance_in_meters: number | null;
    rating: number;
    documents: Document[];
}

export interface CitySuppliers {
    [key: string]: Supplier[];
}
