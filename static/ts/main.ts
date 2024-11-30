import { CONFIG, DEFAULT_MATERIAL_TYPE, html } from "./constants";
import { MapService } from "./mapService";
import { supplierService } from "./supplierService";

class App {
    private mapService: MapService;

    constructor() {
        this.mapService = new MapService();
        this.mapService.setCurrentType(DEFAULT_MATERIAL_TYPE);
    }

    async setupFilter() {
        const filter = document.getElementById("material-filter") as HTMLInputElement;

        const response = await fetch(CONFIG.api.materials);
        const materials = await response.json();
        materials.unshift(DEFAULT_MATERIAL_TYPE);

        const eventHandler = (e: MouseEvent) => {
            const allOptions = filter.querySelectorAll(".material-filter-option");
            const option = e.target as HTMLElement;

            allOptions.forEach((opt) => opt.classList.remove("active-material"));
            option.classList.add("active-material");

            const value = option.getAttribute("data-value");
            if (value) {
                this.mapService.setCurrentType(value);
            }
        };

        for (const material of materials) {
            const option = document.createElement("div");
            option.classList.add("hover:text-slate-500", "material-filter-option");
            option.setAttribute("data-value", material);
            option.textContent = material;

            if (material === DEFAULT_MATERIAL_TYPE) {
                option.classList.add("active-material");
            }

            option.addEventListener("click", eventHandler);
            filter.appendChild(option);
        }
    }

    private async configureEventListeners(): Promise<void> {
        this.setupFilter();

        const closeDetails = document.getElementById("close-details") as HTMLElement;

        closeDetails.addEventListener("click", () => {
            supplierService.closeDetails();
        });
    }

    private hideLoader(): void {
        const loader = document.getElementById("main-loader") as HTMLElement;
        loader.style.display = "none";
    }

    async init(): Promise<void> {
        try {
            await this.configureEventListeners();

            const suppliers = await supplierService.loadSuppliers();
            this.mapService.setCitySuppliers(suppliers);
            supplierService.setCitySuppliers(suppliers);
            await this.mapService.loadStates();
            await this.mapService.preloadCities();

            this.hideLoader();
        } catch (error) {
            console.error("error:", error);
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const app = new App();
    app.init();
});
