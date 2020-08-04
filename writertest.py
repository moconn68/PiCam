import cv2
from recording import Recorder
import time

cap = cv2.VideoCapture(0)
tester = Recorder("test.mp4")
start = time.time()
end = start + 5

while end > time.time():
	ret, frame = cap.read()
	if ret:
		tester.recordFrame(frame)

cap.release()
tester.destroy()
