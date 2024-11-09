const DEFAULT_OPTION = '<option value="">---------</option>';

document.addEventListener("DOMContentLoaded", function () {
    const estadoSelect = document.querySelector('select[name="estado"]');
    const cidadeSelect = document.querySelector('select[name="cidade"]');

    if (estadoSelect && cidadeSelect) {
        cidadeSelect.disabled = !estadoSelect.value;

        async function carregarCidades(estadoId) {
            if (!estadoId) {
                cidadeSelect.innerHTML = DEFAULT_OPTION;
                cidadeSelect.disabled = true;
                return;
            }

            try {
                const response = await fetch(`/cidades/?estado=${estadoId}`);
                const cidades = await response.json();

                cidadeSelect.innerHTML = DEFAULT_OPTION;
                cidades.forEach((cidade) => {
                    const option = document.createElement("option");
                    option.value = cidade.id;
                    option.textContent = cidade.nome;
                    cidadeSelect.appendChild(option);
                });

                cidadeSelect.disabled = false;
            } catch (error) {
                console.error("Erro ao carregar cidades:", error);
                cidadeSelect.disabled = true;
            }

            checkUpdate(cidadeSelect);
        }

        estadoSelect.onchange = (event) => {
            carregarCidades(event.target.value);
        };

        if (estadoSelect.value) {
            carregarCidades(estadoSelect.value);
        }
    }
});

async function checkUpdate(cidadeSelect) {
    const url = window.location.href;
    const updating = url.match(/\d+\/change/);

    if (updating) {
        const fornecedor_id = updating[0].split("/")[0];
        const response = await fetch(`/fornecedor?id=${fornecedor_id}`);
        if (!response.ok) {
            console.error("Erro ao buscar dados do fornecedor");
            return;
        }

        const data = await response.json();
        cidadeSelect.value = String(data.cidade.id);
    }
}
