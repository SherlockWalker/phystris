import threading
from pynput.keyboard import Key, Controller

lastFrame = None
frameLock = threading.Lock()

running = True
camera_enabled = True
camera_ready = False

# You can swap out keyboard bindings here! I kinda made this so that I can test it on TETR.IO
# Can use string characters or pynput.keyboard.Key objects (e.g. Key.left, Key.right, Key.down, Key.space)
keybinds = {
    "moveL": "a",
    "moveR": "d",
    "rotateL": "left",
    "rotateR": "right",
    "softdrop": "w",
    "harddrop": "s",
}
