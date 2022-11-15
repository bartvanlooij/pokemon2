import PIL.Image
from PIL import Image
import pytesseract
import math

def calibration(calibration_img : PIL.Image.Image):
    black_seen = False
    top_bar_seen = False
    for i in range(calibration_img.height):


        pixel_color = calibration_img.getpixel((0, i))
        print(pixel_color, i)
        if pixel_color == (240,240,240):
            top_bar_seen = True
        if top_bar_seen:
            if pixel_color != (240,240,240):
                top_screen_top = i
                top_bar_seen = False
        if pixel_color == (0, 0, 0):
            black_seen = True
        if black_seen:
            if pixel_color != (0, 0, 0):
                top = i
                top_screen_coords = (0, top_screen_top, calibration_img.width, top)
                bot_screen_coords = (0, top, calibration_img.width, calibration_img.height)
                break

    return top_screen_coords, bot_screen_coords

def find_name_box(top_screen : PIL.Image.Image):

    top_box_found = 0
    tolerance = 5
    for i in range(top_screen.height):
        r, g, b = top_screen.getpixel((0,i))
        if ( 60 - tolerance <= r <= 60 + tolerance and
                60 - tolerance <= g <= 60 + tolerance and
                60 - tolerance <= b <= 60 + tolerance
                and top_box_found == 0):
            top_box_found += 1


        if (top_box_found == 1 and not
              (
                      (r < 60 - tolerance and g < 60 - tolerance and b < 60 - tolerance)
                  or (r < 60 + tolerance and g < 60 + tolerance and b < 60 + tolerance)
              )):
            top_box_found += 1
            top_box = i


        if ( 60 - tolerance <= r <= 60 + tolerance and
                60 - tolerance <= g <= 60 + tolerance and
                60 - tolerance <= b <= 60 + tolerance
                and top_box_found == 2):
            bottom_box = i

            break
    box_image = top_screen.crop((0, top_box, top_screen.width, bottom_box))
    for i in range(0,box_image.width):
        r, g, b = box_image.getpixel((i,0))
        if ( 60 - tolerance <= r <= 60 + tolerance and
                60 - tolerance <= g <= 60 + tolerance and
                60 - tolerance <= b <= 60 + tolerance):
            box_right = i
            break

    box_right = math.floor(box_right*0.61)
    bottom_box = bottom_box - top_box
    bottom_box = math.floor(bottom_box*0.6)
    box_coords = (0,top_box, box_right, top_box + bottom_box)
    return box_coords
