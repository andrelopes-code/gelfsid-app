import { CitySuppliers } from "./types";
import { getRandomPastelColor } from "./utils";
import {
    WEAK_STROKE_COLOR,
    FILL_COLOR,
    STROKE_COLOR,
    GREEN_COLOR,
    ORANGE_COLOR,
    DEFAULT_MATERIAL_TYPE,
} from "./constants";

export class StyleService {
    private styleCache = new Map<string, L.PathOptions>();

    getCityStyle(cityKey: string, currentMaterialType: string | null, citySuppliers: CitySuppliers) {
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
        const suppliers = citySuppliers[cityKey];
        const filterDisabled = currentMaterialType === DEFAULT_MATERIAL_TYPE;
        const supplierHasCurrentMaterialType = suppliers?.some(
            (s) => s.material_type === currentMaterialType
        );

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
}