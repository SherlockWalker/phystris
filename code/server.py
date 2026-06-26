from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import StreamingResponse, HTMLResponse
from contextlib import asynccontextmanager

import cv2
import time
import threading

import shared
import bodytracking


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


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>PhysTris</title>
        </head>

        <body>
            <h1>PhysTris</h1>
            <img src="/video">

            <div class="panel">
                <button id="cameraBtn" onclick="toggleCamera()">Camera: ON</button>
            </div>

            <script>
                async function toggleCamera() 
                {
                    await fetch('/camera/toggle', { method: 'POST' });
                    updateButton();
                }

                async function updateButton() 
                {
                    const res = await fetch('/state');
                    const data = await res.json();
                    const btn = document.getElementById("cameraBtn");
                    btn.innerText = data.camera_enabled ? "Camera: ON" : "Camera: OFF";
                }
                updateButton();
                setInterval(updateButton, 1000);
            </script>
        </body>
    </html>
    """


def generate_frames():
    while True:
        with shared.frameLock:
            frame = None if shared.lastFrame is None else shared.lastFrame.copy()

        if frame is None: time.sleep(0.01); continue

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

@app.get("/state")
def state():
    return {
        "camera_enabled": shared.camera_enabled
    }
