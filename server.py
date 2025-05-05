from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import keyboard
import asyncio
import threading
import json

app = FastAPI()
clients = set()
key_event_queue = asyncio.Queue()
loop = asyncio.get_event_loop()
pressed_modifiers = set()
modifier_keys = {"ctrl", "alt", "shift", "windows", "right ctrl", "right alt", "right shift", "right windows"}
keymap_json_filename = "keymaps.json"

# public/overlayをマウント
app.mount("/overlay", StaticFiles(directory="public/overlay"), name="overlay")

@app.get("/overlay")
async def read_index():
    return FileResponse("public/overlay/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            key = await key_event_queue.get()
            await websocket.send_text(json.dumps({"keys": [key]}))
    except Exception as e:
        print("WebSocket Error:", e)
    finally:
        clients.remove(websocket)

def convert_key_from_keymaps_json(key: str) -> str:
    try:
        with open(keymap_json_filename, encoding='utf-8') as f:
            keymaps = json.load(f)
        for keymap in keymaps:
            if key in keymap["key"]:
                return keymap["name"]
    except Exception as e:
        print("keymap error:", e)
    return key

# 押されたキーの組み合わせを取得
def on_key_event(e):
    if e.event_type == "down":
        is_modifier = False
        name = e.name.lower()

        if name in modifier_keys:
            is_modifier = True
            is_first_press = name not in pressed_modifiers
            pressed_modifiers.add(convert_key_from_keymaps_json(name))
            # print(pressed_modifiers)
            if not is_first_press:
                return
        
        combo = [convert_key_from_keymaps_json(name)]
        if not is_modifier: combo = list(pressed_modifiers) + [name]
        formatted = " + ".join(combo).title()
        asyncio.run_coroutine_threadsafe(key_event_queue.put(formatted), loop)

    elif e.event_type == "up":
        name = e.name.lower()
        if name in modifier_keys:
            pressed_modifiers.discard(convert_key_from_keymaps_json(name))
            # print(pressed_modifiers)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=keyboard.hook, args=(on_key_event,), daemon=True).start()
    print("http://127.0.0.1:8000/overlay")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", reload=True)
