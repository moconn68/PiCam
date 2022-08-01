# PiCam

## What's This?
PiCam is a mini pet project I undertook for a short while between my graduation from college and the start of my full time employment the summer of 2020. It is a toy implementation of a "smart" home security camera system that uses machine learning via OpenCV to detect motion on a webcam and automatically trigger a video recording which is then saved to disk. The application also exposes a live web view of the camera that can be viewed at any time.

This was mostly an exercise in gaining a greater understanding of the Python language, working with my brand new Raspberry Pi's, learning more about machine learning via OpenCV, and finding a use for an old webcam and external HDD which had both been collecting dust for a while. In it's current state it is perfectly functional but likely misses a large amount of edge cases and is nowhere near robustly configured nor secured, as the live web view operates purely on open port forwarding. I do not advise the use of this project as an actual method of home security, and it should only be used as a fun hobby project to explore the aforementioned topics. 

## Raspberry Pi System Configuration 
1. Install Raspberry Pi OS
2. Set up system
3. Enable SSH
4. Set Static IP on raspberry pi [guide here](https://thepihut.com/blogs/raspberry-pi-tutorials/how-to-give-your-raspberry-pi-a-static-ip-address-update)
5. Video server 
	+ mount external drive
```
mkdir /mnt/<mounted_name>
sudo mount <drive_location(ie /dev/sda1)> /mnt/<mounted_name>
sudo vi /etc/fstab -> enter in info about drive
	Looks something like:
	/dev/sda1  /mnt/<mounted_name>  vfat  umask=000  0  0
mkdir /mnt/<mounted_name>/videos
ln -s /mnt/<mounted_name>/videos <PiCam Dir>/videos
```
	+ Use Samba to share video folder
```
sudo apt install samba
sudo vi /etc/samba/smb.conf -> add to end:
	[videos]
	Comment = Camera recorded videos 
	Path = /mnt/<mounted_name>/videos
	Browseable = yes
	Writeable = Yes
	only guest = no
	create mask = 0777
	directory mask = 0777
	Guest ok = yes

```


## Installing Dependencies (Raspberry Pi)
1. Must have Raspberry Pi OS installed! (it no ubuntu etc.) due to piwheels availability for ARM
2. Need additional system-level dependencies for OpenCV to work:
```
sudo apt update
sudo apt upgrade
sudo apt-get install libcblas-dev;
sudo apt-get install libhdf5-dev;
sudo apt-get install libhdf5-serial-dev;
sudo apt-get install libatlas-base-dev;
sudo apt-get install libjasper-dev; 
sudo apt-get install libqtgui4; 
sudo apt-get install libqt4-test;
```
3. Install python dependencies - not you must use the versions specified in requirements_pi.txt especially opencv!
```
source venv/bin/activate
pip install -r requirements_pi.txt
```
