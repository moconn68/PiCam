camera_server = {
	"ip": "192.168.1.10",
	"port": 8080,
	"frame_count": 32,
}

file_server = {
	"ip": "192.168.1.10",
	"port": 9000,
	"paths": {
		"videos": "./videos/"
	},
	"endpoints": {
		"video": "video_intake"
	}
}
