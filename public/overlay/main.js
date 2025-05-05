const ws = new WebSocket("ws://localhost:8000/ws");
const container = document.getElementById("keys");

ws.onmessage = e => {
    const { keys } = JSON.parse(e.data);
    container.innerHTML = "";
    keys.forEach(key => {
        const el = document.createElement("div");
        el.className = "key";
        el.textContent = key;
        container.appendChild(el);
    });
};
