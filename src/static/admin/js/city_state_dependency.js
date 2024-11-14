const DEFAULT_OPTION = '<option value="">Select</option>';

async function checkUpdate(citySelect) {
    const url = window.location.href;
    const updating = url.match(/\d+\/change/);

    if (updating) {
        const supplierID = updating[0].split("/")[0];
        const response = await fetch(`/supplier?id=${supplierID}`);

        if (!response.ok) {
            console.error("error loading supplier:", response.statusText);
            return;
        }

        const data = await response.json();
        citySelect.value = String(data.city.id);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const stateSelect = document.querySelector('select[name="state"]');
    const citySelect = document.querySelector('select[name="city"]');

    if (stateSelect && citySelect) {
        citySelect.disabled = !stateSelect.value;

        async function loadCities(stateID) {
            if (!stateID) {
                citySelect.innerHTML = DEFAULT_OPTION;
                citySelect.disabled = true;
                return;
            }

            try {
                const response = await fetch(`/cities/?state=${stateID}`);
                const cities = await response.json();

                citySelect.innerHTML = DEFAULT_OPTION;
                cities.forEach((city) => {
                    const option = document.createElement("option");
                    option.value = city.id;
                    option.textContent = city.name;
                    citySelect.appendChild(option);
                });

                citySelect.disabled = false;
            } catch (error) {
                console.error("error loading cities:", error);
                citySelect.disabled = true;
            }

            checkUpdate(citySelect);
        }

        stateSelect.onchange = (event) => {
            loadCities(event.target.value);
        };

        if (stateSelect.value) {
            loadCities(stateSelect.value);
        }
    }
});
