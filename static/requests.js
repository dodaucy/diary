function get(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onerror = function() {
        alert("Network error");
    }
    xhr.onload = function() {
        if (xhr.status == 200) {
            callback(JSON.parse(xhr.responseText));
        } else {
            alert("Error: " + xhr.status);
        }
    }
    xhr.send();
}
