from pynput.keyboard import Key, Controller
import time

import shared

keyboard = Controller()

"""
About here I kind of figured that if I just fit all this stuff into bodytracking.py I'd have a super bloated file and debugging is hell
So here's the stuff on where and how I'm going to trigger using body tracking
Yes, this is basically a macro, I've done macros before and I got banned off a game twice for using them but for different reason
Typechecking and notes is because I don't want to have to open thousands of files at once lol I'll just rely on python to yell at me
"""
SPECIAL_KEYS = {
    "left": Key.left,
    "right": Key.right,
    "up": Key.up,
    "down": Key.down,
    
    "space": Key.space,
    "shift": Key.shift,
    "ctrl": Key.ctrl,
    "alt": Key.alt
}

def keyhelper(k):
    if isinstance(k, str):
        k = k.lower().strip()
        return SPECIAL_KEYS.get(k, k)
    return k

def K(name: str):
    return keyhelper(shared.keybinds[name])

# SD/HD line ratio, 0-1 where 0 is top of screen
SDline = 1/2
HDline = 2/3

# Other settings that I pilfered from TETR.IO
DAS_DELAY = 0.35
ARR_DELAY = 0.12
ROTATE_COOLDOWN = 0.40
HARD_DROP_DURATION = 1.2

# Global states for Postures
isSoftDropping = False
isJumping = False
jumpStartTime = None
lastHDtime = 0.0
HDmessageTime = 0.0

class detectBox:
    def __init__(self, name: str, 
                       x1: float, y1: float, x2: float, y2: float, 
                       binding,
                       mode="tap", cooldown=0.4, das=0.35, arr=0.12,
                       colourOn=(0, 255, 0), colourOff=(255, 0, 0), thickness=4):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.binding = binding
        self.colour = (colourOn[::-1], colourOff[::-1]) #Converted to BGR format here due to camera so after drawn it flips back
        self.thickness = thickness

        self.mode = mode
        self.cooldown = cooldown
        self.das = das
        self.arr = arr

        self.isActive = False
        self.lastTrigger = 0.0
        self.activeStartTime = 0.0
        self.isRepeating = False

    def trigger(self):
        key = keyhelper(shared.keybinds[self.binding])
        keyboard.press(key)
        keyboard.release(key)
        self.lastTrigger = time.time()

    def update(self, landmarks):
        current = False
        if landmarks and len(landmarks) > 0:
            pose_landmarks = landmarks[0]
            for lm in pose_landmarks:
                if lm.visibility > 0.5:
                    if (self.x1 <= lm.x <= self.x2) and (self.y1 <= lm.y <= self.y2): current = True; break

        now = time.time()
        if current:
            if not self.isActive:
                if now - self.lastTrigger >= self.cooldown:
                    self.isActive = True
                    self.activeStartTime = now
                    self.isRepeating = False
                    self.trigger()
            elif self.mode == "repeat":
                if not self.isRepeating:
                    if now - self.activeStartTime >= self.das:
                        self.trigger()
                        self.isRepeating = True
                elif now - self.lastTrigger >= self.arr: self.trigger()
            elif self.mode == "tap": pass
        else:
            self.isActive = False
            self.isRepeating = False


detections = []


# LR rotation, LR move
def createDetections():
    global detections # I'm highly aware I shouldn't do this (god I wish Python was more similar to C++ features...)
    detections = [
        detectBox("LRotate", 0, 0, 0.25, 0.25, "rotateL", mode="tap", cooldown=ROTATE_COOLDOWN),
        detectBox("RRotate", 0.75, 0, 1, 0.25, "rotateR", mode="tap", cooldown=ROTATE_COOLDOWN),
        detectBox("LMove", 0, 0.75, 0.25, 1, "moveL", mode="repeat", das=DAS_DELAY, arr=ARR_DELAY),
        detectBox("RMove", 0.75, 0.75, 1, 1, "moveR", mode="repeat", das=DAS_DELAY, arr=ARR_DELAY)
    ]


def updatePostures(landmarks):
    global isSoftDropping, isJumping, jumpStartTime, lastHDtime, HDmessageTime
    
    if not landmarks or len(landmarks) == 0:
        if isSoftDropping: 
            keyboard.release(keyhelper(shared.keybinds["softdrop"]))
            isSoftDropping = False
        return

    pose_landmarks = landmarks[0]

    # Soft drop logic
    shouldSoftDrop = True
    for lm in pose_landmarks:
        if lm.visibility > 0.5 and lm.y < SDline:
            shouldSoftDrop = False; break

    if shouldSoftDrop and not isSoftDropping:
        keyboard.press(keyhelper(shared.keybinds["softdrop"]))
        isSoftDropping = True
    elif not shouldSoftDrop and isSoftDropping:
        keyboard.release(keyhelper(shared.keybinds["softdrop"]))
        isSoftDropping = False


    # Hard drop logic
    shouldHardDrop = True
    for lm in pose_landmarks:
        if lm.visibility > 0.5 and lm.y >= HDline: 
            shouldHardDrop = False; break
            
    now = time.time()
    if shouldHardDrop:
        if not isJumping:
            isJumping = True
            jumpStartTime = now
        elif now - jumpStartTime > HARD_DROP_DURATION:
            isJumping = False
            jumpStartTime = None

    elif isJumping:
        duration = now - jumpStartTime
        if duration <= HARD_DROP_DURATION:
            keyboard.press(keyhelper(shared.keybinds["harddrop"]))
            keyboard.release(keyhelper(shared.keybinds["harddrop"]))
            lastHDtime = now
            HDmessageTime = now + 1.0
        
        isJumping = False
        jumpStartTime = None


def updateMacros(landmarks):
    updatePostures(landmarks)
    for detect in detections: detect.update(landmarks)

def cleanup():
    for key in ["rotateL", "rotateR", "moveL", "moveR", "softdrop", "harddrop"]:
        try: keyboard.release(keyhelper(shared.keybinds[key]))
        except: pass
