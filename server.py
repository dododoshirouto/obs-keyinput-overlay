from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pynput import keyboard
import asyncio
import threading
import json

app = FastAPI()
clients = set()

# キーイベント送信用の非同期キュー
key_event_queue = asyncio.Queue()


# publicフォルダを/staticとしてマウント（例：/static/style.css）
app.mount("/overlay", StaticFiles(directory="public/overlay"), name="overlay")

# ルートアクセスで public/index.html を返す
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
            print("send key:", key)
            await websocket.send_text(json.dumps({"keys": [key]}))
    except Exception:
        clients.remove(websocket)


loop = asyncio.get_event_loop()


# pynputでキー入力を監視して、非同期キューに追加
def on_press(key):
    global loop
    try:
        k = key.char or str(key)
        print("press key:", k)
    except AttributeError:
        k = str(key)
    if loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(key_event_queue.put(k), loop)


def start_key_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()


@app.on_event("startup")
async def startup_event():
    global loop
    loop = asyncio.get_event_loop()
    threading.Thread(target=start_key_listener, daemon=True).start()


# サーバ起動時にリスナーも別スレッドで動かす
def run():
    print_url()
    threading.Thread(target=start_key_listener, daemon=True).start()


def print_url():
    print("http://127.0.0.1:8000/overlay")


if __name__ == "__main__":
    run()
