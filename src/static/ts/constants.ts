import type { Config, StateCodeMapping } from "./types";

export const BRAZIL_COORDINATES: [number, number] = [-14.235, -51.925];
export const HOST_CITY_KEY = "31-Sete Lagoas";
export const FILL_COLOR = "#151b2500";
export const STROKE_COLOR = "#4b5260";

export const CARV_TYPE = "Carvão Vegetal";
export const MINE_TYPE = "Minério";
export const MINE_COLOR = "var(--highlight)";
export const CARV_COLOR = "var(--green-highlight)";

export const GOOD_RATING_COLOR = CARV_COLOR;
export const BAD_RATING_COLOR = MINE_COLOR;

export const html = String.raw;

export const CONFIG: Config = {
    geojson: {
        states: "static/data/geojson/br_states.json",
        cities: "static/data/geojson/mun/geojs-{uf}-mun.json",
    },
    api: {
        suppliers: "http://localhost:8000/fornecedores/",
    },
    fileServerBaseUrl: "http://localhost:8080",
};

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
