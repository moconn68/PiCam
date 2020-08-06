"""
file_server.py: Flask server arbitrating network storage system. 
Primarily serves to accept, parse, and store video files from a custom security camera
"""
__author__ = "Matthew O'Connell"
__email__ = "mattgoconn@gmail.com"
__website__ = "https://github.com/moconn68"

from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import shutil
import time
import datetime
import sched
import threading
import ffmpy
import config
app = Flask(__name__)

months = {
	"01": "January",
	"02": "February",
	"03": "March",
	"04": "April",
	"05": "May",
	"06": "June",
	"07": "July",
	"08": "August",
	"09": "September",
	"10": "October",
	"11": "November",
	"12": "December"
}

s = sched.scheduler(time.time, time.sleep)

dtOldestFolder = None
freeStorageWaitTime = 10 *60

def next_month(dt):
	if dt.month <= 11:
		return dt.month +1
	else:
		return 1

def free_storage():
	global dtOldestFolder
	print("freeing storage")
	# only perform if storage usage >=95%
	if shutil.disk_usage(config.video_folder_path).used / shutil.disk_usage(config.video_folder_path).total >= 0.95:
		# delete the oldest folder
		shutil.rmtree(config.video_folder_path + dtOldestFolder.strptime("%B%Y"))
		# then update dtOldestFolder to be the next month	
		nextMonthDate = None
		try:
			nextMonthDate = dtOldestFolder.replace(month=dtOldestFolder.month+1, day=1)
		except ValueError:
			if dtOldestFolder.month == 12:
				nextMonthDate = dtOldestFolder.replace(year=dtOldestFolder.year+1, month=1, day=1)	
		dtOldestFolder = nextMonthDate
	s.enter(freeStorageWaitTime, 1, free_storage)

def schedule_clean():
	s.enter(freeStorageWaitTime, 1, free_storage)
	s.run()

def create_video_folder(timestamp_string):
#	root_path = config.file_server['paths']['videos']
	root_path = config.video_folder_path
	print(timestamp_string)
	year = str(timestamp_string[0:4])
	month = str(months[timestamp_string[5:7]])
	day = str(timestamp_string[8:10]) 
	dirpath = root_path + year + month + '/' + day + '/'
	os.makedirs(dirpath, exist_ok=True)
	return dirpath

def avi_to_mp4(filename):
	mp4FileName = filename[0:len(filename)-3]+'mp4'
	ff = ffmpy.FFmpeg(
	    inputs={filename: None},
	    outputs={mp4FileName: None}
	)
	ff.run()
	os.remove(filename)
	return mp4FileName


@app.route('/')
def index():
	return None

@app.route('/video_intake', methods=['POST'])
def receive_video():
	global dtOldestFolder
	name = request.form['filename']
	timestamp = request.form['timestamp']
	print(timestamp)
#	if not dtOldestFolder:
#		dtOldestFolder = datetime.strptime(timestamp, "%")
	f = request.files[name]
	print("file received: " + name)
	recordingPath = create_video_folder(timestamp)
	print("recordingPath: " + recordingPath)
	video_path = recordingPath + secure_filename(f.filename)
	print("video_path: " + video_path)
	f.save(video_path)
#	avi_to_mp4(video_path)	
	return "file saved" 

if __name__=="__main__":
	#app.run(port="9000", debug=True)
	t = threading.Thread(target=schedule_clean)
	t.start()
	app.run(host=config.file_server["ip"], port=config.file_server["port"], debug=True, threaded=True,
		use_reloader=False)
