import threading

lastFrame = None
frameLock = threading.Lock()

running = True
