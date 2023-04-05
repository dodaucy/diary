/*
#############################################
#                                           #
#                   diary                   #
#                                           #
#                    MIT                    #
#     Copyright (C) 2022 - 2023 dodaucy     #
#     https://github.com/dodaucy/diary      #
#                                           #
#############################################
*/


var last_resize;
var last_data;
var cache = {};
const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];


function renderStats() {
    var year = parseInt(document.getElementById("year-span").innerText);
    var month = months.indexOf(document.getElementById("month-span").innerText) + 1;
    console.log(`Render stats for ${year}-${month}`);

    // Use cached data if available or get data from server
    if (!(year in cache)) {
        console.log(`Get data from server for ${year}...`);
        disable(true);
        request("GET", `stats?year=${year}`, function(stats) {
            cache[year] = stats;
            disable(false);
            renderStats();
        }, null);
        return;
    }

    // Get context
    console.log("Get canvas context");
    var stats_canvas = document.getElementById("stats");
    var ctx = stats_canvas.getContext("2d");

    // Calculate size
    console.log(`Window width: ${window.innerWidth}`);
    if (window.innerWidth < 800) {
        var width = window.innerWidth - 20;
    } else {
        var width = 800;
    }
    var place_per_day = Math.floor(width / (cache[year][month - 1].length - 1));
    console.log(`Place per day: ${place_per_day}`);
    stats_canvas.width = place_per_day * (cache[year][month - 1].length - 1) + 10;
    var line_spacing = Math.floor(stats_canvas.width / 10);
    stats_canvas.height = line_spacing * 3;
    console.log(`Line spacing: ${line_spacing}`);
    console.log(`Canvas size optimized from ${width}x${stats_canvas.width / 10 * 3} to ${stats_canvas.width}x${stats_canvas.height}`);

    // Clear canvas
    ctx.clearRect(0, 0, stats_canvas.width, stats_canvas.height);

    // Draw lines
    ctx.strokeStyle = font_color;
    ctx.fillStyle = font_color;
    for (var i = 0; i < 3; i++) {
        var y = line_spacing * (i + 0.5);
        // Draw line
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(stats_canvas.width, y);
        ctx.stroke();
        // Draw text
        ctx.font = `${line_spacing / 6}px ${getComputedStyle(document.body).getPropertyValue('--font-family')}`;
        ctx.fillText(["Bad", "Okay", "Good"][2 - i], 0, y - line_spacing / 6);
    }

    // Draw stats
    var checkboxes = document.getElementById('display-box').children;
    for (var i = 0; i < checkboxes.length; i++) {
        // Get elements
        var input = checkboxes[i].getElementsByTagName('input')[0];
        var label = checkboxes[i].getElementsByTagName('label')[0];
        var id = input.id.split('-')[0];
        // Check if checkbox is checked
        if (input.checked) {
            // Set color
            ctx.strokeStyle = label.style.color;
            ctx.fillStyle = label.style.color;
            // Start drawing
            ctx.beginPath();
            for (var j = 0; j < cache[year][month - 1].length; j++) {
                if (id in cache[year][month - 1][j] && cache[year][month - 1][j][id] > 0) {
                    var x = j * place_per_day + 5;
                    var y = stats_canvas.height - (cache[year][month - 1][j][id] - 0.5) * line_spacing;
                    // Draw line
                    ctx.lineTo(x, y);
                    ctx.stroke();
                    // Draw circle
                    ctx.beginPath();
                    ctx.arc(x, y, 3, 0, 2 * Math.PI);
                    ctx.fill();
                    // Move back to circle center
                    ctx.beginPath();
                    ctx.moveTo(x, y);
                }
            }
            ctx.stroke();
        }
    }
}


function resize() {
    // Spam protection (to not roast the CPU on resize)
    if (last_data == `${window.innerWidth}x${window.innerHeight}`) {
        return;
    }
    if (!!last_resize) {
        if (Date.now() - last_resize < 500) {
            setTimeout(function(){
                resize();
            }, 500)
            return;
        }
    }
    last_resize = Date.now();
    last_data = `${window.innerWidth}x${window.innerHeight}`;
    // Render stats
    renderStats();
}


function updateYear(left) {
    // Get year
    var year = parseInt(document.getElementById("year-span").innerText);
    // Update year
    if (left) {
        year--;
    } else {
        year++;
    }
    document.getElementById("year-span").innerText = year;
    // Render stats
    renderStats();
}


function updateMonth(left) {
    // Get month
    var month = months.indexOf(document.getElementById("month-span").innerText) + 1;
    // Update month
    if (left) {
        month--;
    } else {
        month++;
    }
    var stats_rendered = false;
    if (month < 1) {
        month = 12;
        updateYear(true);
        stats_rendered = true;
    } else if (month > 12) {
        month = 1;
        updateYear(false);
        stats_rendered = true;
    }
    document.getElementById("month-span").innerText = months[month - 1];
    // Render stats
    if (!stats_rendered) {
        renderStats();
    }
}


function init() {
    // Set month and year
    var date = new Date();
    document.getElementById("month-span").innerText = months[date.getMonth()];
    document.getElementById("year-span").innerText = date.getFullYear();
    // Render stats
    renderStats();
    // Add event listener
    window.addEventListener("resize", function(event) {
        resize();
    }, true);
}
