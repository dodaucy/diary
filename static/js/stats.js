var last_resize;
var last_data;
var cache = {};
const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];


async function render_stats() {
    disable(true);
    var year = parseInt(document.getElementById("year-span").innerText);
    var month = months.indexOf(document.getElementById("month-span").innerText) + 1;
    console.log(`Render stats for ${year}-${month}`);

    // Get data from server if not cached
    if (!(year in cache)) {
        console.log(`Get data from server for ${year}...`);
        cache[year] = await async_request(
            "GET",
            `stats?year=${year}`,
            true
        );
    }

    // Get context
    console.log("Get canvas context");
    var stats_canvas = document.getElementById("stats");
    var ctx = stats_canvas.getContext("2d");

    // Calculate size
    console.log(`Window width: ${window.innerWidth}`);
    var width = Math.min(window.innerWidth - 20, 800);
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
        ctx.font = `${line_spacing / 6}px ${getComputedStyle(document.body).getPropertyValue("--font-family")}`;
        ctx.fillText(["Bad", "Okay", "Good"][2 - i], 0, y - line_spacing / 6);
    }

    // Draw stats
    var checkboxes = document.getElementById("display-box").children;
    for (var i = 0; i < checkboxes.length; i++) {
        // Get elements
        var input = checkboxes[i].getElementsByTagName("input")[0];
        var label = checkboxes[i].getElementsByTagName("label")[0];
        var id = input.id.split("-")[0];
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

    disable(false);
}


async function resize() {
    // Spam protection (to not roast the CPU on resize)
    if (last_data == `${window.innerWidth}x${window.innerHeight}`) {
        return;
    }
    if (!!last_resize) {
        if (Date.now() - last_resize < 500) {
            setTimeout(async function(){
                await resize();
            }, 500)
            return;
        }
    }
    last_resize = Date.now();
    last_data = `${window.innerWidth}x${window.innerHeight}`;
    // Render stats
    try {
        await render_stats();
    } catch (error) {
        error_string = error.toString();
        if (!error_string.startsWith("Request Failed")) {
            throw error;
        }
        show_reload_popup(true, error_string.substring(15));
    }
}


async function update_year(left, render_stats_after_update) {
    var year = parseInt(document.getElementById("year-span").innerText);
    var year_span = document.getElementById("year-span");
    // Update year
    year_span.innerText = year + (left ? -1 : 1);
    // Render stats
    if (!render_stats_after_update) {
        return;
    }
    try {
        await render_stats();
    } catch (error) {
        if (!error.toString().startsWith("Request Failed")) {
            throw error;
        }
        // Reset year
        console.log("Reset year");
        year_span.innerText = year;
        disable(false);
    }
}


async function update_month(left) {
    var month_span = document.getElementById("month-span");
    var month = months.indexOf(month_span.innerText) + 1;
    // Update month
    var new_month = month + (left ? -1 : 1);
    month_span.innerText = months[(new_month - 1 + 12) % 12];
    // Update year if needed
    if (new_month < 1) {
        await update_year(true, false);
    } else if (new_month > 12) {
        await update_year(false, false);
    }
    // Render stats
    try {
        await render_stats();
    } catch (error) {
        if (!error.toString().startsWith("Request Failed")) {
            throw error;
        }
        // Reset month
        console.log("Reset month");
        month_span.innerText = months[month - 1];
        if (new_month < 1) {
            await update_year(false, false);
        } else if (new_month > 12) {
            await update_year(true, false);
        }
        disable(false);
    }
}


async function init() {
    // Set month and year
    var date = new Date();
    document.getElementById("month-span").innerText = months[date.getMonth()];
    document.getElementById("year-span").innerText = date.getFullYear();
    // Render loading canvas
    console.log("Render loading canvas");
    var stats_canvas = document.getElementById("stats");
    var ctx = stats_canvas.getContext("2d");
    stats_canvas.width = Math.min(window.innerWidth, 800);
    stats_canvas.height = stats_canvas.width / 10 * 3;
    ctx.font = `${stats_canvas.height / 6}px ${getComputedStyle(document.body).getPropertyValue("--font-family")}`;
    ctx.fillStyle = font_color;
    ctx.textAlign = "center";
    ctx.fillText("Loading...", stats_canvas.width / 2, stats_canvas.height / 2);
    // Render stats
    try {
        await render_stats();
    } catch (error) {
        error_string = error.toString();
        if (!error_string.startsWith("Request Failed")) {
            throw error;
        }
        show_reload_popup(true, error_string.substring(15));
    }
    // Add event listener
    window.addEventListener("resize", async function(event) {
        await resize();
    }, true);
}
