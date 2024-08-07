// script.js

// Initialize the Chart.js line chart
const ctx = document.getElementById('myLineChart').getContext('2d');
const datafile_fully = "results/2024_07_13/fully/post_process/mean_perfs.csv";
const datafile_dynamic = "results/2024_07_13/dynamic/post_process/mean_perfs.csv";
let linePlotInitialized = false;
let index = 0; // Start index for data points
let dataSets = [];


const myLineChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // X-axis labels
        datasets: [
            {
                label: 'Fully-connected',
                data: [], // Data points from the first CSV
                borderColor: '#ff7979',
                backgroundColor: '#ff7979',
                fill: false,
                lineTension: 0.1
            },
            {
                label: 'Dynamic',
                data: [], // Data points from the second CSV
                borderColor: "#6ab04c",
                backgroundColor: "#6ab04c",
                fill: false,
                lineTension: 0.1
            }
        ]
    },
    options: {
        responsive: true,
        animation: {
            duration: 0 // Disable default animation for manual control
        },
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 22 // Increase font size of legend labels
                    }
                }
            }
        },
        scales: {
            x: {
                type: 'linear',
                position: 'bottom',
                title: {
                    display: true,
                    text: 'Crafting step', // Label for x-axis
                    color: '#000000', // Color of the label
                    font: {
                        size: 22 // Font size of the x-axis label
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Group inventory size', // Label for y-axis
                    color: '#000000', // Color of the label
                    font: {
                        size: 22 // Font size of the y-axis label
                    }
                }
            }
        }
    }
});

// Function to parse single-column CSV data
function parseCSVData(csv) {
    const lines = csv.trim().split('\n');
    const data = [];

    // Iterate through each line and parse data
    for (let i = 0; i < lines.length; i++) {
        const value = parseFloat(lines[i].trim());
        if (!isNaN(value)) {
            data.push({ x: i, y: value }); // Store data as { x, y }
        }
    }

    return data;
}

function updateChart() {
    for (let datasetIndex = 0; datasetIndex < myLineChart.data.datasets.length; datasetIndex++) {
        let data = dataSets[datasetIndex];
        if (index >= data.length)
            return;
        myLineChart.data.datasets[datasetIndex].data.push(data[index]);
        myLineChart.data.labels.push(data[index].x); // Optionally update x-axis labels
        myLineChart.update();
    }
    index++;
}

// Fetch and parse both CSV files, then start gradual update
function fetchAndUpdateCharts() {
    // Fetch data from the first CSV file
    fetch(datafile_fully)
        .then(response => response.text())
        .then(csv => {
            const data1 = parseCSVData(csv);

            // Fetch data from the second CSV file
            fetch(datafile_dynamic)
                .then(response => response.text())
                .then(csv => {
                    const data2 = parseCSVData(csv);
                    dataSets = [data1, data2];
                    linePlotInitialized = true;
                })
                .catch(error => {
                    console.error('Error loading second CSV file:', error);
                });
        })
        .catch(error => {
            console.error('Error loading first CSV file:', error);
        });
}

// Call the function to fetch and update the chart
fetchAndUpdateCharts();

document.addEventListener('plotUpdateEvent', function (event) {
    updateChart();
});
