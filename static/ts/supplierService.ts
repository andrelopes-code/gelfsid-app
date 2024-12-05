import type { Supplier, CitySuppliers } from "./types";
import { STATE_CODE_MAP, APP_CONFIG, GREEN_COLOR, ORANGE_COLOR, STROKE_COLOR } from "./constants";
import { SupplierCard } from "./components/supplierCard";
import { getCityKey } from "./utils";

class SupplierService {
    private citySuppliers: CitySuppliers = {};
    public supplierData: Supplier[] = [];
    public materialTypes: Set<string> = new Set();

    async loadCitySuppliers() {
        const response = await fetch(APP_CONFIG.api.suppliers);
        this.supplierData = await response.json();

        const suppliers: CitySuppliers = {};

        // Percorre todos os fornecedores para formar
        // a lista de fornecedores por município
        for (const supplier of this.supplierData) {
            // Adiciona o tipo de material no Set() de materiais
            this.materialTypes.add(supplier.material_type);

            const cityKey = getCityKey(STATE_CODE_MAP[supplier.state.abbr], supplier.city.name);
            if (!suppliers[cityKey]) {
                suppliers[cityKey] = [];
            }
            suppliers[cityKey].push(supplier);
        }

        return suppliers;
    }

    generateSupplierCards(suppliers: Supplier[]) {
        const container = document.getElementById("supplier-cards-container");
        if (!container) return;
        container.innerHTML = "";

        suppliers.forEach((supplier) => {
            const newCard = document.createElement("div");
            newCard.classList.add("w-full", "h-fit");

            let borderColor = STROKE_COLOR;

            switch (supplier.material_type) {
                case "Carvão Vegetal":
                    borderColor = GREEN_COLOR;
                    break;

                case "Minério de Ferro":
                    borderColor = ORANGE_COLOR;
                    break;
            }

            newCard.style.borderColor = borderColor;

            newCard.innerHTML = SupplierCard(
                supplier,
                borderColor,
                supplier.rating > 80 ? GREEN_COLOR : ORANGE_COLOR
            );
            container.appendChild(newCard);
        });
    }

    openDetails(cityKey: string, currentType: string | null) {
        let suppliers = this.citySuppliers[cityKey];
        if (!suppliers) return;

        const detailsTitle = document.querySelector("#details-title");
        const detailsElement = document.getElementById("details");

        if (detailsTitle) {
            detailsTitle.textContent = suppliers[0].city.name;
        }

        this.generateSupplierCards(suppliers);

        if (detailsElement) {
            detailsElement.classList.remove("translate-x-full");
            detailsElement.classList.add("translate-x-0");
        }
    }

    closeDetails() {
        const detailsElement = document.getElementById("details");
        if (detailsElement) {
            detailsElement.classList.remove("translate-x-0");
            detailsElement.classList.add("translate-x-full");
        }
    }

    setCitySuppliers(suppliers: CitySuppliers) {
        this.citySuppliers = suppliers;
    }
}

export const supplierService = new SupplierService();
