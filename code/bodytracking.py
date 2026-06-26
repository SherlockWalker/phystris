import cv2 # I take a leaf out of Michael Reeves' book
import mediapipe as mp
from mediapipe import tasks as tasks
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time

# my libraries
import detection
from draw_detections import drawLandmarks, drawDetection, drawStatusOverlays

#libraries for porting to web
import shared

def bodytracking():
    # Path to model, remember to change later when I have better code structure
    modelPath = "pose_landmarker.task"

    # I got this bit from Google's documentation and guide on use of pose landmarker
    BaseOptions = tasks.BaseOptions
    PoseLandmarker = vision.PoseLandmarker
    PoseLandmarkerOptions = vision.PoseLandmarkerOptions
    PoseLandmarkerResult = vision.PoseLandmarkerResult
    VisionRunningMode = vision.RunningMode

    def print_result(result, output, timestamp): #For now I don't use timestamp, it might error I don't care
        image = cv2.cvtColor(output.numpy_view(), cv2.COLOR_RGB2BGR)
        
        # Update macro tracking
        detection.updateMacros(result.pose_landmarks)

        # 2. Check if any poses were actually detected
        if (result.pose_landmarks):
            frame = drawLandmarks(output.numpy_view(), result) #Draw landmark
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Back to BGR you go:3 for display or something
        else:
            frame = image

        # Keybinds. Don't change them here!
        keysDict = {'rotateL': detection.KEY_ROTATE_LEFT,
                    'rotateR': detection.KEY_ROTATE_RIGHT,
                    'moveL': detection.KEY_MOVE_LEFT,
                    'moveR': detection.KEY_MOVE_RIGHT,
                    'softdrop': detection.KEY_SOFT_DROP,
                    'harddrop': detection.KEY_HARD_DROP}
        
        frame = drawDetection(frame, detection.detections)
        frame = drawStatusOverlays(frame, detection.isSoftDropping, detection.isJumping, detection.jumpStartTime, detection.HDmessageTime, keysDict,
                                    detection.SDline, detection.HDline)
        with shared.frameLock: shared.lastFrame = frame.copy()

    # PoseLandmarker instance created
    options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=modelPath),
                                    running_mode=VisionRunningMode.LIVE_STREAM, # Livestream mode
                                    result_callback=print_result)

    # Open camera (CV2)
    # I super hate this bit because documentation was really messed up
    # Change to either 0/1/2 depending what camera I have for now. 
    # My builtin webcam works on some angles and I don't want to activate it so this'll sometimes flip back and forth between 0 and 1
    camera = cv2.VideoCapture(1); 
    """
    for i in range(0, 3):
        camera = cv2.VideoCapture(i) 
        if (camera.isOpened()): break;
    """
    if (not camera or not camera.isOpened()):
        print("Camera unavailable.")
        return

    with PoseLandmarker.create_from_options(options) as landmarker:
        hasRead, frame = camera.read()
        if not hasRead:
            print("Failed to read initial camera frame.")
            return
            
        fy, fx, _ = frame.shape
        detection.createDetections()
        
        while (shared.running):
            hasRead, frame = camera.read()
            if (not hasRead): # Just exit the camera stream entirely
                print("Frame not received. Removing video stream."); break
                
            frame = cv2.flip(frame, 1) #Flip camera horizontally
            time.sleep(0.01)

            # For some historical reason, cameras read in BGR so I have to convert it to RGB
            convertedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); 

            # Convert the frame received to a MediaPipe’s Image object.
            # This is Google's thing btw
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=convertedFrame)
            landmarker.detect_async(mp_image, int(time.time() * 1000))

            #Draw on last frame received, else receive first frame
            
            # I need a different way to exit from program!
            #if (cv2.waitKey(1) & 0xFF == ord('q')): break

    detection.cleanup()
    if camera: camera.release()
    cv2.destroyAllWindows()
