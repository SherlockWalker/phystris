import cv2 # I take a leaf out of Michael Reeves' book
import mediapipe as mp
from mediapipe import tasks as tasks
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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



# Path to model, remember to change later when I have better code structure
modelPath = "../pose_landmarker.task"

# I got this bit from Google's documentation and guide on use of pose landmarker
BaseOptions = tasks.BaseOptions
PoseLandmarker = vision.PoseLandmarker
PoseLandmarkerOptions = vision.PoseLandmarkerOptions
PoseLandmarkerResult = vision.PoseLandmarkerResult
VisionRunningMode = vision.RunningMode

# Debugging?
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    print('pose landmarker result: {}'.format(result)) # Should be of type PoseLandmarkerResult but it errored so not explicit here 

# PoseLandmarker instance created
options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=modelPath),
                                running_mode=VisionRunningMode.LIVE_STREAM, # Livestream mode
                                result_callback=print_result)

# Open camera (CV2)
# I super hate this bit because documentation was really messed up
for i in range(0, 3): # Change to either 0/1/2 depending what camera I have for now.
    camera = cv2.VideoCapture(i) 
    if (camera.isOpened()): break; 
    elif (camera == 2): print("Camera unavailable."); exit(); 


with PoseLandmarker.create_from_options(options) as landmarker:
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
        landmarker.detect_async(mp_image, 50) # 50ms, change later


        

