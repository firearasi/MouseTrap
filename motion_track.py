#!/usr/bin/env python3

"""
motion-track ver 0.6 written by Claude Pageau pageauc@gmail.com
Raspberry (Pi) - python opencv2 motion tracking using picamera module

This is a raspberry pi python opencv2 motion tracking demonstration program.
It will detect motion in the field of view and use opencv to calculate the
largest contour and return its x,y coordinate.  I will be using this for
a simple RPI robotics project, but thought the code would be useful for 
other users as a starting point for a project.  I did quite a bit of 
searching on the internet, github, etc but could not find a similar
implementation that returns x,y coordinates of the most dominate moving 
object in the frame.  Some of this code is base on a YouTube tutorial by
Kyle Hounslow using C here https://www.youtube.com/watch?v=X6rPdRZzgjg

Here is a my YouTube video demonstrating this demo program using a 
Raspberry Pi B2 https://youtu.be/09JS7twPBsQ

Requires a Raspberry Pi with a RPI camera module installed and configured
dependencies

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-opencv python-picamera

"""
print("motion3-track.py using python3 and OpenCV3")
print("Loading Please Wait ....")
import io
import time
#import datetime
import picamera
import picamera.array
import cv2
import numpy as np
import subprocess

# Add --gui option for GUI environment and remote_host
import argparse
parser=argparse.ArgumentParser(prog="motion-track",prefix_chars='-')
parser.add_argument('--gui',action="store_true")
parser.add_argument('-c','--canny',action="store_true")
parser.add_argument('-f','--facedetect',action="store_true")
parser.add_argument('-r','--remote_host',help="Transmit tracking photo to this remote host")
parser.add_argument('-t','--threshold',help="Photo taking threshold in seconds",type=float,default=1.5)

args=parser.parse_args()
remote_host=args.remote_host
if(remote_host):
  print("Sending motion tracking pictures to remote host:",remote_host)
  remote_dir="firearasi@"+remote_host+":/home/firearasi/Pictures/cv"

debug = True       # Set to False for no data display
window_on = args.gui   # Set to True displays opencv windows (GUI desktop reqd)

# Camera Settings
CAMERA_WIDTH = 1280*2//3
CAMERA_HEIGHT = 768*2//3
CAMERA_HFLIP = True
CAMERA_VFLIP = True
CAMERA_FRAMERATE=24

# Motion Tracking Settings
THRESHOLD_SENSITIVITY = 25
BLUR_SIZE = 10
MIN_AREA = 25     # excludes all contours less than or equal to this Area
CIRCLE_SIZE = 25  # diameter of circle to show motion location in 
THRESHOLD_CONSECUTIVE_FOUND=int(CAMERA_FRAMERATE * args.threshold)

def show_FPS(start_time,frame_count):
  if debug:
    if frame_count >= 10:
      duration = float(time.time() - start_time)
      FPS = float(frame_count / duration)
      print("Processing at %.2f fps last %i frames" %( FPS, frame_count))
      frame_count = 0
      start_time = time.time()
    else:
        frame_count += 1
  return start_time, frame_count

if args.facedetect:
  eye_data=cv2.CascadeClassifier('haarcascades/haarcascades_eye.xml')
  mouth_data=cv2.CascadeClassifier('haarcascades/haarcascades_mcs_mouth.xml')
  face_data=cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
  
  def face_detect(img,factor_down=0.33):
    factor_up=1/factor_down
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    small_gray=cv2.resize(gray,(0,0),fx=factor_down,fy=factor_down)
    
    faces=face_data.detectMultiScale(small_gray,1.3,5)
    for (face_x,face_y,face_w,face_h) in faces:
      (x,y,w,h)=(face_x*factor_up,face_y*factor_up,face_w*factor_up,face_h*factor_up)
      cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    return img
    


def canny(img):
  edges=cv2.Canny(img,100,200)
  return edges
def corner_harris(img):
  gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  gray=np.float32(gray)
  dst=cv2.cornerHarris(gray,2,3,0.04)
  dst=cv2.dilate(dst,None)
  
  out=np.copy(img)
  out[dst>0.01*dst.max()]=[0,0,255]
  return out

