from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from contextlib import asynccontextmanager

import cv2
import time
import threading
import os

import shared
import bodytracking

print("SERVER.PY LOADED.")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start body tracking in background thread
    trackingThread = threading.Thread(
        target=bodytracking.bodytracking,
        daemon=True
    )
    trackingThread.start()

    yield

    # Shutdown signal
    shared.running = False
    trackingThread.join(timeout=2)


app = FastAPI(lifespan=lifespan)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")


def generate_frames():
    while True:
        with shared.frameLock:
            frame = None if shared.lastFrame is None else shared.lastFrame.copy()

        if frame is None: time.sleep(0.01); continue
        shared.camera_ready = True

        success, buffer = cv2.imencode(".jpg", frame)

        if not success: continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )

        time.sleep(1 / 30)  # limit FPS to reduce CPU usage


@app.get("/video")
def video():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/health")
def health():
    return {
        "camera_running": shared.lastFrame is not None,
        "tracking_running": shared.running
    }

@app.post("/camera/toggle")
def toggle_camera():
    shared.camera_enabled = not shared.camera_enabled
    return {"camera_enabled": shared.camera_enabled}

@app.post("/camera/set")
async def set_camera(request: Request):
    data = await request.json()
    shared.camera_enabled = bool(data.get("enabled", True))
    return {"camera_enabled": shared.camera_enabled}

@app.get("/camera/status")
def camera_status():
    return {
        "enabled": shared.camera_enabled,
        "ready": shared.camera_ready
    }

@app.get("/state")
def state():
    return {
        "camera_enabled": shared.camera_enabled
    }

@app.get("/config")
def get_config():
    return shared.keybinds

@app.post("/config")
async def set_config(request: Request):
    data = await request.json()

    print("Received:", data)

    for k, v in data.items():
        shared.keybinds[k] = v

    print("Stored:", shared.keybinds)

    return shared.keybinds
