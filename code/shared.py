import threading

lastFrame = None
frameLock = threading.Lock()

running = True
camera_enabled = True
