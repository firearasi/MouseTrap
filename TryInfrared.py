#!/usr/bin/python

import time
import argparse
import subprocess
import picamera
CAMERA_WIDTH=1024
CAMERA_HEIGHT=768
CAMERA_HFLIP=True
CAMERA_VFLIP=True

parser=argparse.ArgumentParser(prog="TryInfrared",prefix_chars='-')
parser.add_argument('-i','--interval',type=int,default=60,help="Photo taking interval in seconds")
parser.add_argument('-r','--remote_host',help="Transmit tracking photo \
  to this")


args=parser.parse_args()


try:
  while True:
    with picamera.PiCamera() as camera:
      camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
      camera.hflip = CAMERA_HFLIP
      camera.vflip = CAMERA_VFLIP
      filename="footageAt%s.png"%(int(time.time()))  
      camera.capture(filename)
      print("Photo saved:%s"%filename)
      
      if args.remote_host is not None:
        subprocess.call(['scp',filename,args.remote_host])
    time.sleep(args.interval)
except KeyboardInterrupt:
  pass
