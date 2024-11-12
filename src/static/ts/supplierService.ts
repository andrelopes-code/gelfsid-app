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
import { SupplierCard } from "./components/supplierCard";

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
            console.log(supplier);
            suppliers[cityKey].push(supplier);
        }

        return suppliers;
    }

    generateSupplierCards(suppliers: Supplier[]): void {
        const container = document.getElementById("supplier-cards-container");
        if (!container) return;
        container.innerHTML = "";

        suppliers.forEach((supplier) => {
            const newCard = document.createElement("div");
            newCard.innerHTML = SupplierCard(
                supplier,
                supplier.tipo_material === CARV_TYPE ? CARV_COLOR : MINE_COLOR,
                supplier.avaliacao > 80 ? GOOD_RATING_COLOR : BAD_RATING_COLOR
            );
            container.appendChild(newCard);
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
