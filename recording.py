import cv2
import time
import datetime

class Recorder:
	def __init__(self):
		self.vw = None

	def __init__(self, filename):
		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		self.vw = cv2.VideoWriter(filename, fourcc, 20.0, (640,480))

	def createWriter(self, filename):
		self.vw = cv2.VideoWriter(filename, -1, 20.0, (640,480))	

	def recordFrame(self, frame):
		self.vw.write(frame)

	def destroy(self):
		self.vw.release()
