"""
motion_detection.py: Uses OpenCV and background subtraction to detect motion in video. 
Inspired by Adrian Rosebrock (https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/)
"""
__author__ = "Matthew O'Connell"
__email__ = "mattgoconn@gmail.com"
__website__ = "https://github.com/moconn68"
__credits__ = ["Adrian Rosebrock"]

import numpy as np
import imutils
import cv2

class MotionDetector:
	def __init__(self, accumWeight=0.5):
		self.accumWeight = accumWeight
		self.bgModel = None

	def update(self, image):
		# if model is none, needs to be initialized with image
		if self.bgModel is None:
			self.bgModel = image.copy().astype("float")
			return

		# update model with new average
		cv2.accumulateWeighted(image, self.bgModel, self.accumWeight)

	def detect(self, image, tVal=25):
		# difference between model and image
		delta = cv2.absdiff(self.bgModel.astype("uint8"), image)
		# threhold image
		thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]
		# erosions & dilations to remove small artifacts	
		thresh = cv2.erode(thresh, None, iterations=2)
		thresh = cv2.dilate(thresh, None, iterations=2)

		# find thresholded image's contours & intialize min & max bounding boxes
		contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		contours = imutils.grab_contours(contours)
		(minX, minY) = (np.inf, np.inf)
		(maxX, maxY) = (-np.inf, -np.inf)
		
		if len(contours) == 0:
			return None
		for c in contours:	
			(x, y, w, h) = cv2.boundingRect(c)
			(minX, minY) = (min(minX, x), min(minY, y))
			(maxX, maxY) = (max(maxX, x+w), max(maxY, y+h))

		return (thresh, (minX, minY, maxX, maxY))
