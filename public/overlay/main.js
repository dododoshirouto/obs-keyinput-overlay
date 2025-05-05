const ws = new WebSocket("ws://localhost:8000/ws");
const container = document.getElementById("keys");

ws.onmessage = e => {
    const { keys } = JSON.parse(e.data);

    displayKey(keys[0]);
};



var settimeoutid = null;
var keyElem = container.getElementsByClassName("key")[0];
function displayKey(key) {
    keyElem.innerHTML = key;
    keyElem.classList.add("open");
    clearTimeout(settimeoutid);
    settimeoutid = setTimeout(() => {
        keyElem.classList.remove("open");
    }, 500);
    keyElem.classList.add("press");
    setTimeout(() => {
        keyElem.classList.remove("press");
    }, 30);
}