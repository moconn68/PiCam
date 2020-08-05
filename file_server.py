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
import time
import datetime
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

def create_video_folder(timestamp_string):
	root_path = config.file_server['paths']['videos']
	print(timestamp_string)
	year = str(timestamp_string[0:4])
	month = str(months[timestamp_string[5:7]])
	day = str(timestamp_string[8:10]) 
	dirpath = root_path + year + month + '/' + day + '/'
	os.makedirs(dirpath, exist_ok=True)
	return dirpath

def avi_to_mp4(filename):
    ff = ffmpy.FFmpeg(
        inputs={filename: None},
        outputs={filename[0:len(filename)-3]+'mp4': None}
    )
    ff.run()
    os.remove(filename)


@app.route('/')
def index():
	return None

@app.route('/video_intake', methods=['POST'])
def receive_video():
	name = request.form['filename']
	timestamp = request.form['timestamp']
	f = request.files[name]
	recordingPath = create_video_folder(timestamp)
	video_path = recordingPath + f.filename
	f.save(video_path)
	avi_to_mp4(video_path)	
	return "file saved" 

#app.run(port="9000", debug=True)
app.run(host=config.file_server["ip"], port=config.file_server["port"], debug=True, threaded=True,
	use_reloader=False)
