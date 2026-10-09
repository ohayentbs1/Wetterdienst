const chartDataElement = document.getElementById('weather-chart-data');
const chartCanvas = document.getElementById('weather-chart');

if (chartDataElement && chartCanvas) {
    const chartData = JSON.parse(chartDataElement.textContent);
    const colors = [
        '#38bdf8', '#fb7185', '#4ade80', '#facc15', '#c084fc',
        '#2dd4bf', '#fb923c', '#818cf8', '#f472b6', '#a3e635',
        '#22d3ee', '#e879f9', '#f87171'
    ];

    new Chart(chartCanvas, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: chartData.datasets.map((dataset, index) => ({
                ...dataset,
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length],
                pointRadius: 1,
                tension: 0.2
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#e2e8f0'
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Tag',
                        color: '#cbd5e1'
                    },
                    ticks: {
                        color: '#94a3b8',
                        maxTicksLimit: 14
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Messwert (Einheit je Linie)',
                        color: '#cbd5e1'
                    },
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}
