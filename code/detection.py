from pynput.keyboard import Key, Controller

keyboard = Controller();

"""
About here I kind of figured that if I just fit all this stuff into bodytracking.py I'd have a super bloated file and debugging is hell
So here's the stuff on where and how I'm going to trigger using body tracking
Yes, this is basically a macro, I've done macros before and I got banned off a game twice for using them but for different reason
"""
class detectBox:
    def __init__(self, name, x1, y1, x2, y2, binding, colour=(255, 0, 0)):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.binding = binding
        self.colour = colour
        self.collided = False

    def trigger(self): keyboard.press(self.binding);
    def untrigger(self): keyboard.release(self.binding);

    def collision(self, landmark): #Assuming landmark is of form (x,y) because how else would you store it
        inside = (self.x1 <= landmark[0] <= self.x2) and (self.y1 <= landmark[0] <= self.y2)
        if (inside and not self.collided): self.trigger();
        elif (not inside and self.collided): self.untrigger();
