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
    name: string;
    filepath?: string;
    validity?: string;
    type: string;
}

export interface Supplier {
    id: number;
    corporate_name: string;
    city: City;
    state: State;
    cpf_cnpj: string;
    material_type: string;
    distance_in_meters: number | null;
    rating: number;
    documents: Document[];
    charcoal_recent_stats: {
        period: string;
        average_moisture: number;
        average_fines: number;
        average_density: number;
        count: number;
    } | null;
}

export interface CitySuppliers {
    [key: string]: Supplier[];
}