def motion_track():
  print("Initializing Camera ....")
  # Save images to an in-program stream
  stream = io.BytesIO()
  with picamera.PiCamera() as camera:
    camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
    camera.hflip = CAMERA_HFLIP
    camera.vflip = CAMERA_VFLIP
    camera.framerate=CAMERA_FRAMERATE
    time.sleep(0.2)
    first_image = True
    if window_on:
      print("press Ctrl-C to quit opencv display")
    else:
      print("press q to quit")        
    print("Start Motion Tracking ....")

    frame_count = 0
    start_time = time.time()
    
    start_time, frame_count = show_FPS(start_time, frame_count)
    consecutive_found = 0
    
    stream=picamera.array.PiRGBArray(camera)
    for frame in camera.capture_continuous(stream,format='bgr',use_video_port=True):
      # initialize variables         
      motion_found = False
      
      biggest_area = MIN_AREA
      cx = 0
      cy = 0
      cw = 0
      ch = 0
      image2 = frame.array
      stream.truncate(0)
      # At this point the image is available as stream.array
      if first_image:
      # initialize image1 using image2 (only done first time)
        image1 = image2
        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        first_image = False
      else:
        # Convert to gray scale, which is easier
        grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # Get differences between the two greyed, blurred images
        differenceimage = cv2.absdiff(grayimage1, grayimage2)
        differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))
        # Get threshold of difference image based on THRESHOLD_SENSITIVITY variable
        retval, thresholdimage = cv2.threshold(differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY)
        # Get all the contours found in the thresholdimage
        # syntax for opencv2
        #contours,hierarchy = cv2.findContours(thresholdimage,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # syntax for opencv3
        thresholdimage,contours,hierarchy = cv2.findContours(thresholdimage,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
          #contours = cv2.findContours(thresholdimage,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        total_contours = len(contours)
        # save grayimage2 to grayimage1 ready for next image2
        grayimage1 = grayimage2
        # find contour with biggest area
        for c in contours:
            # get area of next contour
          found_area = cv2.contourArea(c)
          # find the middle of largest bounding rectangle
          if found_area > biggest_area:
            motion_found = True
            consecutive_found += 1
            biggest_area = found_area
            (x, y, w, h) = cv2.boundingRect(c)
            cx = int(x + w/2)   # put circle in middle of width
            cy = int(y + h/6)   # put circle closer to top
            cw = w
            ch = h
        if motion_found:
          # Do Something here with motion data 
          if window_on:
            # show small circle at motion location 
            cv2.circle(image2,(cx,cy),CIRCLE_SIZE,(0,255,0),2)
          if consecutive_found>=THRESHOLD_CONSECUTIVE_FOUND:
            print("Significant motions tracked @ %s" % time.ctime())
            consecutive_found = 0 # reset
            if not window_on:
              cv2.circle(image2,(cx,cy),CIRCLE_SIZE,(0,255,0),2) # add circle around motion anyway
            cv2.imwrite("motion.png",image2)
             
            if remote_host:
              subprocess.run(["scp","motion.png",remote_dir])
            if args.canny: #whether to use canny edge detection
              cv2.imwrite("motion_canny.png",canny(image2))  
              if remote_host:
                subprocess.run(["scp","motion_canny.png",remote_dir])

            if args.facedetect:
              cv2.imwrite("motion_face.png",face_detect(image2))
              if remote_host:
                subprocess.run(["scp","motion_face.png",remote_dir])
          if debug:
            print("total_Contours=%2i  Motion at cx=%3i cy=%3i   biggest_area:%3ix%3i=%5i" % (total_contours, cx ,cy, cw, ch, biggest_area))
        else:
          consecutive_found = 0
        if window_on:
            # cv2.imshow('Difference Image',differenceimage) 
          cv2.imshow('Threshold Image', thresholdimage)
          cv2.imshow('Movement Status', image2)
          # Close Window if q pressed
          if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            print("End Motion Tracking")
            break
    
motion_track()
  
