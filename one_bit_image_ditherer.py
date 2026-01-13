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


# --------------
#   Constants
# --------------

b = 255
w = 0
patterns = np.array([
    [[w,w,w],[w,w,w],[w,w,w]],        # bucket 0
    [[w,w,w],[w,b,w],[w,w,w]],      # bucket 1
    [[b,w,b],[w,w,w],[b,w,b]],# bucket 2
    [[w,b,w],[b,b,b],[w,b,w]], # bucket 3
    [[b,b,b],[b,w,b],[b,b,b]], # bucket 4
    [[b,b,b],[b,b,b],[b,b,b]] # bucket 5
], dtype=np.uint8)

# --------------
# Functions
# --------------

def bucket_index(img):
    bins = np.array([43, 85, 128, 170, 213, 256])
    return np.digitize(img, bins)     # shape: (H, W)

def pixelate(pixelation_factor: int , img: Image):
    tiny = img.resize(size=[int(img.width/pixelation_factor),int(img.height/pixelation_factor)])
    return tiny

# this function takes a value, and moves it from its position away from 128
def pixel_divergence(img_arr: np.array, divergence_factor: float, divergence_point: float = 128.0):
    # center the values around 0
    centered = img_arr - divergence_point
    # scale by divergence factor
    scaled = centered * divergence_factor
    # re-center around 128
    re_centered = scaled + divergence_point
    # clip to valid range
    clipped = np.clip(re_centered, 0, 255)
    return clipped.astype(np.uint8)
    

def add_random_pixels(img_array: np.array, random_factor: int):
    # Generate the random pixel coordinates
    rng = np.random.default_rng()
    H, W = img_array.shape
    num_random_pixels = int(random_factor**1.5)
    random_pixels = rng.integers(0, [H, W], size=(num_random_pixels,2))
    
    # separate into x and y coords
    x_coords = random_pixels[:, 0]
    y_coords = random_pixels[:, 1]

    # now set those pixels to random black or white
    img_array[x_coords, y_coords] = np.random.choice([0, 255], size=random_pixels.shape[0])

    return img_array


def expand_pixels(img_array):
    img_array = img_array.astype(np.uint8)

    idx = bucket_index(img_array)        # (H, W)
    mapped = patterns[idx]               # (H, W, 3, 3)
    H, W = img_array.shape

    mapped = mapped.transpose(0, 2, 1, 3)

    # now flatten the first two and last two dimensions
    out = mapped.reshape(H*3, W*3).astype(np.uint8)

    return out


def robust_normalize(stat, lo, hi, eps=1e-9):
    return np.clip((stat - lo) / (hi - lo + eps), 0.0, 1.0)

def compute_divergence_factor(gray: np.ndarray, 
                              min_df=0.0, max_df=8.0, 
                              lo_std=5, hi_std=40, 
                              gamma=1.2):
    # Measure variation
    std = float(np.std(gray))

    # Normalize relative to expected std bounds
    norm = robust_normalize(std, lo_std, hi_std)
    norm = norm ** gamma

    return min_df + (max_df - min_df) * norm

def process_frame(img: Image, pixelation_factor: int, random_factor: int, divergence_factor: float, divergence_point: float):
    # Performing operations on image object
    img_pixelated = pixelate(pixelation_factor,img)  # Higher is more pixelated

    # converting to a numpy array.
    # Operations from now on expect a numpy array.
    arr = np.array(img_pixelated)

    # try divergence point as median
    if divergence_point is None:
        divergence_point = np.median(arr)
    if divergence_factor is None:
        divergence_factor = compute_divergence_factor(arr)
    arr = pixel_divergence(arr, divergence_factor, divergence_point)

    arr_random = add_random_pixels(arr, random_factor)
    arr_dithered = expand_pixels(arr_random)
    final_image = Image.fromarray(np.uint8(arr_dithered))

    return final_image


# this is for the TUI
def dither_image_file(
    input_path: str,
    output_path: str,
    pixelation_factor: int,
    random_factor: int,
    divergence_factor: float,
    divergence_point: float
) -> None:
    img = Image.open(input_path).convert('L')

    final_image = process_frame(
        img,
        pixelation_factor,
        random_factor,
        divergence_factor,
        divergence_point
    )

    final_image.save(output_path)

# --------------
# Main Code
# --------------


def main():

    # input image path
    if len(sys.argv) < 3:
        print("Usage: python 1_bit_image_ditherer.py <input_image_path> <output_image_path> [pixelation_factor] [random_factor] [divergence_factor] [divergence_point]")
        return
    input_image_path = sys.argv[1]
    output_image_path = sys.argv[2]

    # default parameters
    pixelation_factor = 12
    random_factor = 8
    divergence_factor = 4
    divergence_point = 128.0

    if len(sys.argv) >= 4:
        pixelation_factor = int(sys.argv[3])
    if len(sys.argv) >= 5:
        random_factor = int(sys.argv[4])
    if len(sys.argv) >= 6:
        divergence_factor = float(sys.argv[5])
    if len(sys.argv) >= 7:
        divergence_point = float(sys.argv[6])
    
    path = os.path(input_image_path)
    img = Image.open(path).convert('L')

    final_image = process_frame(img, pixelation_factor, random_factor, divergence_factor, divergence_point)

    final_image.save(fp=output_image_path)

if __name__ == "__main__":
    main()