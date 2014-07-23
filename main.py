#!/usr/bin/python

import StringIO
import subprocess
import datetime
import math
import sys

from PIL import Image
from PIL import ImageChops

# RASPBERRY PI MOTION DETECTOR
# Author: KoffeinFlummi

# DESCRIPTION
# Takes continuous low-res pictures and compares them to detect
# motion. When movment is detected, a full-res picture is taken
# and stored with a time stamp in the capture folder.

# USAGE
# sudo python main.py    => default treshold (5)
# sudo python main.py 10 => custom treshold (10)

frames = []
debug = False

def get_difference(image1, image2):
  """ Compares 2 PIL images and returns the difference as a numerical value. """
  histogram = ImageChops.difference(image1, image2).histogram()
  histogram_sum = sum(histogram)
  samples_probability = [float(h) / histogram_sum for h in histogram]
  return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])

def check_for_movement():
  """ Checks the last 2 frames for movement. """
  global frames
  if len(frames) < 2:
    return 0
  image1 = frames.pop(0)
  image2 = frames[0]
  return get_difference(image1, image2)

def take_test_picture():
  """ Takes a low-res picture used to check for movement. """
  global frames
  command = "raspistill -w 160 -h 90 -t 200 -e bmp -n -o -"
  imageData = StringIO.StringIO()
  imageData.write(subprocess.check_output(command, shell=True))
  imageData.seek(0)
  frames.append(Image.open(imageData))

def take_full_picture():
  """ Takes a (relatively) high-res picture to catch whatever is moving. """
  time = datetime.datetime.now()
  filename = "capture/%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
  subprocess.call("raspistill -w 1280 -h 720 -t 200 -e jpg -q 20 -n -o %s" % (filename), shell=True)

def main():
  treshold = 5
  if len(sys.argv) > 1:
    treshold = float(sys.argv[1])

  while True:
    take_test_picture()
    movement = check_for_movement()
    if debug:
      print movement
    if movement > treshold:
      if debug:
        print "Movement detected."
      take_full_picture()

main()
