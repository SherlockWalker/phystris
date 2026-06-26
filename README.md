# phystris.

Intended to be a submission for [PhysTech](https://phystech-2026.devpost.com/). Here I mix complicated tech with something that I am familiar with to create a monstrosity of sorts. 

**My intention is to make Tetris as arduous to play as possible.**

Below is the idea that I'm trying to create.

![phystris graphics](phystris_graphics/phystech%20tetris.png)

# Instructions.
To run: 
- `git clone` this project back!

Assuming you already have Python, open terminal, and then:
- `cd` into the folder containing the files of PhysTris
- `pip install fastapi uvicorn opencv-python mediapipe numpy`
- `uvicorn server:app --reload`

Then open up http://127.0.0.1:8000/ on your browser to run.
- Start the camera! Or pause the camera if you don't want to use it anymore
- Switch into your favourite Tetris version (I personally play TETR.IO, thank you osk)
- You can modify configs in the page also to change your keybinds for the game.

# What's in the future for this project?
Multiplayer is a definite one. MediaPipe fortunately tracking of up to 4 people, but that's a little too crowded for my liking.

I'd also like to natively make Tetris in this project instead of just making this a macro. Other than that I'll be using the SRS (NOT SRS-180, despite me playing TETR.IO, and for other reasons I'll mention later) kick table for the Tetris bit.


