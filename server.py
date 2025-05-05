from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import keyboard
import asyncio
import threading
import json
import os

app = FastAPI()
clients = set()
key_event_queue = asyncio.Queue()
loop = asyncio.get_event_loop()
pressed_modifiers = set()
modifier_keys = {"ctrl", "alt", "shift", "windows", "right ctrl", "right alt", "right shift", "right windows"}
keymap_json_filename = os.path.join(os.path.dirname(__file__), "keymaps.json")
config_path = os.path.join(os.path.dirname(__file__), "config.json")
config = {}
with open(config_path, encoding="utf-8") as f:
    config_json = json.load(f)
    for data in config_json:
        config[data["name"]] = data["value"]
print(config)

# public/overlayをマウント
app.mount("/overlay", StaticFiles(directory="public/overlay"), name="overlay")

@app.get("/overlay")
async def read_overlay_index():
    return FileResponse("public/overlay/index.html")

@app.get("/setting")
async def read_setting_index():
    return FileResponse("public/setting/index.html")

@app.get("/config.json")
async def get_config():
    return FileResponse(config_path)

@app.post("/save-config")
async def save_config(request: Request):
    data = await request.json()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return {"status": "ok"}

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



# Task Tray Icon
import pystray
from PIL import Image
import webbrowser

def on_open_settings(icon, item):
    webbrowser.open("http://localhost:"+str(config.get("port", 8000))+"/setting")

def on_quit(icon, item):
    icon.stop()
    os._exit(0)

def on_copy_url():
    import pyperclip
    pyperclip.copy("http://localhost:"+str(config.get("port", 8000))+"/overlay")

def setup_tray_icon():
    icon_path = os.path.join(os.path.dirname(__file__), "public", "tray.png")
    image = Image.open(icon_path)

    icon = pystray.Icon("obs-keyinput-overlay", image, "KeyOverlay", menu=pystray.Menu(
        pystray.MenuItem("設定を開く", on_open_settings),
        pystray.MenuItem("URLをコピー", on_copy_url),
        pystray.MenuItem("終了", on_quit)
    ))
    threading.Thread(target=icon.run, daemon=True).start()




@app.on_event("startup")
async def startup_event():
    threading.Thread(target=keyboard.hook, args=(on_key_event,), daemon=True).start()
    setup_tray_icon()
    print("http://127.0.0.1:"+str(config.get("port", 8000))+"/overlay")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", reload=True)
