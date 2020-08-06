# TODO

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
