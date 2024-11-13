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

    fileServerBaseUrl: string;
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

export interface LicencaAmbiental {
    documento: string;
    hyperlink: string;
    validade: string;
    status: string;
}

export interface CadastroTecnicoFederal {
    documento: string;
    hyperlink: string;
    validade: string;
    status: string;
}

export interface RegistroIEF {
    documento: string;
    hyperlink: string;
    validade: string;
    status: string;
}

export interface Supplier {
    razao_social: string;
    cidade: City;
    estado: State;
    cpf_cnpj: string;
    tipo_material: string;
    licenca_ambiental: LicencaAmbiental | null;
    cadastro_tecnico_federal: CadastroTecnicoFederal | null;
    registro_ief: RegistroIEF | null;
    distancia_em_metros: number | null;
    avaliacao: number;
}

export interface CitySuppliers {
    [key: string]: Supplier[];
}
