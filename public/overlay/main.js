var ws = null;
const container = document.getElementById("keys");

config = [];
last_init = 0;
function init() {
    if (Date.now() - last_init < 1000 * 5) return;
    last_init = Date.now();

    fetch('/config.json').then(res => res.json()).then(json => json.forEach(v => {
        config[v.name] = v.value;
        document.body.classList = [];
        for (let key in config) {
            document.body.classList.add(key);
            document.body.classList.add(key + '-' + config[key].replace(/[-\s]+/g, '-'));
        }

        if (!ws) {
            ws = new WebSocket("ws://localhost:" + config.port + "/ws");
            ws.onmessage = e => {
                const { keys } = JSON.parse(e.data);

                displayKey(keys[0]);
            };
        }
    }));
}



var settimeoutid = null;
var keyElem = container.getElementsByClassName("key")[0];
function displayKey(key) {
    keyElem.innerHTML = key;
    keyElem.classList.add("open");
    clearTimeout(settimeoutid);
    settimeoutid = setTimeout(() => {
        keyElem.classList.remove("open");
    }, config.duration ?? 500);
    keyElem.classList.add("press");
    setTimeout(() => {
        keyElem.classList.remove("press");
    }, 30);
    init();
}

window.addEventListener("load", init);

window.addEventListener("onerror", e => {
    document.getElementById("debug").innerHTML += e.message + "\n";
});