import cv2 # I take a leaf out of Michael Reeves' book
import mediapipe as mp
from mediapipe import tasks as tasks
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
from pynput.keyboard import Key

from detection import detectBox;

# Visualisation stuffs, I got off Google's CoLab notebook
import numpy as np
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
def drawLandmarks(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  pose_landmark_style = drawing_styles.get_default_pose_landmarks_style()
  pose_connection_style = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2)

  for pose_landmarks in pose_landmarks_list:
    drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=pose_landmarks,
        connections=vision.PoseLandmarksConnections.POSE_LANDMARKS,
        landmark_drawing_spec=pose_landmark_style,
        connection_drawing_spec=pose_connection_style)

  return annotated_image

detections = []
# For some reason CV2 wants your coordinates to be 0 to 1

# LR rotation, LR move
def createDetections():
    global detections # I'm highly aware I shouldn't do this (god I wish Python was more similar to C++ features...)
    detections = [detectBox("LRotate", 0, 0, 0.25, 0.25, Key.left, (0, 255, 0)),
                 detectBox("RRotate", 0.75, 0, 1, 0.25, Key.right),
                 detectBox("LMove", 0, 0.75, 0.25, 1, "a"),
                 detectBox("RMove", 0.75, 0.75, 1, 1, "d")
                 ]
# Other than this we need a case to determine if they're on top half of screen or not

def drawDetection(frame, detections):
    fy, fx, _ = frame.shape
    for detect in detections: 
        cv2.rectangle(frame, 
                      (int(detect.x1 * fx), int(detect.y1 * fy)), 
                      (int(detect.x2 * fx), int(detect.y2 * fy)),
                      detect.colour, detect.thickness)
    return frame;

# Path to model, remember to change later when I have better code structure
modelPath = "pose_landmarker.task"

# I got this bit from Google's documentation and guide on use of pose landmarker
BaseOptions = tasks.BaseOptions
PoseLandmarker = vision.PoseLandmarker
PoseLandmarkerOptions = vision.PoseLandmarkerOptions
PoseLandmarkerResult = vision.PoseLandmarkerResult
VisionRunningMode = vision.RunningMode

lastFrame = None #Last displayable frame
def print_result(result, output, timestamp): #For now I don't use timestamp, it might error I don't care
    global lastFrame

    image = cv2.cvtColor(output.numpy_view(), cv2.COLOR_RGB2BGR)
    
    # 2. Check if any poses were actually detected
    if (result.pose_landmarks):
        lastFrame = drawLandmarks(output.numpy_view(), result) #Draw landmark
        lastFrame = cv2.cvtColor(lastFrame, cv2.COLOR_RGB2BGR) # Back to BGR you go:3 for display or something
        lastFrame = cv2.flip(lastFrame, 1) #Flip camera horizontally
        lastFrame = drawDetection(lastFrame, detections)
    else:
        lastFrame = cv2.flip(image, 1)

# PoseLandmarker instance created
options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=modelPath),
                                running_mode=VisionRunningMode.LIVE_STREAM, # Livestream mode
                                result_callback=print_result)

# Open camera (CV2)
# I super hate this bit because documentation was really messed up
# Change to either 0/1/2 depending what camera I have for now. 
# My builtin webcam works on some angles and I don't want to activate it so this'll sometimes flip back and forth between 0 and 1
camera = cv2.VideoCapture(0);
"""
for i in range(0, 3):
    camera = cv2.VideoCapture(i) 
    if (camera.isOpened()): break;
"""


if (not camera or not camera.isOpened()):
    print("Camera unavailable.")
    exit()

lastFrame = None;

with PoseLandmarker.create_from_options(options) as landmarker:
    hasRead, frame = camera.read()
    if not hasRead:
        print("Failed to read initial camera frame.")
        exit()
        
    fy, fx, _ = frame.shape
    cv2.namedWindow("phystris", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("phystris", fx, fy) #Apparently this damn thing is clipping the left side of my camera
    
    createDetections();
    while (True):
        hasRead, frame = camera.read()
        if (not hasRead): # Just exit the camera stream entirely
            print("Frame not received. Removing video stream.")
            break;
        
        # For some historical reason, cameras read in BGR so I have to convert it to RGB
        convertedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); 

        # Convert the frame received to a MediaPipe’s Image object.
        # This is Google's thing btw
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=convertedFrame)
        landmarker.detect_async(mp_image, int(time.time() * 1000))

        #Draw on last frame received, else receive first frame
        if (lastFrame is not None): cv2.imshow("phystris", lastFrame)
        else:
            lastFrame = drawDetection(frame, detections)
            cv2.imshow("phystris", lastFrame)
        
        # I forgot to render video lmao
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
