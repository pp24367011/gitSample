#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys 
import time
import logging
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2

sys.path.append("..")
from lib import LCD_1inch5

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0 
device = 0 

logging.basicConfig(level=logging.DEBUG)

try:
    # Initialize display with hardware SPI
    disp = LCD_1inch5.LCD_1inch5()
    disp.Init()
    disp.clear()

    # Create a blank image for drawing
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)

    # Draw some shapes
    draw.rectangle((15,10,6,11), fill="BLACK")
    draw.rectangle((15,25,7,27), fill="BLACK")
    draw.rectangle((15,40,8,43), fill="BLACK")
    draw.rectangle((15,55,9,59), fill="BLACK")
    disp.ShowImage(image1)
    time.sleep(1)

    # Setup camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (disp.width, disp.height)}))
    picam2.start()

    logging.info("Starting camera preview")
    
    while True:
        # Capture image from the camera
        frame = picam2.capture_array()
        
        # Convert the frame to an image compatible with the display
        img = Image.fromarray(frame)
        img = img.rotate(0)  # Rotate if necessary

        # Display the camera frame on the LCD
        disp.ShowImage(img)
        time.sleep(0.1)

except IOError as e:
    logging.error(e)
except KeyboardInterrupt:
    disp.clear()
    logging.info("Exiting program")
    exit()
