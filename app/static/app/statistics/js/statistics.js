
var monthArr = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
};

var xaxisDates = ["1/1/2021", "1/2/2021", "1/3/2021", "1/4/2021", "1/5/2021", "1/6/2021", "1/7/2021", "1/8/2021", "1/9/2021", "1/10/2021",
    "1/11/2021", "1/12/2021", "1/13/2021", "1/14/2021", "1/15/2021", "1/16/2021", "1/17/2021", "1/18/2021", "1/19/2021", "1/20/2021",
    "1/21/2021", "1/22/2021", "1/23/2021", "1/24/2021", "1/25/2021", "1/26/2021", "1/27/2021", "1/28/2021", "1/29/2021", "1/30/2021", "1/31/2021"];

// dark blue #063951
// red #C13018
// orange #F36F13
// yellow #EBCB38
// green #A2B969
// lighblue #0D95BC
//["#1b2029", "#f39237", "#009688", "#992929", "#214e34", "#795548", "#3e657a", "#c13018"]
// var colorPallete = ['#063951', '#C13018', '#F36F13', '#0D95BC', '#EBCB38', '#A2B969'];
// var colorPallete = ["#1b2029", "#f39237", "#c13018", "#3e657a", "#214e34", "#795548", "#009688", "#992929"];
var colorPallete = ["#e53935", "#f39237", "#009688", "#4caf50", "#22577a"];

var ros = {
    usage: [
        { date: "1/2/2021", downloads: 2 },
        { date: "1/3/2021", downloads: 10 },
        { date: "1/4/2021", downloads: 11 },
        { date: "1/6/2021", downloads: 14 },
        { date: "1/8/2021", downloads: 20 },
        { date: "1/9/2021", downloads: 25 },
        { date: "1/10/2021", downloads: 40 },
        { date: "1/11/2021", downloads: 48 },
        { date: "1/12/2021", downloads: 50 },
        { date: "1/18/2021", downloads: 52 },
        { date: "1/28/2021", downloads: 53 }
    ],
    popularity: [
        { date: "1/2/2021", up: 52, down: 71 },
        { date: "1/3/2021", up: 13, down: 68 },
        { date: "1/4/2021", up: 50, down: 16 },
        { date: "1/6/2021", up: 26, down: 5 },
        { date: "1/10/2021", up: 95, down: 77 },
        { date: "1/11/2021", up: 75, down: 38 },
        { date: "1/13/2021", up: 45, down: 75 },
        { date: "1/14/2021", up: 64, down: 16 },
        { date: "1/15/2021", up: 61, down: 70 },
        { date: "1/19/2021", up: 73, down: 24 },
        { date: "1/20/2021", up: 42, down: 50 },
        { date: "1/21/2021", up: 92, down: 95 },
        { date: "1/22/2021", up: 23, down: 97 },
        { date: "1/23/2021", up: 21, down: 14 },
        { date: "1/24/2021", up: 86, down: 13 },
        { date: "1/25/2021", up: 47, down: 48 },
        { date: "1/26/2021", up: 67, down: 6 },
        { date: "1/27/2021", up: 4, down: 91 },
        { date: "1/28/2021", up: 83, down: 53 },
        { date: "1/30/2021", up: 73, down: 8 }
    ],
    runs_standard: [
        { date: "1/1/2021", cputime: 709.0, memory: 531.3 },
        { date: "1/2/2021", cputime: 748.3, memory: 690.0 },
        { date: "1/8/2021", cputime: 572.3, memory: 252.0 },
        { date: "1/15/2021", cputime: 317.6, memory: 278.1 },
        { date: "1/17/2021", cputime: 747.3, memory: 947.2 },
        { date: "1/18/2021", cputime: 822.6, memory: 470.2 },
        { date: "1/19/2021", cputime: 432.2, memory: 310.5 },
        { date: "1/20/2021", cputime: 449.9, memory: 660.8 },
        { date: "1/21/2021", cputime: 908.7, memory: 178.6 },
        { date: "1/22/2021", cputime: 924.6, memory: 209.3 },
        { date: "1/24/2021", cputime: 884.0, memory: 81.5 },
        { date: "1/25/2021", cputime: 200.6, memory: 139.8 },
        { date: "1/29/2021", cputime: 309.3, memory: 215.6 },
        { date: "1/30/2021", cputime: 152.1, memory: 933.4 },
        { date: "1/31/2021", cputime: 497.9, memory: 368.1 }
    ]
}
// Materialize Initializations
// Chips
// M.Chips.init(document.querySelectorAll('.chips'));

// RO Standard Multi Line Downloads
var rosDownloads = fun(xaxisDates, ros["usage"], "downloads", true);

// RO Standard Multi Line Upvotes
var rosUpvotes = fun(xaxisDates, ros["popularity"], "up", true);

// RO Standard Multi Line CPU Time
var rosCpuTime = fun(xaxisDates, ros["runs_standard"], "cputime", false);

// RO Standard Multi Line Memory
var rosMemory = fun(xaxisDates, ros["runs_standard"], "memory", false);

function fun(dates, data, dataname, keepSteadyByDate) {
    var arr = []
    var k = 0;
    for (var i = 0; i < dates.length && k < data.length; i++) {
        if (dates[i] == data[k]["date"]) {
            arr.push(data[k][dataname]);
            k += 1;
        }
        else if (k == 0) {
            if (keepSteadyByDate) {
                arr.push(0);
            }
            else {
                arr.push(null);
            }
        }
        else {
            if (keepSteadyByDate) {
                arr.push(data[k - 1][dataname]);
            }
            else {
                arr.push(null);
            }
        }
    }
    for (var l = i; l < dates.length; l++) {
        arr.push(data[data.length - 1][dataname]);
    }
    return arr;
}

