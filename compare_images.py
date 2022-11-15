
from PIL import Image
#
# def rmsdiff(im1, im2):
#     "Calculate the root-mean-square difference between two images"
#
#     h = ImageChops.difference(im1, im2).histogram()
#
#     # calculate rms
#     return math.sqrt(reduce(operator.add,
#         map(lambda h, i: h*(i**2), h, range(256))
#     ) / (float(im1.size[0]) * im1.size[1]))
#
# img1 = Image.open("test_fotos/1.png")
# img2 = Image.open("test_fotos/2.png")
#
# rmsdiff(img1,img2)
import PIL.Image
from PIL import Image # No need for ImageChops
import math
from skimage import img_as_float
from skimage.metrics import structural_similarity

def similarity(im1, im2):
    """Calculates the root mean square error (RSME) between two images"""
    return math.sqrt(abs(structural_similarity(img_as_float(im1), img_as_float(im2))))

def make_images_same_size(img1 : PIL.Image.Image, img2 : PIL.Image.Image):
    img2 = img2.resize((img1.width, img1.height))
    return img1, img2
