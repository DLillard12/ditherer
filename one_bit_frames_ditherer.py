# Daniel Lillard
# 2025.05.19
# This is a small project to pixilate an image and turn in b & w
# inspired by: https://www.youtube.com/watch?v=nvR8__cVifI

# ---------------
#   Imports
# ---------------
import numpy as np
from PIL import Image
import os
import sys # for command line args
import os.path # for putting input and output in the right place
import subprocess # for ffmpeg calls

from one_bit_image_ditherer import (process_frame)


# --------------
#   Constants
# --------------

# --------------
# Functions
# --------------

# this function is also in the one_bit_video_ditherer,
# it would be best to make a shared function for this, but for now it is duplicated.
def frames_to_video(video_name):
    cmd = [
    'ffmpeg',
    '-framerate', '30',
    '-i', 'output/'+ video_name +'_frames/frame_%06d.png',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
    'output/'+ video_name +'.mp4'
    ]

    subprocess.run(cmd, check=True)

# logic is held in one_bit_image_ditherer.py to process each frame

def process_frame_folder(input_video_path: str, processed_video_name: str, pixelation_factor: int, random_factor: int, divergence_factor: float, divergence_point: float, darker_color: str, lighter_color: str):
    # if video, add frames folder
    # if frames folder, do not.

    if (input_video_path.endswith('.mp4') or input_video_path.endswith('.avi') or input_video_path.endswith('.mkv')):
        input_video_name = os.path.basename(input_video_path).split('.')[0]
        input_folder_path = os.path.dirname(input_video_path) + "\\" + input_video_name + "_frames\\"
    else:
        input_folder_path = input_video_path
    
    output_video_path = "output\\" + processed_video_name + "_frames\\"

    if not os.path.exists(output_video_path):
        os.makedirs(output_video_path)

    for fname in sorted(os.listdir(input_folder_path)):

        if not fname.endswith('.png'):
            continue
        
        path = os.path.join(input_folder_path, fname)
        img = Image.open(path).convert('L')

        final_image = process_frame(img, pixelation_factor, random_factor, divergence_factor, divergence_point, darker_color, lighter_color)
    
        final_image.save(os.path.join(output_video_path, fname))


# this is for the TUI
def dither_frames(
    input_video_path: str,
    processed_video_name: str,
    pixelation_factor: int = 12,
    random_factor: int = 8,
    divergence_factor: float = 4,
    divergence_point: float = 128.0,
    darker_color: str = "#000000",
    lighter_color: str = "#FFFFFF"
) -> None:
    process_frame_folder(input_video_path, processed_video_name, pixelation_factor, random_factor, divergence_factor, divergence_point, darker_color, lighter_color)
    
    # need to somehow make the video.
    frames_to_video(processed_video_name)

# --------------
# Main Code
# --------------


def main():
    #"input\\*_frames\\" Just need to put the frames name here
    input_video_path = "input\\" + sys.argv[1] + "_frames\\" 
    output_video_path = "output\\" + sys.argv[2] + "_frames\\"

    if not os.path.exists(output_video_path):
        os.makedirs(output_video_path)

    # default parameters
    # from here to the end we could possible make a shared
    # function for all the ditherers, as it is the same.
    pixelation_factor = 12
    random_factor = 8
    divergence_factor = 4
    divergence_point = 128.0
    darker_color = "#000000"
    lighter_color = "#FFFFFF"

    if len(sys.argv) >= 4:
        pixelation_factor = int(sys.argv[3])
    if len(sys.argv) >= 5:
        random_factor = int(sys.argv[4])
    if len(sys.argv) >= 6:
        divergence_factor = float(sys.argv[5])
    if len(sys.argv) >= 7:
        divergence_point = float(sys.argv[6])
    if len(sys.argv) >= 8:
        darker_color = sys.argv[7]
    if len(sys.argv) >= 9:
        lighter_color = sys.argv[8]
    

    process_frame_folder(sys.argv[1], pixelation_factor, random_factor, divergence_factor, divergence_point, darker_color, lighter_color)

if __name__ == "__main__":
    main()