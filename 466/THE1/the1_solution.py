########## CENG 466 THE 1 #########
# Berke Can Ünlü          2381028 #
# Buğra Burak Altıntaş    2380079 #
###################################



import os
import cv2 as cv
import matplotlib.pyplot as plt
import math
# import numpy as np


INPUT_PATH = "./THE1_Images/"
OUTPUT_PATH = "./Outputs/"

def read_image(img_path, rgb = True):
    img = None
    if rgb == True:
        img = cv.imread(img_path)
    else:
        img = cv.imread(img_path)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img

def write_image(img, output_path, rgb = True):
    cv.imwrite(output_path,img)

def extract_save_histogram(img, path):
    plt.hist(img.ravel(),bins=20)
    plt.savefig(path)
    plt.close()
    

def rotate_image(img,  degree = 0, interpolation_type = "linear"):
    rotated = None
    height,width = img.shape[:2]
    center_of_img = (height/2,width/2)
    img_size = (height,width)
    
    # padding in order not to lose corner of image
    
    if(degree != 90 and degree != 180 and degree != 270):
        diagonal_length = math.sqrt(height * height + width * width)
        padding_top = padding_bot = round((diagonal_length - height) / 2)
        padding_left = padding_right = round((diagonal_length - width) / 2)
    
        img = cv.copyMakeBorder(img,padding_top,padding_bot,padding_left,padding_right,cv.BORDER_CONSTANT,value=0)
        height,width = img.shape[:2]
        center_of_img = (height/2,width/2)
        img_size = (height,width)
    
    if interpolation_type == "linear":
        transform_matrix = cv.getRotationMatrix2D(center=center_of_img,angle=degree,scale=1)
        rotated = cv.warpAffine(src=img,M=transform_matrix,dsize=img_size, flags=cv.INTER_LINEAR)
        
    elif interpolation_type == "cubic":
        transform_matrix = cv.getRotationMatrix2D(center=center_of_img,angle=degree,scale=1)
        rotated = cv.warpAffine(src=img,M=transform_matrix,dsize=img_size,flags=cv.INTER_CUBIC)
    return rotated

def histogram_equalization(img):
    equalized = cv.equalizeHist(img)
    return equalized



def adaptive_histogram_equalization(img):
    # may change clipLimit to a lower val
    clahe = cv.createCLAHE(clipLimit=10.0, tileGridSize=(8,8))
    return clahe.apply(img)

"""
def mse(img1, img2):
   h, w = img1.shape[:2]
   diff = cv.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse
"""




if __name__ == '__main__':
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    #PART1
    img = read_image(INPUT_PATH + "a1.png")
    output = rotate_image(img, 45, "linear")
    write_image(output, OUTPUT_PATH + "a1_45_linear.png")
    
    img = read_image(INPUT_PATH + "a1.png")
    output = rotate_image(img, 45, "cubic")
    write_image(output, OUTPUT_PATH + "a1_45_cubic.png")

    img = read_image(INPUT_PATH + "a1.png")
    output = rotate_image(img, 90, "linear")
    write_image(output, OUTPUT_PATH + "a1_90_linear.png")

    img = read_image(INPUT_PATH + "a1.png")
    output = rotate_image(img, 90, "cubic")
    write_image(output, OUTPUT_PATH + "a1_90_cubic.png")
        
    img = read_image(INPUT_PATH + "a2.png")
    output = rotate_image(img, 45, "linear")
    write_image(output, OUTPUT_PATH + "a2_45_linear.png")

    img = read_image(INPUT_PATH + "a2.png")
    output = rotate_image(img, 45, "cubic")
    write_image(output, OUTPUT_PATH + "a2_45_cubic.png")


    #PART2
    img = read_image(INPUT_PATH + "b1.png", rgb = False)
    extract_save_histogram(img, OUTPUT_PATH + "original_histogram.png")
    equalized = histogram_equalization(img)
    extract_save_histogram(equalized, OUTPUT_PATH + "equalized_histogram.png")
    write_image(equalized, OUTPUT_PATH + "enhanced_image.png")

    # BONUS
    # Define the following function
    equalized = adaptive_histogram_equalization(img)
    extract_save_histogram(equalized, OUTPUT_PATH + "adaptive_equalized_histogram.png")
    write_image(equalized, OUTPUT_PATH + "adaptive_enhanced_image.png")