"""
camera_server.py: Flask server arbitrating local security camera via webcam. Includes motion detection and video file tranfer via network.
Inspired by Adrian Rosebrock (https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/)
"""
__author__ = "Matthew O'Connell"
__email__ = "mattgoconn@gmail.com"
__website__ = "https://github.com/moconn68"
__credits__ = ["Adrian Rosebrock"]

from motion_detection import MotionDetector
import config


from flask import Response
from flask import Flask
from flask import render_template

import threading
import argparse
import datetime
import time
import os
import shutil

import cv2

import imutils
from imutils.video import VideoStream

import requests
import ffmpy

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

vs = cv2.VideoCapture(0)
videoRecorder = None

recording = False
# in seconds
maxRecordTime = 30
# If time between detected motion exceeds this number, end current recording
recordMotionBufferTime = 2000
videoFileName = None
recordingStartTime = None

time.sleep(2.0)

@app.route('/')
def index():
	return render_template("index.html")

def detect_motion(frameCount):
	global vs, outputFrame, lock, recording, videoFileName, videoRecorder, recordingStartTime
	motionDetector = MotionDetector(accumWeight=0.1)
	totalFrames = 0
	timeLastMotion = None

	while True:
		ret, frame = vs.read()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)
		
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		if totalFrames > frameCount:
			motion = motionDetector.detect(gray)
			if motion is not None:
				# Motion detected; box & record
				timeLastMotion = time.time()
				if not recording:
					# start recording
					videoFileName = timestamp.strftime("%B%d%Y_%I:%M:%S%p")+'.avi'
					fourcc = cv2.VideoWriter_fourcc(*'XVID')
					frame_width = int(vs.get(3))
					frame_height = int(vs.get(4))
					videoRecorder = cv2.VideoWriter(videoFileName, fourcc, 20.0, (frame_width, frame_height,))
					videoRecorder.write(frame)
					recording = True
					recordingStartTime=time.time()
					print("recording block 1")
				elif time.time() - recordingStartTime < maxRecordTime:
					videoRecorder.write(frame)
					print("recording block 2")
				else:
					videoRecorder.release()
					send_video_file(videoFileName, timestamp)
#					print("videoFileName: " + videoFileName)
#					avi_to_mp4(videoFileName)
#					vidPath = create_video_folder(timestamp)
#					print("moving video to " + vidPath + videoFileName)
#					os.rename(videoFileName, vidPath + videoFileName)
#					shutil.move(os.path.abspath(videoFileName), vidPath + videoFileName)
#					os.system("mv " + videoFileName +  vidPath + videoFileName)
					videoRecorder = None
					videoFileName = None
					recordingStartTime = None
					recording = False
					print("recording stopped - time limit")

				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)
			
		motionDetector.update(gray)
		totalFrames += 1

		if recording and (time.time() - recordingStartTime >= maxRecordTime or time.time() - timeLastMotion >= 2):
			videoRecorder.release()
			send_video_file(videoFileName, timestamp)
#			print("videoFileName: " + videoFileName)
#			avi_to_mp4(videoFileName)
#			vidPath = create_video_folder(timestamp)
#			print("moving video to " + vidPath + videoFileName)
#			os.rename(videoFileName, vidPath + videoFileName)
#			shutil.move(os.path.abspath(videoFileName), vidPath + videoFileName)
#			os.system("mv " + videoFileName +  vidPath + videoFileName)
			videoRecorder = None
			videoFileName = None
			recordingStartTime = None
			recording = False
			print("recording stopped - no motion")

		with lock:
			outputFrame = frame.copy()

def send_video_file(filename, timestamp):
	with open(filename, 'rb') as f:
		try:
			r = requests.post("http://{}:{}/{}".format(config.file_server['ip'], config.file_server['port'], config.file_server['endpoints']['video']),
				files={filename: f},
				data={
					'filename': filename,
					'timestamp': timestamp
				}
			)
			if r.ok:
				os.remove(filename)
				print("File sent successfully to server")
			else:
				raise Exception("Request unsuccessful; file saved locally as {}".format(filename))
		except requests.ConnectionError:
			print("Error: could not connect to file server. Are you sure it is running and you have the right host & port configuration?")

#def create_video_folder(root_path, timestamp):
#	dirname = timestamp.strftime("%B%Y")
#	dirpath = root_path + dirname + '/'
#	os.makedirs(dirpath, exist_ok=True)
#	return dirpath

def create_video_folder(timestamp):
	root_path = config.video_folder_path
#	year = str(timestamp_string[0:4])
#	month = str(months[timestamp_string[5:7]])
#	day = str(timestamp_string[8:10]) 
#	dirpath = root_path + year + month + '/' + day + '/'
#	"%B%d%Y_%I:%M:%S%p"
	dirpath = root_path + timestamp.strftime("%Y%B") + '/' + timestamp.strftime("%d") + '/' 
	os.makedirs(dirpath, exist_ok=True)
	return dirpath

def avi_to_mp4(filename):
	global videoFileName
	mp4FileName = filename[0:len(filename)-3]+'mp4'
	ff = ffmpy.FFmpeg(
		inputs={filename: None},
		outputs={mp4FileName: None}
	)
	ff.run()
	os.remove(filename)
	videoFileName = mp4FileName
		
			
def stream_video():
	global vs, outputFrame, lock
	while True:
		ret, frame = vs.read()
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
	t = threading.Thread(target=detect_motion, args=(config.camera_server["frame_count"],))
	t.daemon = True
	t.start()
	app.run(host=config.camera_server["ip"], port=config.camera_server["port"], debug=True, threaded=True,
		use_reloader=False)
vs.release()
if videoRecorder:
	videoRecorder.release()
