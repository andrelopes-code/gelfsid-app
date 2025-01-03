document.addEventListener("DOMContentLoaded", function () {
    /*
        Script para ajustar o tamanho dos
        gráficos ao redimensionar a janela
    */
    let resizeTimeout;

    function resizeCharts() {
        const chartContainers = document.querySelectorAll(".plotly-chart");
        chartContainers.forEach((chartContainer) => {
            Plotly.Plots.resize(chartContainer);
        });
    }

    window.addEventListener("resize", function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function () {
            resizeCharts();
        }, 200);
    });

    /*
        Event listener que escuta eventos
        de submit para os forms de filtro
    */
    async function updateChart(chartId, formData) {
        // Transforma os dados do form em parâmetros de URL
        const urlParams = new URLSearchParams();
        formData.forEach((value, key) => {
            urlParams.append(key, value);
        });

        const chartContainer = document.getElementById(chartId);

        try {
            const response = await fetch(`${updateChartUrl}?chart_id=${chartId}&${urlParams.toString()}`, {
                method: "GET",
            });
            if (response.ok) {
                const data = await response.json();
                const chartContainer = document.getElementById(chartId);

                if (data.chart_data) {
                    // Garante que qualquer html existente
                    // seja removido antes do novo gráfico
                    // ser adicionado ao container
                    chartContainer.innerHTML = "";

                    try {
                        const updatedChart = JSON.parse(data.chart_data);

                        const plotlyConfig = {
                            displayModeBar: false,
                            showTips: false,
                        };

                        // IMPORTANTE: Plotly.purge para limpar o container antes
                        // de adicionar o novo gráfico, para limpar qualquer resto
                        // de html anterior (os que não foram adicionados pelo plotly)
                        Plotly.purge(chartContainer);

                        Plotly.react(chartContainer, updatedChart.data, updatedChart.layout, plotlyConfig);
                        Plotly.relayout(chartContainer, {
                            autosize: true,
                        });

                        Plotly.Plots.resize(chartContainer);
                    } catch {
                        chartContainer.innerHTML = data.chart_data;
                    }
                }
            }
        } catch (e) {
            console.error(e);
        }
    }

    document.addEventListener("submit", async function (e) {
        e.preventDefault();

        const form = e.target;
        const filterID = form.getAttribute("id");
        const chartElements = document.querySelectorAll(`.plotly-chart[data-related-form="${filterID}"]`);

        for (const ce of chartElements) {
            const chartID = ce?.id;
            if (chartID) {
                updateChart(chartID, new FormData(form));
            }
        }
    });

    /*
        Garantir que o ajuste do gráfico também seja feito após o carregamento de novos dados via HTMX
    */
    document.body.addEventListener("htmx:afterSwap", function (event) {
        resizeCharts();
    });
});
