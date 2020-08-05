camera_server = {
	"ip": "192.168.1.234",
	"port": 8080,
	"frame_count": 32,
}

file_server = {
	"ip": "192.168.1.234",
	"port": 9000,
	"paths": {
		"videos": "./videos/"
	},
	"endpoints": {
		"video": "video_intake"
	}
}

video_folder_path = "/media/pi/massive/videos/"
#video_folder_path = "videos/"
