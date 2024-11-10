// supplierService.ts
import type { Supplier, CitySuppliers } from "./types";
import {
    STATE_CODE_MAP,
    CONFIG,
    CARV_TYPE,
    CARV_COLOR,
    MINE_COLOR,
    GOOD_RATING_COLOR,
    BAD_RATING_COLOR,
} from "./constants";

class SupplierService {
    async loadSuppliers(): Promise<CitySuppliers> {
        const response = await fetch(CONFIG.api.suppliers);
        const supplierData: Supplier[] = await response.json();

        const suppliers: CitySuppliers = {};
        for (const supplier of supplierData) {
            const cityKey = this.getCityKey(STATE_CODE_MAP[supplier.estado.sigla], supplier.cidade.nome);
            if (!suppliers[cityKey]) {
                suppliers[cityKey] = [];
            }
            suppliers[cityKey].push(supplier);
        }

        return suppliers;
    }

    generateSupplierCards(suppliers: Supplier[]): void {
        const container = document.getElementById("supplier-cards-container");
        if (!container) return;
        container.innerHTML = "";

        const template = document.getElementById("supplier-card-template") as HTMLElement;
        if (!template) return;

        suppliers.forEach((supplier) => {
            const card = template.cloneNode(true) as HTMLElement;
            const fields = card.querySelectorAll(".field");

            if (fields[0]) fields[0].textContent = supplier.razao_social;
            if (fields[1]) fields[1].textContent = `${supplier.cidade.nome} - ${supplier.estado.nome}`;
            if (fields[2]) fields[2].textContent = supplier.cnpj;
            if (fields[3]) fields[3].textContent = supplier.tipo_material;
            if (fields[4]) fields[4].textContent = supplier.licenca_operacao;
            if (fields[5])
                fields[5].textContent = supplier.certificacao_ambiental
                    ? "Com Licença Ambiental"
                    : "Sem Licença Ambiental";
            if (fields[6])
                fields[6].textContent =
                    supplier.distancia_em_metros !== null
                        ? `${supplier.distancia_em_metros / 1000} km`
                        : "N/A";

            const cardElement = card.querySelector("#card") as HTMLElement;
            if (cardElement) {
                cardElement.style.borderColor =
                    supplier.tipo_material === CARV_TYPE ? CARV_COLOR : MINE_COLOR;
            }

            const ratingDiv = card.querySelector("#supplier-rating") as HTMLElement;
            if (ratingDiv) {
                ratingDiv.style.color = supplier.avaliacao > 80 ? GOOD_RATING_COLOR : BAD_RATING_COLOR;

                const ratingField = ratingDiv.querySelector(".field");
                if (ratingField) {
                    ratingField.textContent = supplier.avaliacao.toString();
                }
            }

            container.appendChild(card);
        });
    }

    openDetails(cityKey: string): void {
        const suppliers = this.citySuppliers[cityKey];
        if (!suppliers) return;

        const detailsTitle = document.querySelector("#details-title");
        const detailsElement = document.getElementById("details");

        if (detailsTitle) {
            detailsTitle.textContent = suppliers[0].cidade.nome;
        }

        this.generateSupplierCards(suppliers);

        if (detailsElement) {
            detailsElement.classList.remove("translate-x-full");
            detailsElement.classList.add("translate-x-0");
        }
    }

    closeDetails(): void {
        const detailsElement = document.getElementById("details");
        if (detailsElement) {
            detailsElement.classList.remove("translate-x-0");
            detailsElement.classList.add("translate-x-full");
        }
    }

    private getCityKey(stateCode: number, cityName: string): string {
        return `${stateCode}-${cityName}`;
    }

    private citySuppliers: CitySuppliers = {};

    setCitySuppliers(suppliers: CitySuppliers): void {
        this.citySuppliers = suppliers;
    }
}

export const supplierService = new SupplierService();
