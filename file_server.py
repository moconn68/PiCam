from flask import Flask, request
from werkzeug.utils import secure_filename
app = Flask(__name__)

@app.route('/')
def index():
	return None

@app.route('/video_intake', methods=['POST'])
def receive_video():
	print(request.files)
	print(request.form)
	name = request.form['filename']
	f = request.files[name]
	f.save("./videos/" + secure_filename(f.filename)) 
#	return "file saved" 
	with open(f.filename) as fileFinal:
		return fileFinal


app.run(port="9000", debug=True)
	
