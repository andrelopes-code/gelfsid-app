import "leaflet/dist/leaflet.css";
import { DEFAULT_MATERIAL_TYPE } from "./constants";
import { MapService } from "./mapService";
import { supplierService } from "./supplierService";

class App {
    private mapService: MapService;

    constructor() {
        this.mapService = new MapService();
        this.mapService.setActiveMaterialType(DEFAULT_MATERIAL_TYPE);
    }

    private async initializeFilter(materialTypes: Set<string>) {
        const filter = document.getElementById("material-filter") as HTMLElement;
        const filterContentElem = filter.querySelector(".material-filter-content") as HTMLElement;
        const materials = Array.from(materialTypes);

        // Adiciona o material padrão ao inicio da lista
        materials.unshift(DEFAULT_MATERIAL_TYPE);

        for (const material of materials) {
            const option = document.createElement("div");

            option.classList.add("hover:text-slate-500", "material-filter-option");
            option.setAttribute("data-value", material);
            option.textContent = material;

            if (material === DEFAULT_MATERIAL_TYPE) {
                option.classList.add("active-material");
            }

            option.addEventListener("click", (e: MouseEvent) => {
                const allOptions = filter.querySelectorAll(".material-filter-option");
                const selectedOption = e.target as HTMLElement;

                // Remove a opção anteriormente ativa e adiciona a que foi clicada
                allOptions.forEach((opt) => opt.classList.remove("active-material"));
                selectedOption.classList.add("active-material");

                // Atualiza o tipo de material atualmente filtrado ao mapService
                const value = selectedOption.getAttribute("data-value");
                if (value) {
                    this.mapService.setActiveMaterialType(value);
                }
            });

            filterContentElem.appendChild(option);
        }
    }

    private async initializeEventListeners() {
        // Adiciona um event listener para quando o botão de
        // fechar os detalhes de fornecedores for clicado
        const closeDetailsBtn = document.getElementById("close-details") as HTMLElement;
        closeDetailsBtn.addEventListener("click", () => {
            supplierService.closeDetails();
        });
    }

    private initializeShapefileSearchControls() {
        const searchElem = document.getElementById("shapes-search-controls") as HTMLInputElement;
        const nextBtn = searchElem.querySelector("#next-button") as HTMLButtonElement;
        const prevBtn = searchElem.querySelector("#prev-button") as HTMLButtonElement;

        nextBtn.addEventListener("click", () => {
            const input = searchElem.querySelector("input") as HTMLInputElement;

            this.mapService.searchShapefilesAndNavigate(input.value, "next");
        });

        prevBtn.addEventListener("click", () => {
            const input = searchElem.querySelector("input") as HTMLInputElement;
            this.mapService.searchShapefilesAndNavigate(input.value, "prev");
        });
    }

    private hideScreenLoader() {
        (document.getElementById("main-loader") as HTMLElement).style.display = "none";
    }

    async init() {
        try {
            await this.initializeEventListeners();

            const citySuppliers = await supplierService.loadCitySuppliers();

            this.mapService.setCitySuppliers(citySuppliers);
            supplierService.setCitySuppliers(citySuppliers);
            this.initializeFilter(supplierService.materialTypes);
            this.initializeShapefileSearchControls();

            this.mapService.preloadCities();
            this.mapService.loadStates();
            this.hideScreenLoader();
        } catch (error) {
            console.error("error:", error);
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const app = new App();
    app.init();
});
