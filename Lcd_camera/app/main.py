# -*- coding: UTF-8 -*-
import os
import sys 
import time
import logging
import spidev as SPI
import cv2
import numpy as np
from PIL import Image
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

# Initialize display with hardware SPI
disp = LCD_1inch5.LCD_1inch5()
disp.Init()
disp.clear()

# Setup camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (disp.width, disp.height)}))
picam2.start()

logging.info("Starting camera preview")

# Define two effects
def apply_none(frame):
    return frame

def apply_aqua_tone(frame):
    # Check if the frame has 3 channels
    if frame.shape[2] == 3:  # Ensure it's an RGB frame
        aqua_filter = np.array([0.8, 1.0, 1.2])  # Adds a bluish tint
        frame_aqua = cv2.multiply(frame, aqua_filter)
        frame_aqua = np.clip(frame_aqua, 0, 255).astype(np.uint8)
        return frame_aqua
    else:
        # If the frame is not in RGB, just return it without applying the effect
        logging.warning("Frame is not RGB, skipping aqua tone effect")
        return frame

# List of effects
effects = [apply_none, apply_aqua_tone]
effect_names = ['Normal', 'Aqua Tone']
effect_index = 0

# Variables for gesture recognition
prev_x = None
gesture_threshold = 80

try:
    while True:
        # Capture image from the camera
        frame = picam2.capture_array()
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally

        # Apply current effect
        frame_effect = effects[effect_index](frame)

        # Convert to PIL image and display on LCD
        frame_pil = Image.fromarray(cv2.cvtColor(frame_effect, cv2.COLOR_BGR2RGB))
        disp.ShowImage(frame_pil)

        # Gesture-based effect switching (simulated simple swipe gesture)
        current_x = np.random.randint(0, 240)  # Replace this line with hand tracking input for x-coordinate
        if prev_x is not None:
            delta_x = current_x - prev_x
            if delta_x > gesture_threshold:
                effect_index = (effect_index + 1) % len(effects)
                logging.info(f'Switched to effect: {effect_names[effect_index]}')
            elif delta_x < -gesture_threshold:
                effect_index = (effect_index - 1) % len(effects)
                logging.info(f'Switched to effect: {effect_names[effect_index]}')

        prev_x = current_x
        time.sleep(0.1)

except KeyboardInterrupt:
    disp.clear()
    logging.info("Exiting program")
    exit()
