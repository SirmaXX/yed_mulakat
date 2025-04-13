<script>
    import { tick } from "svelte";
    import Chart from "chart.js/auto";

    let chart;
    let chartCanvas;
    let batteryData = [];
    let selectedBattery = "05";
    let xAxis = "time";
    let yAxes = ["current_measured"];
    let error = null;

    const availableFields = [
        "time",
        "cycle",
        "capacity",
        "voltage_measured",
        "current_measured",
        "temperature_measured",
        "current_load",
        "voltage_load",
    ];

    async function fetchAndDraw() {
        error = null;
        try {
            const res = await fetch(
                `http://localhost:8000/api/data/${selectedBattery}`,
            );
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            // sort by x-axis field (time or cycle)
            batteryData = data.sort((a, b) => a[xAxis] - b[xAxis]);
            await tick();
            drawChart();
        } catch (err) {
            error = err.message;
            console.error("Veri çekme hatası:", err);
        }
    }

    function drawChart() {
        if (!batteryData.length || !xAxis || !yAxes.length) return;

        const labels = batteryData.map((row) => row[xAxis]);
        const datasets = yAxes.map((y) => ({
            label: y,
            data: batteryData.map((row) => row[y]),
            borderColor: getRandomColor(),
            fill: false,
        }));

        if (chart) chart.destroy();

        chart = new Chart(chartCanvas, {
            type: "line",
            data: { labels, datasets },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        mode: "index",
                        intersect: false,
                    },
                    legend: {
                        display: true,
                        position: "top",
                    },
                },
                interaction: {
                    mode: "nearest",
                    axis: "x",
                    intersect: false,
                },
                scales: {
                    x: {
                        title: { display: true, text: xAxis },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 30,
                            autoSkip: true,
                            maxTicksLimit: 20,
                        },
                    },
                    y: {
                        title: { display: true, text: "Değer" },
                        suggestedMin: -2,
                        suggestedMax: 2,
                    },
                },
            },
        });
    }

    function getRandomColor() {
        const colors = [
            "red",
            "blue",
            "green",
            "orange",
            "purple",
            "cyan",
            "black",
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }
</script>

<div class="container mt-4">
    <h2>Batarya Zaman Serisi</h2>

    <div class="form-group mb-2">
        <label>Batarya Seç:</label>
        <select bind:value={selectedBattery} class="form-select">
            <option value="05">Batarya 5</option>
            <option value="06">Batarya 6</option>
            <option value="18">Batarya 18</option>
        </select>

        <label class="mt-2">X Ekseni (Zaman):</label>
        <select bind:value={xAxis} class="form-select">
            {#each availableFields as field}
                <option value={field}>{field}</option>
            {/each}
        </select>

        <label class="mt-2">Y Ekseni (Görselleştirilecek Değişkenler):</label>
        <select bind:value={yAxes} multiple class="form-select">
            {#each availableFields.filter((f) => f !== xAxis) as field}
                <option value={field}>{field}</option>
            {/each}
        </select>

        <button class="btn btn-primary mt-3" on:click={fetchAndDraw}
            >Grafiği Çiz</button
        >
    </div>

    {#if error}
        <div class="alert alert-danger mt-2">Hata: {error}</div>
    {/if}

    <canvas bind:this={chartCanvas} class="mt-4"></canvas>
</div>

<style>
    canvas {
        max-width: 100%;
    }
</style>