// ------------------------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------------

function getCustomData(dataset_editor) {
    try {
        var dataset_editor_value = dataset_editor.getValue();
        dataset_editor_value = dataset_editor_value.replace(/\n/g, '');
        dataset_editor_value = dataset_editor_value.replace(/\t/g, '');
        dataset_editor_value = dataset_editor_value.replace(/\s/g, '');
    
        var labelsXaxis = dataset_editor_value.split('labels:[')[1].split('datasets:')[0].slice(0, -1).replace(/'/g, '').split(',');
        labelsXaxis = toInts(labelsXaxis);
    
        var datasetsStr = dataset_editor_value.split('labels:')[1].split('datasets:[')[1].slice(0, -2).split(/\{([^}]+)\}/g);
        var datasetsYaxis = [];
        for (var i = 1; i < datasetsStr.length; i+=2) {
            var type = datasetsStr[i].split("type:'")[1].split("'")[0];
            var label = datasetsStr[i].split("label:'")[1].split("'")[0];
            var data = datasetsStr[i].split("data:[")[1].slice(0, -1).replace(/'/g, '').split(',');
            data = toInts(data);
            var newDataset = {
                'type': type,
                'label': label,
                'data': data
            }
            datasetsYaxis.push(newDataset);
        }
        return {labelsXaxis: labelsXaxis, datasetsYaxis: datasetsYaxis};
    } catch(err) {
        generateToast('Error: Incorrect data was given', 'red lighten-2 black-text', 'stay on');
        return null;
    } 
}

function toInts (arr) {
    for (var i = 0; i < arr.length; i++) {
        if (!isNaN(arr[i])) {
            arr[i] = parseInt(arr[i]);
        }
        if (arr[i] == 'null') {
            arr[i] = null;
        }
    }
    return arr;
}

function formatCustomDataset (datasetsYaxis) {
    try {
        var currColorIndex = 0;
        var currDatasetId = 0;
        var newDatasets = [];
        var newyAxes = [];

        for (var i = 0; i < datasetsYaxis.length; i++) {
            var axisPosition;
            if ((i % 2) == 0) {
                axisPosition = 'left';
            }
            else {
                axisPosition = 'right';
            }

            var newDataset = {
                type: datasetsYaxis[i].type,
                yAxisID: 'axis' + currDatasetId,
                label: datasetsYaxis[i].label,
                borderColor: colorPallete[currColorIndex],
                backgroundColor: colorPallete[currColorIndex],
                borderWidth: 2,
                fill: false,
                data: datasetsYaxis[i].data
            }
            newDatasets.push(newDataset);

            var newyAxis = {
                type: 'linear',
                display: true,
                position: axisPosition,
                id: 'axis' + currDatasetId,
                scaleLabel: {
                    display: true,
                    labelString: datasetsYaxis[i].label,
                    fontColor: colorPallete[currColorIndex]
                },
                ticks: {
                    fontColor: colorPallete[currColorIndex]
                }
            }
            if (i != 0) {
                newyAxis.gridLines = {drawOnChartArea: false}
            }
            newyAxes.push(newyAxis);


            currDatasetId++;
            if ((currColorIndex + 1) >= colorPallete.length) {
                currColorIndex = 0;
            }
            else {
                currColorIndex++;
            }
        }
        return {newDatasets: newDatasets, newyAxes: newyAxes};
    } catch(err) {
        generateToast('An error occured', 'red lighten-2 black-text', 'stay on');
        return null;
    }  
}

function updateCustomChart (customChartVar, editorType) {
    try {
        var newData = null;
        if (editorType == 'tool') {
            newData = getCustomData(tool_dataset_editor);
        }
        else if (editorType == 'workflow') {
            newData = getCustomData(workflow_dataset_editor);
        }
        if (newData == null) {
            return;
        }
        var formattedDatasets = formatCustomDataset(newData.datasetsYaxis);
        if (formattedDatasets == null) {
            return;
        }
        customChartVar.data = {
            labels: newData.labelsXaxis,
            datasets: formattedDatasets.newDatasets
        };

        customChartVar.options = {
            responsive: true,
            maintainAspectRatio: false,
            hoverMode: 'index',
            scales: {
                yAxes: formattedDatasets.newyAxes,
            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
        }
    
        customChartVar.update();
    } catch(err) {
        generateToast('An error occured', 'red lighten-2 black-text', 'stay on');
        return;
    }
}


/*  ---------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------- Tool Statistics ------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------- */
// Tool Custom Chart
var toolCustomChartVar;
function toolCustomChartUpdateListener () {
    updateCustomChart(toolCustomChartVar, 'tool');
}
// Tool Standard Chart
var toolStandardChartVar = null;
var toolStandardValues = {};

// Tool Comments Chart
var toolCommentsChartVar = null;
var toolCommentsValues = {};

function fetchToolStats () {
    /*  ---------------------------------------------------------------------------------------------------------------------------------
    -------------------------------------------------------- Tool Custom Chart ----------------------------------------------------------
    ---------------------------------------------------------------------------------------------------------------------------------- */
    var toolCustomChart = document.getElementById('toolCustomChart').getContext('2d');
    toolCustomChartVar = new Chart(toolCustomChart, {
        type: 'bar',
        data: {
            labels: ["1/1/2021", "1/2/2021", "1/3/2021", "1/4/2021", "1/5/2021", "1/6/2021", "1/7/2021", "1/8/2021", "1/9/2021", "1/10/2021"],
            datasets: [{
                type: 'line',
                yAxisID: 'downloads',
                label: 'Downloads',
                borderColor: colorPallete[0],
                backgroundColor: colorPallete[0],
                borderWidth: 2,
                fill: false,
                data: [2, 10, 11, 14, 20, 25, 40, 48, 50, 52],
            }, {
                type: 'line',
                yAxisID: 'upvotes',
                label: 'Upvotes',
                borderColor: colorPallete[1],
                backgroundColor: colorPallete[1],
                borderWidth: 2,
                fill: false,
                data: [0, 52, 13, 50, 50, 26, 26, 26, 26, 95],
            }, {
                type: 'bar',
                yAxisID: 'cpuTime',
                label: 'CPU Time',
                backgroundColor: colorPallete[2],
                data: [709, 748.3, null, null, null, null, null, 572.3, null, null],
            }, {
                type: 'bar',
                yAxisID: 'memory',
                label: 'Memory',
                backgroundColor: colorPallete[3],
                data: [531.3, 690, null, null, null, null, null, 252, null, null],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            hoverMode: 'index',
            scales: {
                yAxes: [{
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'downloads',
                    scaleLabel: {
                        display: true,
                        labelString: 'Downloads',
                        fontColor: colorPallete[0],
                    },
                    ticks: {
                        fontColor: colorPallete[0],
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'upvotes',
                    scaleLabel: {
                        display: true,
                        labelString: 'Upvotes',
                        fontColor: colorPallete[1],
                    },
                    ticks: {
                        fontColor: colorPallete[1]
                    },
                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'right',
                    id: 'cpuTime',
                    scaleLabel: {
                        display: true,
                        labelString: 'CPU Time',
                        fontColor: colorPallete[2],
                    },
                    ticks: {
                        fontColor: colorPallete[2]
                    },

                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'right',
                    id: 'memory',
                    scaleLabel: {
                        display: true,
                        labelString: 'Memory',
                        fontColor: colorPallete[3],
                    },
                    ticks: {
                        fontColor: colorPallete[3]
                    },

                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }],

            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
        }
    });
    document.getElementById('toolCustomChartUpdate').addEventListener('click', toolCustomChartUpdateListener);

    /*  --------------------------------------------------------------------------------------------------------------------
    ------------------------------------------------- Tool Standard Chart --------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------- */
    if (toolStandardChartVar == null) {
        createToolStandardChart();
    }
    

    /*  --------------------------------------------------------------------------------------------------------------------
    ------------------------------------------------- Tool Comments Chart --------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------- */
    if (toolCommentsChartVar == null) {
        createToolCommentsChart();
    }
}

/*  ---------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------- Workflow Statistics ------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------- */
var workflowCustomChartVar;
function workflowCustomChartUpdateListener () {
    updateCustomChart(workflowCustomChartVar, 'workflow');
}

// Workflow Standard Chart
var workflowStandardChartVar = null;
var workflowStandardValues = {};

// Workflow Comments Chart
var workflowCommentsChartVar = null;
var workflowCommentsValues = {};

function fetchWorkflowStats () {
    /*  ---------------------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------------- Workflow Custom Chart ----------------------------------------------------------
    ---------------------------------------------------------------------------------------------------------------------------------- */
    var workflowCustomChart = document.getElementById('workflowCustomChart').getContext('2d');
    workflowCustomChartVar = new Chart(workflowCustomChart, {
        type: 'bar',
        data: {
            labels: ["1/1/2021", "1/2/2021", "1/3/2021", "1/4/2021", "1/5/2021", "1/6/2021", "1/7/2021", "1/8/2021", "1/9/2021", "1/10/2021"],
            datasets: [{
                type: 'line',
                yAxisID: 'downloads',
                label: 'Downloads',
                borderColor: colorPallete[0],
                backgroundColor: colorPallete[0],
                borderWidth: 2,
                fill: false,
                data: [2, 10, 11, 14, 20, 25, 40, 48, 50, 52],
            }, {
                type: 'line',
                yAxisID: 'upvotes',
                label: 'Upvotes',
                borderColor: colorPallete[1],
                backgroundColor: colorPallete[1],
                borderWidth: 2,
                fill: false,
                data: [0, 52, 13, 50, 50, 26, 26, 26, 26, 95],
            }, {
                type: 'bar',
                yAxisID: 'cpuTime',
                label: 'CPU Time',
                backgroundColor: colorPallete[2],
                data: [709, 748.3, null, null, null, null, null, 572.3, null, null],
            }, {
                type: 'bar',
                yAxisID: 'memory',
                label: 'Memory',
                backgroundColor: colorPallete[3],
                data: [531.3, 690, null, null, null, null, null, 252, null, null],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            hoverMode: 'index',
            scales: {
                yAxes: [{
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'downloads',
                    scaleLabel: {
                        display: true,
                        labelString: 'Downloads',
                        fontColor: colorPallete[0],
                    },
                    ticks: {
                        fontColor: colorPallete[0],
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'upvotes',
                    scaleLabel: {
                        display: true,
                        labelString: 'Upvotes',
                        fontColor: colorPallete[1],
                    },
                    ticks: {
                        fontColor: colorPallete[1]
                    },
                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'right',
                    id: 'cpuTime',
                    scaleLabel: {
                        display: true,
                        labelString: 'CPU Time',
                        fontColor: colorPallete[2],
                    },
                    ticks: {
                        fontColor: colorPallete[2]
                    },

                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'right',
                    id: 'memory',
                    scaleLabel: {
                        display: true,
                        labelString: 'Memory',
                        fontColor: colorPallete[3],
                    },
                    ticks: {
                        fontColor: colorPallete[3]
                    },

                    // grid line settings
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }],

            },
            tooltips: {
                mode: 'index',
                intersect: false
            },
        }
    });
    document.getElementById('workflowCustomChartUpdate').addEventListener('click', workflowCustomChartUpdateListener);

    /*  --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------- Workflow Standard Chart --------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------- */
    if (workflowStandardChartVar == null) {
        createWorkflowStandardChart();
    }

    /*  --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------- Workflow Comments Chart --------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------- */
    if (workflowCommentsChartVar == null) {
        createWorkflowCommentsChart();
    }
}


/*  ---------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------- Months Radio Buttons ------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------- */
function chartButtonsInit () {
    // Tool Standard Metrics
    var toolStandardButtons = document.getElementsByClassName('toolStandard');
    for (var i = 0; i < toolStandardButtons.length; i++) {
        toolStandardButtons[i].addEventListener('click', function (event) {
            setColorsForRadioButton(toolStandardButtons, event.target);
            var newChartValues = getStandardDataWithDuration('tool', event.target);
            updateStandardChart('tool', toolStandardChartVar, newChartValues);
        });
    }
    
    // Workflow Standard Metrics
    var workflowStandardButtons = document.getElementsByClassName('workflowStandard');
    for (var i = 0; i < toolStandardButtons.length; i++) {
        workflowStandardButtons[i].addEventListener('click', function (event) {
            setColorsForRadioButton(workflowStandardButtons, event.target);
            var newChartValues = getStandardDataWithDuration('workflow', event.target);
            updateStandardChart('workflow', workflowStandardChartVar, newChartValues);
        });
    }

    // Tool Comments
    var toolCommentsButtons = document.getElementsByClassName('toolComments');
    for (var i = 0; i < toolCommentsButtons.length; i++) {
        toolCommentsButtons[i].addEventListener('click', function (event) {
            setColorsForRadioButton(toolCommentsButtons, event.target);
            var newChartValues = getCommentDataWithDuration('tool', event.target);
            updateCommentsChart('tool', toolCommentsChartVar, newChartValues);
        });
    }
    
    // Workflow Comments
    var workflowCommentsButtons = document.getElementsByClassName('workflowComments');
    for (var i = 0; i < workflowCommentsButtons.length; i++) {
        workflowCommentsButtons[i].addEventListener('click', function (event) {
            setColorsForRadioButton(workflowCommentsButtons, event.target);
            var newChartValues = getCommentDataWithDuration('workflow', event.target);
            updateCommentsChart('workflow', workflowCommentsChartVar, newChartValues);
        });
    }

};
window.addEventListener("load", chartButtonsInit);

// Sets the color for the clicked radio button
function setColorsForRadioButton (btns, clickedBtn) {
    //make all buttons white
    for (var i = 0; i < btns.length; i++) {
        btns[i].style.background = 'white';
        btns[i].style.color = 'black';
    }
    // make clicked button teal
    clickedBtn.style.background = '#2BBBAD';
    clickedBtn.style.color = '#FFF';
}




/*  ---------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------- Tool / Workflow Standard Charts ----------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------- */
function createToolStandardChart () {
    var toolStandardChart = document.getElementById('toolStandardChart').getContext('2d');
    toolStandardChartVar = new Chart(toolStandardChart, {
        type: 'bar',
        data: {
            labels: ["2021-01-01", "2021-01-02", "2021-01-03"],
            datasets: [{
                type: 'line',
                yAxisID: 'upvotes',
                label: 'Upvotes',
                borderColor: colorPallete[3],
                backgroundColor: colorPallete[3],
                borderWidth: 2,
                fill: false,
                data: [1, 2, 3],
                pointRadius: 0
            }, {
                type: 'line',
                yAxisID: 'downvotes',
                label: 'Downvotes',
                borderColor: colorPallete[0],
                backgroundColor: colorPallete[0],
                borderWidth: 2,
                fill: false,
                data: [1, 2, 3],
                pointRadius: 0
            }, {
                type: 'line',
                yAxisID: 'downloads',
                label: 'Downloads',
                borderColor: colorPallete[1],
                backgroundColor: colorPallete[1],
                borderWidth: 2,
                fill: false,
                data: [1, 2, 3],
                pointRadius: 0
            }, {
                type: 'bar',
                yAxisID: 'cpuTime',
                label: 'CPU Time',
                backgroundColor: colorPallete[2],
                data: [1, 2, 3]
            }, {
                type: 'bar',
                yAxisID: 'memory',
                label: 'Memory',
                backgroundColor: colorPallete[4],
                data: [1, 2, 3]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            hoverMode: 'index',
            // stacked: false,
            scales: {
                yAxes: [{
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'upvotes',
                    scaleLabel: {
                        display: true,
                        labelString: 'Upvotes',
                        fontColor: colorPallete[3],
                    },
                    ticks: {
                        fontColor: colorPallete[3],
                        beginAtZero: true
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'downvotes',
                    scaleLabel: {
                        display: true,
                        labelString: 'Downvotes',
                        fontColor: colorPallete[0],
                    },
                    ticks: {
                        fontColor: colorPallete[0],
                        beginAtZero: true
                    },
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'downloads',
                    scaleLabel: {
                        display: true,
                        labelString: 'Downloads',
                        fontColor: colorPallete[1],
                    },
                    ticks: {
                        fontColor: colorPallete[1],
                        beginAtZero: true
                    },
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'right',
                    id: 'cpuTime',
                    scaleLabel: {
                        display: true,
                        labelString: 'CPU Time (clock ticks)',
                        fontColor: colorPallete[2],
                    },
                    ticks: {
                        fontColor: colorPallete[2]
                    },
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'right',
                    id: 'memory',
                    scaleLabel: {
                        display: true,
                        labelString: 'Memory (MB)',
                        fontColor: colorPallete[4],
                    },
                    ticks: {
                        fontColor: colorPallete[4]
                    },
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }],
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                }]
            },
            tooltips: {
                mode: 'index',
                intersect: false
            }
        }
    });
}
function createWorkflowStandardChart () {
    var workflowStandardChart = document.getElementById('workflowStandardChart').getContext('2d');
    workflowStandardChartVar = new Chart(workflowStandardChart, {
        type: 'bar',
        data: {
            labels: ["2021-01-01", "2021-01-02", "2021-01-03"],
            datasets: [{
                type: 'line',
                yAxisID: 'upvotes',
                label: 'Upvotes',
                borderColor: colorPallete[3],
                backgroundColor: colorPallete[3],
                borderWidth: 2,
                fill: false,
                data: [1, 2, 3],
                pointRadius: 0
            }, {
                type: 'line',
                yAxisID: 'downvotes',
                label: 'Downvotes',
                borderColor: colorPallete[0],
                backgroundColor: colorPallete[0],
                borderWidth: 2,
                fill: false,
                data: [1, 2, 3],
                pointRadius: 0
            }, {
                type: 'line',
                yAxisID: 'downloads',
                label: 'Downloads',
                borderColor: colorPallete[1],
                backgroundColor: colorPallete[1],
                borderWidth: 2,
                fill: false,
                data: [1, 2, 3],
                pointRadius: 0
            }, {
                type: 'line',
                yAxisID: 'exportVariety',
                label: 'Export Variety',
                borderColor: colorPallete[2],
                backgroundColor: colorPallete[2],
                borderWidth: 2,
                fill: false,
                data: [1, 2, 3],
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            hoverMode: 'index',
            // stacked: false,
            scales: {
                yAxes: [{
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'upvotes',
                    scaleLabel: {
                        display: true,
                        labelString: 'Upvotes',
                        fontColor: colorPallete[3],
                    },
                    ticks: {
                        fontColor: colorPallete[3],
                        beginAtZero: true
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'downvotes',
                    scaleLabel: {
                        display: true,
                        labelString: 'Downvotes',
                        fontColor: colorPallete[0],
                    },
                    ticks: {
                        fontColor: colorPallete[0],
                        beginAtZero: true
                    },
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'left',
                    id: 'downloads',
                    scaleLabel: {
                        display: true,
                        labelString: 'Downloads',
                        fontColor: colorPallete[1],
                    },
                    ticks: {
                        fontColor: colorPallete[1],
                        beginAtZero: true
                    },
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }, {
                    type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: 'right',
                    id: 'exportVariety',
                    scaleLabel: {
                        display: true,
                        labelString: 'Export Variety',
                        fontColor: colorPallete[2],
                    },
                    ticks: {
                        fontColor: colorPallete[2],
                        beginAtZero: true
                    },
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }],
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                }]
            },
            tooltips: {
                mode: 'index',
                intersect: false
            }
        }
    });
}

// gets data from OBC_ctrl.js
function getStandardData (roType, data, ro_created_at) {
    var roStandardValues = {};
    // Get dates
    for (var i = 0; i < data.length; i++) {
        data[i].created_at = data[i].created_at.substring(12, 16) + '-' + monthArr[data[i].created_at.substring(8, 11)] + '-' + data[i].created_at.substring(5, 7);
    }

    var today = new Date();
    var todaydd = String(today.getDate()).padStart(2, '0');
    var todaymm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var todayyyyy = today.getFullYear();
    if (data.length != 0) {
        var firstdd = ro_created_at.substring(5, 7);
        var firstmm = monthArr[ro_created_at.substring(8, 11)];
        var firstyyyy = ro_created_at.substring(12, 16);
    
        roStandardValues.xaxis = formatDates(getDates(new Date(firstyyyy, firstmm - 1, firstdd), new Date(todayyyyy, todaymm - 1, todaydd)));
    }
    else {
        roStandardValues.xaxis = formatDates(getDates(new Date(todayyyyy, todaymm - 1, todaydd), new Date(todayyyyy, todaymm - 1, todaydd)));
    }

    // Get data
    roStandardValues.upvotes = new Array(roStandardValues.xaxis.length).fill(0);
    roStandardValues.downvotes = new Array(roStandardValues.xaxis.length).fill(0);
    roStandardValues.downloads = new Array(roStandardValues.xaxis.length).fill(null);
    if (roType == 'tool') {
        roStandardValues.cpuTime = new Array(roStandardValues.xaxis.length).fill(null);
        roStandardValues.memory = new Array(roStandardValues.xaxis.length).fill(null);
    }
    else if (roType == 'workflow') {
        roStandardValues.exportVariety = new Array(roStandardValues.xaxis.length).fill(null);
    }

    for (var i = 0; i < data.length; i++) {
        var index = roStandardValues.xaxis.indexOf(data[i].created_at);
        switch (data[i].upvote) {
            case true:
                roStandardValues.upvotes = incrementSubarray(roStandardValues.upvotes, index, 1);
            case false:
                roStandardValues.downvotes = incrementSubarray(roStandardValues.downvotes, index, 1);
                break;
        }
    }

    if (roType == 'tool') {
        toolStandardValues = roStandardValues;
        if (toolStandardChartVar != null) {
            updateStandardChart('tool', toolStandardChartVar, toolStandardValues);
        }
        // set radiobutton to all
        var toolStandardButtons = document.getElementsByClassName('toolStandard');
        setColorsForRadioButton(toolStandardButtons, document.getElementById('toolStandardAllRadioBtn'));
    }
    else if (roType == 'workflow') {
        workflowStandardValues = roStandardValues;
        if (workflowStandardChartVar != null) {
            updateStandardChart('workflow', workflowStandardChartVar, workflowStandardValues);
        }
        // set radiobutton to all
        var workflowStandardButtons = document.getElementsByClassName('workflowStandard');
        setColorsForRadioButton(workflowStandardButtons, document.getElementById('workflowStandardAllRadioBtn'));
    }

}

function incrementSubarray (array, incrementFromIndex, incrementNum) {
    var slicedArr = array.slice(incrementFromIndex).map(function(entry) {
        return entry + incrementNum;
    });
    Array.prototype.splice.apply(array, [incrementFromIndex, array.length].concat(slicedArr));
    return array;
}

function updateStandardChart (roType, standardChartVar, chartValues) {
    if (roType == 'tool') {
        standardChartVar.data = {
            labels: chartValues.xaxis,
            datasets: [{
                type: 'line',
                yAxisID: 'upvotes',
                label: 'Upvotes',
                borderColor: colorPallete[3],
                backgroundColor: colorPallete[3],
                borderWidth: 2,
                fill: false,
                data: chartValues.upvotes,
                pointRadius: 0
            },{
                type: 'line',
                yAxisID: 'downvotes',
                label: 'Downvotes',
                borderColor: colorPallete[0],
                backgroundColor: colorPallete[0],
                borderWidth: 2,
                fill: false,
                data: chartValues.downvotes,
                pointRadius: 0
            },{
                type: 'line',
                yAxisID: 'downloads',
                label: 'Downloads',
                borderColor: colorPallete[1],
                backgroundColor: colorPallete[1],
                borderWidth: 2,
                fill: false,
                data: chartValues.downloads,
                pointRadius: 0
            }, {
                type: 'bar',
                yAxisID: 'cpuTime',
                label: 'CPU Time',
                backgroundColor: colorPallete[2],
                data: chartValues.cpuTime,
            }, {
                type: 'bar',
                yAxisID: 'memory',
                label: 'Memory',
                backgroundColor: colorPallete[4],
                data: chartValues.memory,
            }]
        };
    }
    else if (roType == 'workflow') {
        standardChartVar.data = {
            labels: chartValues.xaxis,
            datasets: [{
                type: 'line',
                yAxisID: 'upvotes',
                label: 'Upvotes',
                borderColor: colorPallete[3],
                backgroundColor: colorPallete[3],
                borderWidth: 2,
                fill: false,
                data: chartValues.upvotes,
                pointRadius: 0
            },{
                type: 'line',
                yAxisID: 'downvotes',
                label: 'Downvotes',
                borderColor: colorPallete[0],
                backgroundColor: colorPallete[0],
                borderWidth: 2,
                fill: false,
                data: chartValues.downvotes,
                pointRadius: 0
            },{
                type: 'line',
                yAxisID: 'downloads',
                label: 'Downloads',
                borderColor: colorPallete[1],
                backgroundColor: colorPallete[1],
                borderWidth: 2,
                fill: false,
                data: chartValues.downloads,
                pointRadius: 0
            }, {
                type: 'line',
                yAxisID: 'exportVariety',
                label: 'Export Variety',
                borderColor: colorPallete[2],
                backgroundColor: colorPallete[2],
                borderWidth: 2,
                fill: false,
                data: chartValues.exportVariety,
                pointRadius: 0
            }]
        };
    }
    standardChartVar.update();
}

function getStandardDataWithDuration (roType, clickedBtn) {
    var duration;
    switch (clickedBtn.name) {
        case '1month':
            duration = 1;
            break;
        case '3months':
            duration = 3;
            break;
        case '6months':
            duration = 6;
            break;
        case 'all':
            duration = 0;
            break;
    } 

    var allChartValues;
    if (roType == 'tool'){
        allChartValues = {
            xaxis: toolStandardValues.xaxis,
            upvotes: toolStandardValues.upvotes,
            downvotes: toolStandardValues.downvotes,
            downloads: toolStandardValues.downloads,
            cpuTime: toolStandardValues.cpuTime,
            memory: toolStandardValues.memory
        }
    }
    else if (roType == 'workflow'){
        allChartValues = {
            xaxis: workflowStandardValues.xaxis,
            upvotes: workflowStandardValues.upvotes,
            downvotes: workflowStandardValues.downvotes,
            downloads: workflowStandardValues.downloads,
            exportVariety: workflowStandardValues.exportVariety
        }
    }
    var startDate = new Date(allChartValues.xaxis[0].split('-')[0], allChartValues.xaxis[0].split('-')[1] - 1, allChartValues.xaxis[0].split('-')[2]);
    var currDate = new Date(allChartValues.xaxis[allChartValues.xaxis.length - 1].split('-')[0], allChartValues.xaxis[allChartValues.xaxis.length - 1].split('-')[1] - 1, allChartValues.xaxis[allChartValues.xaxis.length - 1].split('-')[2]);
    var pastDate;
    switch (duration) {
        case 0:
            return allChartValues;
        case 1:
            pastDate = currDate.removeDays(30);
            break;
        case 3:
            pastDate = currDate.removeDays(90);
            break;
        case 6:
            pastDate = currDate.removeDays(180);
            break;
    }
                    
    if (pastDate >= startDate) {
        var newStartDate = pastDate.getFullYear() + '-' + String(pastDate.getMonth() + 1).padStart(2, '0') + '-' + String(pastDate.getDate()).padStart(2, '0');
        var index = allChartValues.xaxis.indexOf(newStartDate);
        
        if (roType == 'tool') {
            return {
                xaxis: allChartValues.xaxis.slice(index),
                upvotes: allChartValues.upvotes.slice(index),
                downvotes: allChartValues.downvotes.slice(index),
                downloads: allChartValues.downloads.slice(index),
                cpuTime: allChartValues.cpuTime.slice(index),
                memory: allChartValues.memory.slice(index)
            }
        }
        else if (roType == 'workflow') {
            return {
                xaxis: allChartValues.xaxis.slice(index),
                upvotes: allChartValues.upvotes.slice(index),
                downvotes: allChartValues.downvotes.slice(index),
                downloads: allChartValues.downloads.slice(index),
                exportVariety: allChartValues.exportVariety.slice(index)
            }
        }
    }
    return allChartValues;

}

/*  ---------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------- Tool / Workflow Comment Charts ----------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------- */
function createToolCommentsChart () {
    var toolCommentsChart = document.getElementById('toolCommentsChart').getContext('2d');
    toolCommentsChartVar = new Chart(toolCommentsChart, {
        type: 'bar',
        data: {
            labels: ["2021-01-01", "2021-01-02", "2021-01-03"],
            datasets: [{
                label: 'Agree',
                backgroundColor: colorPallete[0],
                data: [1, 2, 3]
            }, {
                label: 'Disagree',
                backgroundColor: colorPallete[1],
                data: [2, 3, 4]
            }, {
                label: 'Solution',
                backgroundColor: colorPallete[2],
                data: [3, 4, 5]
            }, {
                label: 'Issue',
                backgroundColor: colorPallete[3],
                data: [4, 5, 6]
            }]
        },
        options: {
            tooltips: {
                mode: 'index',
                intersect: false
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    stacked: true,
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                }],
                yAxes: [{
                    stacked: true
                }]
            }
        }
    });
}
function createWorkflowCommentsChart () {
    var workflowCommentsChart = document.getElementById('workflowCommentsChart').getContext('2d');
    workflowCommentsChartVar = new Chart(workflowCommentsChart, {
        type: 'bar',
        data: {
            labels: ["2021-01-01", "2021-01-02", "2021-01-03"],
            datasets: [{
                label: 'Agree',
                backgroundColor: colorPallete[0],
                data: [1, 2, 3]
            }, {
                label: 'Disagree',
                backgroundColor: colorPallete[1],
                data: [2, 3, 4]
            }, {
                label: 'Solution',
                backgroundColor: colorPallete[2],
                data: [3, 4, 5]
            }, {
                label: 'Issue',
                backgroundColor: colorPallete[3],
                data: [4, 5, 6]
            }]
        },
        options: {
            tooltips: {
                mode: 'index',
                intersect: false
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    stacked: true,
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                }],
                yAxes: [{
                    stacked: true
                }]
            }
        }
    });
}

// gets data from OBC_ctrl.js
function getCommentsData (roType, data, ro_created_at) {
    var roCommentsValues = {};
    // Get dates
    var commentsData = [];
    for (var i = 0; i < data.length; i++) {
        getChildrenComments(data[i], commentsData);
    }

    var today = new Date();
    var todaydd = String(today.getDate()).padStart(2, '0');
    var todaymm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var todayyyyy = today.getFullYear();
    if (commentsData.length != 0) {
        var firstdd = ro_created_at.substring(5, 7);
        var firstmm = monthArr[ro_created_at.substring(8, 11)];
        var firstyyyy = ro_created_at.substring(12, 16);
    
        roCommentsValues.xaxis = formatDates(getDates(new Date(firstyyyy, firstmm - 1, firstdd), new Date(todayyyyy, todaymm - 1, todaydd)));
    }
    else {
        roCommentsValues.xaxis = formatDates(getDates(new Date(todayyyyy, todaymm - 1, todaydd), new Date(todayyyyy, todaymm - 1, todaydd)));
    }

    // Get data
    roCommentsValues.note = new Array(roCommentsValues.xaxis.length).fill(null);
    roCommentsValues.agree = new Array(roCommentsValues.xaxis.length).fill(null);
    roCommentsValues.disagree = new Array(roCommentsValues.xaxis.length).fill(null);
    roCommentsValues.solution = new Array(roCommentsValues.xaxis.length).fill(null);
    roCommentsValues.issue = new Array(roCommentsValues.xaxis.length).fill(null);

    for (var i = 0; i < commentsData.length; i++) {
        var index = roCommentsValues.xaxis.indexOf(commentsData[i].created_at);
        switch (commentsData[i].opinion) {
            case 'note':
                if (roCommentsValues.note[index] == null) {
                    roCommentsValues.note[index] = 1;
                    break;
                }
                roCommentsValues.note[index] += 1;
                break;
            case 'agree':
                if (roCommentsValues.agree[index] == null) {
                    roCommentsValues.agree[index] = 1;
                    break;
                }
                roCommentsValues.agree[index] += 1;
                break;
            case 'disagree':
                if (roCommentsValues.disagree[index] == null) {
                    roCommentsValues.disagree[index] = 1;
                    break;
                }
                roCommentsValues.disagree[index] += 1;
                break;
            case 'solution':
                if (roCommentsValues.solution[index] == null) {
                    roCommentsValues.solution[index] = 1;
                    break;
                }
                roCommentsValues.solution[index] += 1;
                break;
            case 'issue':
                if (roCommentsValues.issue[index] == null) {
                    roCommentsValues.issue[index] = 1;
                    break;
                }
                roCommentsValues.issue[index] += 1;
                break;
        }
    }

    if (roType == 'tool') {
        toolCommentsValues = roCommentsValues;
        if (toolCommentsChartVar != null) {
            updateCommentsChart('tool', toolCommentsChartVar, toolCommentsValues);
        }
        // set radiobutton to all
        var toolCommentsButtons = document.getElementsByClassName('toolComments');
        setColorsForRadioButton(toolCommentsButtons, document.getElementById('toolCommentsAllRadioBtn'));
    }
    else if (roType == 'workflow') {
        workflowCommentsValues = roCommentsValues;
        if (workflowCommentsChartVar != null) {
            updateCommentsChart('workflow', workflowCommentsChartVar, workflowCommentsValues);
        }
        // set radiobutton to all
        var workflowCommentsButtons = document.getElementsByClassName('workflowComments');
        setColorsForRadioButton(workflowCommentsButtons, document.getElementById('workflowCommentsAllRadioBtn'));
    }
}

function formatDates (dates) {
    for (var i = 0; i < dates.length; i++) {
        dates[i] = dates[i].toString().substring(11, 15) + '-' + monthArr[dates[i].toString().substring(4, 7)] + '-' + dates[i].toString().substring(8, 10);
    }
    return dates;
}


Date.prototype.addDays = function(days) {
    var date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
}
Date.prototype.removeDays = function(days) {
    var date = new Date(this.valueOf());
    date.setDate(date.getDate() - days);
    return date;
}
function getDates(startDate, stopDate) {
    var dateArray = new Array();
    var currentDate = startDate;
    while (currentDate <= stopDate) {
        dateArray.push(new Date (currentDate));
        currentDate = currentDate.addDays(1);
    }
    return dateArray;
}

function updateCommentsChart (roType, commentsChartVar, chartValues) {
    commentsChartVar.data = {
        labels: chartValues.xaxis,
        datasets: [{
            label: 'Note',
            backgroundColor: colorPallete[4],
            data: chartValues.note
        }, {
            label: 'Agree',
            backgroundColor: colorPallete[3],
            data: chartValues.agree
        }, {
            label: 'Disagree',
            backgroundColor: colorPallete[0],
            data: chartValues.disagree
        }, {
            label: 'Solution',
            backgroundColor: colorPallete[2],
            data: chartValues.solution
        }, {
            label: 'Issue',
            backgroundColor: colorPallete[1],
            data: chartValues.issue
        }]  
    };

    commentsChartVar.update();
}

function getCommentDataWithDuration (roType, clickedBtn) {
    var duration;
    switch (clickedBtn.name) {
        case '1month':
            duration = 1;
            break;
        case '3months':
            duration = 3;
            break;
        case '6months':
            duration = 6;
            break;
        case 'all':
            duration = 0;
            break;
    }

    var allChartValues;
    if (roType == 'tool'){
        allChartValues = {
            xaxis: toolCommentsValues.xaxis,
            note: toolCommentsValues.note,
            agree: toolCommentsValues.agree,
            disagree: toolCommentsValues.disagree,
            solution: toolCommentsValues.solution,
            issue: toolCommentsValues.issue
        }
    }
    else if (roType == 'workflow'){
        allChartValues = {
            xaxis: workflowCommentsValues.xaxis,
            note: workflowCommentsValues.note,
            agree: workflowCommentsValues.agree,
            disagree: workflowCommentsValues.disagree,
            solution: workflowCommentsValues.solution,
            issue: workflowCommentsValues.issue
        }
    }
    
    var startDate = new Date(allChartValues.xaxis[0].split('-')[0], allChartValues.xaxis[0].split('-')[1] - 1, allChartValues.xaxis[0].split('-')[2]);
    var currDate = new Date(allChartValues.xaxis[allChartValues.xaxis.length - 1].split('-')[0], allChartValues.xaxis[allChartValues.xaxis.length - 1].split('-')[1] - 1, allChartValues.xaxis[allChartValues.xaxis.length - 1].split('-')[2]);
    var pastDate;
    switch (duration) {
        case 0:
            return allChartValues;
        case 1:
            pastDate = currDate.removeDays(30);
            break;
        case 3:
            pastDate = currDate.removeDays(90);
            break;
        case 6:
            pastDate = currDate.removeDays(180);
            break;
    }
                    
    if (pastDate >= startDate) {
        var newStartDate = pastDate.getFullYear() + '-' + String(pastDate.getMonth() + 1).padStart(2, '0') + '-' + String(pastDate.getDate()).padStart(2, '0');
        var index = allChartValues.xaxis.indexOf(newStartDate);
                        
        return {
            xaxis: allChartValues.xaxis.slice(index),
            note: allChartValues.note.slice(index),
            agree: allChartValues.agree.slice(index),
            disagree: allChartValues.disagree.slice(index),
            solution: allChartValues.solution.slice(index),
            issue: allChartValues.issue.slice(index)
        }
    }
    return allChartValues;
}

function getChildrenComments (comment, data) {
    data.push({
        'comment': comment.comment,
        'opinion': comment.opinion,
        'created_at': comment.created_at.substring(12, 16) + '-' + monthArr[comment.created_at.substring(8, 11)] + '-' + comment.created_at.substring(5, 7)
    });
    if (comment.children == []) {
        return;
    }
    for (var i = 0; i < comment.children.length; i++) {
        getChildrenComments(comment.children[i], data);
    }
}









