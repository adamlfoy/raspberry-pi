# Configuring the system image

*ROVERS* system image is a modified version of *Rasbpbian Stretch with desktop 4.14*. Each modification is further described to allow replication and re-configuration of the system.

## Modifications

Here is a full list of changes introduced to the system. Naturally, before installing any of them you should `update` and `upgrade` your system via `apt-get`.

1. `VNC`, `SSH` activation
2. `Python3.6` installation
3. *Python* libraries installation via `pip`
4. Server start on boot
5. `OpenCV` installation (pending)

### 1. VNC-SSH-activation

- Launch Raspberry Pi Configuration from the *Preferences* menu
- Navigate to the *Interfaces* tab
- Enable *SSH* and *VNC*

### 2. Python3.6 installation

Run the following block of commands:

```commandline
sudo apt-get install build-essential checkinstall
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
sudo -i
cd /usr/src
wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
tar xzf Python-3.6.4.tgz
cd Python-3.6.4
bash configure
make altinstall
```

### 3. Python libraries installation via pip

Run the following block of commands:

```commandline
sudo python3.6 -m pip install --upgrade pip
sudo python3.6 -m pip install diskcache
sudo python3.6 -m pip install pyserial
sudo python3.6 -m pip install pathos
```

### 4. Server start on boot

1. Run the following command:

```commandline
sudo nano /etc/rc.local
```

2. Add the following line to the file (before the default script which can print IP):

```
sudo python3.6 /home/pi/Desktop/ROV/main.py 2> /home/pi/Desktop/ROV/error_log &
```

Example file content:

```
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Run the server
sudo python3.6 /home/pi/Desktop/ROV/main.py & 2> /home/pi/Desktop/ROV/error_log

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
printf "My IP address is %s\n" "$_IP"
fi

exit 0
```

3. Add the following `startup.service` file into `/etc/systemd/system`:

```
[Unit]
Description=Running /etc/rc.local
ConditionPathExists=/etc/rc.local

[Service]
Type=forking
ExecStart=/bin/sh /etc/rc.local start
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

4. Run the following block of commands:

```commandline
sudo systemctl daemon-reload
sudo systemctl enable startup.service
```

Sources:

1. https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/

2. https://www.raspberrypi.org/documentation/linux/usage/systemd.md

### 5. OpenCV installation

Installation of OpenCV is done by generally following this guide: https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/ with the following steps having modifications.

1. Step #4

Skip the majority of Step #4. Do not create a virtual environment and instead install numpy using the following command:
```commandline
sudo python3.6 -m pip install numpy
```
2. Step #5

When compiling consider using the following command:
```commandline
make -j3
```
This will only use 3 cores instead of all 4 which the guide prescribes. This is done because using all 4 cores is likely to cause the pi to freeze while compiling while using 3 leaves a single core for other threads to run on. Allowing for the monitoring of the compilation much more easily.

Also be aware that the compilation can take up to 3 hours to complete because the pi will spend a lot of time swapping things between swap space and memory. Be patient if it looks like the process has hung, it likely hasn't but is swapping things in and out of memory.

3. Step #6

Skip step #6 as described in the guide.
Instead of linking to the virtual environment instead link to the python 3.6 installation.

```commandline
cd /usr/local/lib/python3.6/site-packages/
ln -s /usr/local/python/cv2/python-3.5/cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so
```
