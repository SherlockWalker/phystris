from fastapi import FastAPI
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
            <title>Pose Tracker</title>
        </head>
        <body>
            <h1>Pose Tracker</h1>
            <img src="/video">
        </body>
    </html>
    """


def generate_frames():
    while True:

        with shared.frameLock:
            frame = None if shared.lastFrame is None else shared.lastFrame.copy()

        if frame is None:
            time.sleep(0.01)
            continue

        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            continue

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
