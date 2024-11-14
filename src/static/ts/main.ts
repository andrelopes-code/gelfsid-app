import { CARV_TYPE, MINE_TYPE } from "./constants";
import { MapService } from "./mapService";
import { supplierService } from "./supplierService";

class App {
    private mapService: MapService;

    constructor() {
        this.mapService = new MapService(CARV_TYPE);
    }

    private async configureEventListeners(): Promise<void> {
        const filter = document.getElementById("filter") as HTMLInputElement;
        if (!filter) {
            throw new Error("filter element not found");
        }

        filter.addEventListener("change", () => {
            if (filter.checked) {
                this.mapService.setCurrentType(MINE_TYPE);
                document.documentElement.style.setProperty("--material", "#d68367");
            } else {
                this.mapService.setCurrentType(CARV_TYPE);
                document.documentElement.style.setProperty("--material", "#98e089");
            }
        });

        const closeDetails = document.getElementById("close-details") as HTMLElement;
        if (!closeDetails) {
            throw new Error("Close Details element not found");
        }

        closeDetails.addEventListener("click", () => {
            supplierService.closeDetails();
        });
    }

    private hideLoader(): void {
        const loader = document.getElementById("main-loader") as HTMLElement;
        if (!loader) {
            throw new Error("Loader element not found");
        }

        loader.style.display = "none";
    }

    async init(): Promise<void> {
        try {
            await this.configureEventListeners();

            const suppliers = await supplierService.loadSuppliers();
            this.mapService.setCitySuppliers(suppliers);
            supplierService.setCitySuppliers(suppliers);

            await this.mapService.loadStates();

            this.hideLoader();

            await this.mapService.preloadCities();
        } catch (error) {
            console.error("error:", error);
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const app = new App();
    app.init();
});
