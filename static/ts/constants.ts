import type { StateCodeMapping } from "./types";

interface GeoJsonConfig {
    states: string;
    cities: string;
}

interface ApiConfig {
    suppliers: string;
}

interface AppConfig {
    geojson: GeoJsonConfig;
    api: ApiConfig;
}

export const APP_CONFIG: AppConfig = {
    geojson: {
        states: "static/data/geojson/br_states.json",
        cities: "static/data/geojson/geojs-{uf}-mun.json",
    },
    api: {
        suppliers: "/api/suppliers/",
    },
};

export const DEFAULT_MATERIAL_TYPE = "Todos";
export const BRAZIL_COORDINATES: [number, number] = [-14.235, -51.925];
export const HOST_CITY_COORDINATES = [-19.4457253885, -44.2600188074];
export const HOST_CITY_TOOLTIP_TEXT = "GELF Sete Lagoas";
export const HOST_CITY_KEY = "31-Sete Lagoas";
export const html = String.raw;

export const FILL_COLOR = "var(--fill-color)";
export const STROKE_COLOR = "var(--stroke-color)";
export const WEAK_STROKE_COLOR = "var(--weak-stroke-color)";
export const ORANGE_COLOR = "var(--primary-color)";
export const GREEN_COLOR = "var(--secondary-color)";
export const DEFAULT_COLOR = "var(--off)";

export const GOOD_RATING_COLOR = GREEN_COLOR;
export const BAD_RATING_COLOR = ORANGE_COLOR;

export const STATE_CODE_MAP: StateCodeMapping = {
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
