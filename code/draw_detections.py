import cv2
import numpy as np
import time
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
from mediapipe.tasks.python import vision

# Visualisation stuffs, I got off Google's CoLab notebook
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

def drawDetection(frame, detections):
    """
    Notes to myself, after trial and error: So the structure of landmarks is structured like this
    Inside are list of 1-4 poses.
    Each pose has index 0-33 of actual landmarks.
    Each landmark has attributes x, y, z
    """
    fy, fx, _ = frame.shape
    for detect in detections:
        boundsX = (int(detect.x1 * fx), int(detect.x2 * fx))
        boundsY = (int(detect.y1 * fy), int(detect.y2 * fy))
        # Active is green (0), Inactive is red (1) in detect.colour tuple
        borderColour = detect.colour[0] if detect.isActive else detect.colour[1]
        cv2.rectangle(frame, (boundsX[0], boundsY[0]), (boundsX[1], boundsY[1]), borderColour, detect.thickness)
        
        # Add box label
        cv2.putText(frame, detect.name, (boundsX[0] + 5, boundsY[0] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, borderColour, 1, cv2.LINE_AA)
    return frame


def drawStatusOverlays(frame, isSoftDropping, isJumping, jumpStartTime, HDmessageTime, keysDict):
    fy, fx, _ = frame.shape

    # To you: Modify the height of soft drop and hard drop line here!
    # Multiplier 0 is top, 1 is bottom
    # I may make a slider thing
    SDline = int(fy / 2)
    HDline = int(fy * 2 / 3)
    
    # Draw the soft drop line and hard drop line
    cv2.line(frame, (0, SDline), (fx, SDline), (0, 165, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Crouch past this line to soft drop", (10, SDline - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1, cv2.LINE_AA)
    cv2.line(frame, (0, HDline), (fx, HDline), (255, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Jump past this line to hard drop", (10, HDline - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1, cv2.LINE_AA)
    
    SDcolour = (0, 255, 0) if isSoftDropping else (128, 128, 128)
    SDtext = "SOFT DROP" if isSoftDropping else "NO SOFT DROPPING"
    cv2.putText(frame, SDtext, (fx // 2 - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, SDcolour, 2, cv2.LINE_AA)

    now = time.time()
    if isJumping and jumpStartTime is not None:
        jump_duration = now - jumpStartTime
        HDtext = f"AIRBORNE ({jump_duration:.2f}s)"
        HDcolour = (0, 255, 255) # Yellow/Cyan
    elif now < HDmessageTime:
        HDtext = "HARD DROP"
        HDcolour = (255, 255, 0) # Cyan/Blue BGR
    else:
        HDtext = "NO HARD DROP"
        HDcolour = (0, 255, 0)
    cv2.putText(frame, f"JUMP STATE: {HDtext}", (fx // 2 - 100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, HDcolour, 2, cv2.LINE_AA)
    
    # Draw key bindings helper at bottom
    line1 = f"Rotate L: {keysDict['rotateL']} | Rotate R: {keysDict['rotateR']}"
    line2 = f"Move L: {keysDict['moveL']} | Move R: {keysDict['moveR']}"
    line3 = f"Soft Drop: {keysDict['softdrop']} | Hard Drop: {keysDict['harddrop']}"
    
    cv2.putText(frame, line1, (20, fy - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(frame, line2, (20, fy - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(frame, line3, (20, fy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
    
    return frame
