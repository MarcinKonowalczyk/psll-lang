function drawChart(canvas, xdata, ydata, params) {
    const ctx = document.getElementById(canvas).getContext('2d');

    const myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: xdata,
            datasets: [{
                label: params.ylabel,
                data: ydata,
                backgroundColor: "rgba(" + (params.color ? params.color : [255, 99, 132]) + ",0.2)",
                borderColor:  "rgba(" + (params.color ? params.color : [255, 99, 132]) + ",1.0)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            resizeDelay: 10,
            fill: true,
            scales: {
                y: {
                    title: {
                        display: params.ylabel,
                        text: params.ylabel
                    }
                },
                x: {
                    ticks: {
                        callback: function(value, index, values) {
                            return xdata[index].substring(0,7);
                        }
                    },
                    title: {
                        display: true,
                        text: params.xlabel ? params.xlabel : "commit hash"
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    caretPadding: 10
                }
            },
            elements: {
                point: {
                    radius: 3,
                    hoverRadius: 5,
                    hitRadius: 20
                }
            }
        }
    });
}

function load_data(filename) {
    return fetch(filename).then((data) => (data.text()))
        .then(function(text) {
            lines = text.split("\n");
            x = []; y = [];
            for (i in lines) {
                split_line = lines[i].split(" ");
                x.push(split_line[0])
                y.push(parseFloat(split_line[1]))
            }
            return {x, y}
        });
}