# Daniel Lillard
# 2025.12.03
# Takes a video, and outputs a dithered version of the video
# inspired by: https://www.youtube.com/watch?v=nvR8__cVifI


# ---------------
# expected command line args:
# python one_bit_video_ditherer.py input/video_name.mp4
# e.g.: python one_bit_video_ditherer.py input/knights_fighting.mp4
# ---------------

# ---------------
#   Imports
# ---------------
import subprocess
import os
import sys # for command line args

from one_bit_frames_ditherer import process_frame_folder

# --------------
#   Functions
# --------------
def video_to_frames(video_path):
    video_name = os.path.basename(video_path).split('.')[0]
    input_folder_path = os.path.dirname(video_path) + "\\" + video_name + "_frames\\"
    if not os.path.exists(input_folder_path):
        os.makedirs(input_folder_path)

    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
        input_folder_path + 'frame_%06d.png'
    ]

    subprocess.run(cmd, check=True)

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


# --------------
# For the TUI
# --------------
def dither_video(
    input_video_path: str,
    video_name: str,
    pixelation_factor: int = 12,
    random_factor: int = 8,
    divergence_factor: float = 4,
    divergence_point: float = 128.0,
    darker_color: str = "#000000",
    lighter_color: str = "#FFFFFF"
) -> None:
    video_to_frames(input_video_path)

    process_frame_folder(
        input_video_path,
        video_name,
        pixelation_factor,
        random_factor,
        divergence_factor,
        divergence_point,
        darker_color,
        lighter_color
    )

    frames_to_video(video_name)
# --------------
# Main Code
# --------------

def main():
    input_video_path = sys.argv[1]  # e.g., "input/knights_fighting.mp4"

    output_video_name = sys.argv[2]  # e.g., "knights_fighting_12"

    video_name = os.path.splitext(os.path.basename(input_video_path))[0]
    
    video_to_frames(input_video_path, video_name)

    # default parameters
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

    process_frame_folder(video_name, output_video_name, pixelation_factor, random_factor, divergence_factor, divergence_point, darker_color, lighter_color)

    frames_to_video(output_video_name)

if __name__ == "__main__":
    main()