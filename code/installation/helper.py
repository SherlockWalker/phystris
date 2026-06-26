"""
# Prototype for video stream, which uh kinda worked
import cv2
camera = cv2.VideoCapture(2) #My camera is broken I'm using my stupid fisheye webcam
ret, frame = camera.read()
cv2.imshow("camera", frame)
cv2.waitKey(0)
"""

# Script to download the model task; I have no need for it anymore
import urllib.request
urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task", \
                           "pose_landmarker.task")
