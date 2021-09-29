function drawChart(canvas, xdata, ydata, params) {
    const ctx = document.getElementById(canvas).getContext('2d');

    const myChart = new Chart(ctx, {
        type: params.type ? params.type : 'line',
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
            },
            errorBarColor: "rgba(" + (params.color ? params.color : [255, 99, 132]) + ", 1.0)",
            errorBarWhiskerColor: "rgba(" + (params.color ? params.color : [255, 99, 132]) + ", 1.0)",
            errorBarLineWidth: 1,
            errorBarWhiskerLineWidth: 1,
            errorBarWhiskerSize: 10,
        }
    });
}

function loadData(filename, scale) {
    scale = scale ? parseFloat(scale) : 1.0
    return fetch(filename).then((data) => (data.text()))
        .then(function(text) {
            lines = text.split("\n");
            x = []; y = [];
            for (i in lines) {
                line = lines[i];
                if (line) {
                    split_line = line.split(" ");
                    x.push(split_line[0])
                    y.push(parseFloat(split_line[1])*scale)
                }
            }
            return {x, y}
        });
}

function round(x, n=2) {
    b = 10**2
    return Math.round((x + Number.EPSILON) * b) / b
}

function loadDataWithErrorBars(filename, scale) {
    scale = scale ? parseFloat(scale) : 1.0
    return fetch(filename).then((data) => (data.text()))
        .then(function(text) {
            lines = text.split("\n");
            x = []; y = [];
            for (i in lines) {
                line = lines[i];
                if (line) {
                    split_line = line.split(" ");
                    x.push(split_line[0])
                    value = parseFloat(split_line[1])*scale
                    plus = parseFloat(split_line[2])*scale
                    minus = parseFloat(split_line[3])*scale
                    y.push({y: round(value, 2), yMax: round(value+plus, 2), yMin: round(value-minus, 2)})
                }
            }
            return {x, y}
        });
}
