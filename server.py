"""
server.py: Flask server arbitrating local security camera via webcam. Includes motion detection capabilities.
Inspired by Adrian Rosebrock (https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/)
"""
__author__ = "Matthew O'Connell"
__email__ = "mattgoconn@gmail.com"
__website__ = "https://github.com/moconn68"
__credits__ = ["Adrian Rosebrock"]

from motion_detection import MotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

#vs = VideoStream(src=0).start()
vs = cv2.VideoCapture(0)
time.sleep(2.0)

@app.route('/')
def index():
	return render_template("index.html")

def detect_motion(frameCount):
	global vs, outputFrame, lock
	
	motionDetector = MotionDetector(accumWeight=0.1)
	totalFrames = 0
	while True:
		ret, frame = vs.read()
		frame = imutils.resize(frame, width=1000)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		if totalFrames > frameCount:
			motion = motionDetector.detect(gray)
			if motion is not None:
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)
			
		motionDetector.update(gray)
		totalFrames += 1
		
		with lock:
			outputFrame = frame.copy()
		
			
def stream_video():
	global vs, outputFrame, lock
	while True:
#		frame = vs.read()
#		frame = imutils.resize(frame, width=1000)
		ret, frame = vs.read()
#		frame = cv2.resize(frame, (1000,1000), interpolation=cv2.INTER_AREA)
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
		with lock:
			outputFrame = frame.copy()
			

def generate():
	global outputFrame, lock
	while True:
		with lock:
			if outputFrame is None:
				continue
			
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			if not flag:
				continue
			
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route('/video_feed')
def video_feed():
	return Response(generate(),
		mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())

	t = threading.Thread(target=detect_motion, args=(args["frame_count"],))
#	t = threading.Thread(target=stream_video)
	t.daemon = True
	t.start()

	app.run(host=args["ip"], port=args["port"], debug=True, threaded=True,
		use_reloader=False)

vs.stop()
