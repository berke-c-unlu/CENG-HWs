########## CENG 466 THE 1 #########
# Berke Can Ünlü          2381028 #
# Buğra Burak Altıntaş    2380079 #
###################################



import os
import cv2 as cv
from math import sqrt, pi
import matplotlib.pyplot as plt
import numpy as np
import scipy.fftpack as spfft
from scipy.linalg import hadamard

INPUT_PATH = "./THE2_images/"
OUTPUT_PATH = "./Outputs/"

R1 = 20
R2 = 60
R3 = 100


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

# saves filters
def save_filter(filter,rows,cols,filter_name):
    im = np.zeros((rows,cols))
    for r in range(rows):
        for c in range(cols):
            im[r,c] = round(filter[r,c] * 255)
    
    cv.imwrite("./filters/" +filter_name+ ".png", im)

# returns distance between two points in square form
def distance_sqr(x,y,center):
    return (x- center[0])**2 + (y - center[1])**2

# To fit the shape 2^N format.
def find_size(n):
    size = 2
    while n > size:
        size *= 2
    return size

# Split channels into b,g,r
def split_channels(img):
    b,g,r = cv.split(img)
    return b,g,r

# Apply Discrete Fourier Transform
def apply_dft(b,g,r):
    b_dft = spfft.fft2(b)
    g_dft = spfft.fft2(g)
    r_dft = spfft.fft2(r)
    return b_dft,g_dft,r_dft

# Apply Fourier Transform Shift
def apply_shift(b,g,r):
    b_shift = spfft.fftshift(b)
    g_shift = spfft.fftshift(g)
    r_shift = spfft.fftshift(r)
    return b_shift,g_shift,r_shift

# Apply Inverse Discrete Fourier Transform
def apply_idft_with_shift(b,g,r):
    # take inverse transform of each filtered channel
    filtered_blue = spfft.ifft2(spfft.ifftshift(b)).real
    filtered_green = spfft.ifft2(spfft.ifftshift(g)).real
    filtered_red = spfft.ifft2(spfft.ifftshift(r)).real

    return filtered_blue,filtered_green,filtered_red

# Get Magnitudes of shifted DFT for each channel
def get_magnitudes_ft(b,g,r):
    # Convert cartesian coordinates to polar coordinates to get magnitude and phase
    mag_blue = abs(b)
    mag_green = abs(g)
    mag_red = abs(r)

    return mag_blue,mag_green,mag_red

# Apply Discrete Cosine Transform
def apply_dct(b,g,r):
    b_dct = spfft.dctn(b)
    g_dct = spfft.dctn(g)
    r_dct = spfft.dctn(r)
    return b_dct,g_dct,r_dct

# Creates Gaussian Low Pass Filter in frequency domain
def get_LP_gaussian(cutoff_freq,rows,cols):
    # zero matrix with image size
    g_filter = np.zeros((rows,cols))

    # center of the image
    center = (int(rows/2),int(cols/2))

    # changes the entries of filter matrix for gaussian low pass filter
    for x in range(rows):
        for y in range(cols):
            # distance between the center of the image and current point
            dist = distance_sqr(x,y,center)
            # Gaussian Function in frequency domain
            # Reference : From the book by R. Gonzales, R.Woods
            g_filter[x,y] = np.exp((-dist)/((2*cutoff_freq**2)))
    
    return g_filter

# Creates Gaussian High Pass Filter in frequency domain
def get_HP_gaussian(cutoff_freq,rows,cols):
    # matrix with full ones
    # Since GHPF = 1 - GLPF
    g_filter = np.ones((rows,cols))

    # center of the image
    center = (int(rows/2),int(cols/2))

    for x in range(rows):
        for y in range(cols):
            # distance between center and current point
            dist = distance_sqr(x,y,center)
            # Gaussian Function in frequency domain
            # Reference : From the book by R. Gonzales, R.Woods
            g_filter[x,y] -= np.exp((-dist)/((2*cutoff_freq**2)))

    return g_filter

# Creates Band Pass Filter in frequency domain (Ideal)
def get_BP_ideal(cutoff_freq,bandwidth,rows,cols):
    # zero matrix with image size
    bp_filter = np.zeros((rows,cols))
    # center of the image
    center = (int(rows/2),int(cols/2))

    r1 = center[0] - bandwidth - cutoff_freq - 1
    r2 = center[0] + bandwidth + cutoff_freq
    c1 = center[1] - bandwidth - cutoff_freq - 1
    c2 = center[1] + bandwidth + cutoff_freq

    for r in range(r1,r2):
        for c in range(c1,c2):
            bp_filter[r,c] = 1

    r1 = center[0] - cutoff_freq - 1
    r2 = center[0] + cutoff_freq
    c1 = center[1] - cutoff_freq - 1
    c2 = center[1] + cutoff_freq

    for r in range(r1,r2):
        for c in range(c1,c2):
            bp_filter[r,c] = 0
    
    return bp_filter

# Creates Band Reject Filter in frequency domain (Ideal)
def get_BR_ideal(cutoff_freq,bandwidth,rows,cols):
    # zero matrix with image size
    br_filter = np.ones((rows,cols))
    br_filter = np.subtract(br_filter,get_BP_ideal(cutoff_freq,bandwidth,rows,cols))
    
    return br_filter

def improve_contrast(img,clipLimit = 3, tileSize = (3,3), sigma = 6, kernelSize = (3,3)):
    (B,G,R) = cv.split(img)

    clahe = cv.createCLAHE(clipLimit, tileSize)
    B = clahe.apply(B)
    G = clahe.apply(G)
    R = clahe.apply(R)

    merged = cv.merge([B,G,R])
    return cv.GaussianBlur(merged,kernelSize,sigmaX=sigma)

# Creates Butterworh Low Pass Filter in frequency domain
def get_LP_butterworh(cutoff_freq,rows,cols):
    # zero matrix with image size
    b_filter = np.zeros((rows,cols))

    # center of the image
    center = (int(rows/2),int(cols/2))

    # changes the entries of filter matrix for gaussian low pass filter
    for x in range(rows):
        for y in range(cols):
            # distance between the center of the image and current point
            dist = sqrt(distance_sqr(x,y,center))
            # Gaussian Function in frequency domain
            # Reference : From the book by R. Gonzales, R.Woods
            b_filter[x,y] = 1 / ((1 + dist / cutoff_freq)**2)
    
    return b_filter

# Creates Butterworh High Pass Filter in frequency domain
def get_HP_butterworh(cutoff_freq,rows,cols):
    # one matrix with image size
    b_filter = np.ones((rows,cols))

    # center of the image
    center = (int(rows/2),int(cols/2))

    # changes the entries of filter matrix for gaussian low pass filter
    for x in range(rows):
        for y in range(cols):
            # distance between the center of the image and current point
            dist = sqrt(distance_sqr(x,y,center))
            # Gaussian Function in frequency domain
            # Reference : From the book by R. Gonzales, R.Woods
            b_filter[x,y] = 1 - (1 / ((1 + dist / cutoff_freq)**2))
    
    return b_filter

###############################################################################################################

############################################ TRANSFORMS #######################################################

# Discrete Fourier Transform
# Shifted to the center
def fourier_transform(blue_channel,green_channel,red_channel):
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    blue_shift,green_shift,red_shift = apply_shift(blue_ft,green_ft,red_ft)

    mag_blue,mag_green,mag_red = get_magnitudes_ft(blue_shift,green_shift,red_shift)

    # Merge R G B magnitudes
    magnitude = cv.merge([mag_blue,mag_green,mag_red])

    # Normalize RGB values
    normalized = cv.normalize(magnitude, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
    normalized = np.multiply(255,normalized)

    return normalized

# Cosine Transform
# Not shifted to the center
def cosine_transform(blue_channel,green_channel,red_channel):
    # Apply discrete cosine transform to each of the channels
    blue_dct,green_dct,red_dct = apply_dct(blue_channel,green_channel,red_channel)

    # Merge all channels
    merged_ct = cv.merge([blue_dct,green_dct,red_dct])

    normalized = cv.normalize(merged_ct, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
    normalized = np.multiply(127,normalized)

    return normalized

# Hadamard Transform
# Not shifted to the center
def hadamard_transform(img):
    # retrieve the shape of image to resize image and construct hadamard matrices
    shape = np.shape(img)

    M = find_size(shape[0])
    N = find_size(shape[1])

    # resized image
    # we interpolated the image to fit the image 2^N and 2^M size
    # The image did not abruptly change, so we decided to interpolate the image
    resized = cv.resize(img,dsize=(N,M),interpolation=cv.INTER_CUBIC)

    # Split image into channels B G R
    blue_channel = np.float32(resized[:,:,0])
    green_channel = np.float32(resized[:,:,1])
    red_channel = np.float32(resized[:,:,2])

    # Construct hadamard matrices

    hadamard_left = hadamard(M)
    hadamard_right = hadamard(N)

    left_blue = np.matmul(hadamard_left,blue_channel)
    blue_ht = np.matmul(left_blue,hadamard_right)

    left_green = np.matmul(hadamard_left,green_channel)
    green_ht = np.matmul(left_green,hadamard_right)

    left_red = np.matmul(hadamard_left,red_channel)
    red_ht = np.matmul(left_red,hadamard_right)

    merged = cv.merge([blue_ht,green_ht,red_ht])

    normalized = cv.normalize(merged, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
    normalized = np.multiply(64,normalized)

    return normalized

###############################################################################################################

############################################## LOW PASS FILTERS ###############################################

# Ideal low pass filter with cutoff frequency
# Uses Discrete Fourier Transform
def ideal_low_pass_filter(blue_channel,green_channel,red_channel,cutoff_freq):
    # Apply fourier transform to each channel
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    # Shift the transformed image to the center
    blue_shifted,green_shifted,red_shifted = apply_shift(blue_ft,green_ft,red_ft)

    # Shape of the image
    shape = blue_shifted.shape

    # indexes of lowpass filter
    left_top = int(shape[0]/2 - cutoff_freq - 1)
    left_bot = int(shape[0]/2 + cutoff_freq)
    right_top = int(shape[1]/2 - cutoff_freq - 1)
    right_bot = int(shape[1]/2 + cutoff_freq)

    # initialize zero arrays for lowpass filter
    low_pass_blue = spfft.fft2(np.zeros((shape[0], shape[1])))
    low_pass_green = spfft.fft2(np.zeros((shape[0], shape[1])))
    low_pass_red = spfft.fft2(np.zeros((shape[0], shape[1])))

    # apply filter for each channels
    low_pass_blue[left_top : left_bot, right_top: right_bot] = blue_shifted[left_top : left_bot, right_top : right_bot]
    low_pass_green[left_top : left_bot, right_top: right_bot] = green_shifted[left_top : left_bot, right_top : right_bot]
    low_pass_red[left_top : left_bot, right_top: right_bot] = red_shifted[left_top : left_bot, right_top : right_bot]

    # take inverse transform of each filtered channel
    filtered_blue,filtered_green,filtered_red = apply_idft_with_shift(low_pass_blue,low_pass_green,low_pass_red)

    # Merge each channel and normalize the final image
    merged = cv.merge([filtered_blue,filtered_green,filtered_red])
    normalized = cv.normalize(merged,None,alpha=0,beta=255,norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

    return normalized

# Gaussian Low pass filter with cutoff frequency
# Uses Discrete Fourier Transform
def gaussian_low_pass_filter(blue_channel,green_channel,red_channel,cutoff_freq):
    # Apply fourier transform to each channel
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    # Shift the transformed image to the center
    blue_shifted,green_shifted,red_shifted = apply_shift(blue_ft,green_ft,red_ft)

    # Shape of the image
    shape = blue_shifted.shape

    # indexes of lowpass filter
    r1 = int(shape[0]/2 - cutoff_freq - 1)
    r2 = int(shape[0]/2 + cutoff_freq)
    c1 = int(shape[1]/2 - cutoff_freq - 1)
    c2 = int(shape[1]/2 + cutoff_freq)

    # create gaussian low pass filter in frequency domain
    gaussian_lp_filter = get_LP_gaussian(cutoff_freq,shape[0],shape[1])

    save_filter(gaussian_lp_filter,shape[0],shape[1],"glpf" + str(cutoff_freq))


    # apply filter for each channels
    low_pass_blue = np.multiply(blue_shifted,gaussian_lp_filter)
    low_pass_green = np.multiply(green_shifted,gaussian_lp_filter)
    low_pass_red = np.multiply(red_shifted,gaussian_lp_filter)

    # take inverse transform of each filtered channel
    filtered_blue,filtered_green,filtered_red = apply_idft_with_shift(low_pass_blue,low_pass_green,low_pass_red)

    # Merge each channel and normalize the final image
    merged = cv.merge([filtered_blue,filtered_green,filtered_red])
    normalized = cv.normalize(merged,None,alpha=0,beta=255,norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

    return normalized

# Butterworh Low pass filter with cutoff frequency
# Uses Discrete Fourier Transform
def butterworh_low_pass_filter(blue_channel,green_channel,red_channel,cutoff_freq):
    # Apply fourier transform to each channel
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    # Shift the transformed image to the center
    blue_shifted,green_shifted,red_shifted = apply_shift(blue_ft,green_ft,red_ft)

    # Shape of the image
    shape = blue_shifted.shape

    # indexes of lowpass filter
    r1 = int(shape[0]/2 - cutoff_freq - 1)
    r2 = int(shape[0]/2 + cutoff_freq)
    c1 = int(shape[1]/2 - cutoff_freq - 1)
    c2 = int(shape[1]/2 + cutoff_freq)

    # create gaussian low pass filter in frequency domain
    butterworh_lp_filter = get_LP_butterworh(cutoff_freq,shape[0],shape[1])

    save_filter(butterworh_lp_filter,shape[0],shape[1],"blpf" + str(cutoff_freq))


    # apply filter for each channels
    low_pass_blue = np.multiply(blue_shifted,butterworh_lp_filter)
    low_pass_green = np.multiply(green_shifted,butterworh_lp_filter)
    low_pass_red = np.multiply(red_shifted,butterworh_lp_filter)

    # take inverse transform of each filtered channel
    filtered_blue,filtered_green,filtered_red = apply_idft_with_shift(low_pass_blue,low_pass_green,low_pass_red)

    # Merge each channel and normalize the final image
    merged = cv.merge([filtered_blue,filtered_green,filtered_red])
    normalized = cv.normalize(merged,None,alpha=0,beta=255,norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

    return normalized

###############################################################################################################

############################################## HIGH PASS FILTERS ##############################################

# Ideal high pass filter with cutoff frequency
# Uses Discrete Fourier Transform
def ideal_high_pass_filter(blue_channel,green_channel,red_channel,cutoff_freq):
    # Apply fourier transform to each channel
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    # Shift the transformed image to the center
    blue_shifted,green_shifted,red_shifted = apply_shift(blue_ft,green_ft,red_ft)

    # Shape of the image
    shape = blue_shifted.shape

    # indexes of lowpass filter
    left_top = int(shape[0]/2 - cutoff_freq - 1)
    left_bot = int(shape[0]/2 + cutoff_freq)
    right_top = int(shape[1]/2 - cutoff_freq - 1)
    right_bot = int(shape[1]/2 + cutoff_freq)

    # initialize zero arrays for highpass filter
    high_pass_blue = np.copy(blue_shifted)
    high_pass_green = np.copy(green_shifted)
    high_pass_red = np.copy(red_shifted)

    # apply filter for each channels
    high_pass_blue[left_top : left_bot, right_top: right_bot] = 0
    high_pass_green[left_top : left_bot, right_top: right_bot] = 0
    high_pass_red[left_top : left_bot, right_top: right_bot] = 0

    # take inverse transform of each filtered channel
    filtered_blue,filtered_green,filtered_red = apply_idft_with_shift(high_pass_blue,high_pass_green,high_pass_red)

    # Merge each channel and normalize the final image
    merged = cv.merge([filtered_blue,filtered_green,filtered_red])
    normalized = cv.normalize(merged,None,alpha=0,beta=255,norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

    return normalized

def gaussian_high_pass_filter(blue_channel,green_channel,red_channel,cutoff_freq):
    # Apply fourier transform to each channel
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    # Shift the transformed image to the center
    blue_shifted,green_shifted,red_shifted = apply_shift(blue_ft,green_ft,red_ft)

    # Shape of the image
    shape = blue_shifted.shape

    # indexes of lowpass filter
    r1 = int(shape[0]/2 - cutoff_freq - 1)
    r2 = int(shape[0]/2 + cutoff_freq)
    c1 = int(shape[1]/2 - cutoff_freq - 1)
    c2 = int(shape[1]/2 + cutoff_freq)

    # create gaussian high pass filter in frequency domain
    gaussian_hp_filter = get_HP_gaussian(cutoff_freq,shape[0],shape[1])
    
    save_filter(gaussian_hp_filter,shape[0],shape[1],"ghpf" + str(cutoff_freq))

    # apply gaussian high pass filter to each channel
    high_pass_blue = np.multiply(blue_shifted,gaussian_hp_filter)
    high_pass_green = np.multiply(green_shifted,gaussian_hp_filter)
    high_pass_red = np.multiply(red_shifted,gaussian_hp_filter)

    # take inverse transform of each filtered channel
    filtered_blue,filtered_green,filtered_red = apply_idft_with_shift(high_pass_blue,high_pass_green,high_pass_red)

    # Merge each channel and normalize the final image
    merged = cv.merge([filtered_blue,filtered_green,filtered_red])
    normalized = cv.normalize(merged,None,alpha=0,beta=255,norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

    return normalized

def butterworh_high_pass_filter(blue_channel,green_channel,red_channel,cutoff_freq):
    # Apply fourier transform to each channel
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    # Shift the transformed image to the center
    blue_shifted,green_shifted,red_shifted = apply_shift(blue_ft,green_ft,red_ft)

    # Shape of the image
    shape = blue_shifted.shape

    # indexes of lowpass filter
    r1 = int(shape[0]/2 - cutoff_freq - 1)
    r2 = int(shape[0]/2 + cutoff_freq)
    c1 = int(shape[1]/2 - cutoff_freq - 1)
    c2 = int(shape[1]/2 + cutoff_freq)

    # create gaussian high pass filter in frequency domain
    butterworh_hp_filter = get_HP_butterworh(cutoff_freq,shape[0],shape[1])
    
    save_filter(butterworh_hp_filter,shape[0],shape[1],"bhpf" + str(cutoff_freq))

    # apply gaussian high pass filter to each channel
    high_pass_blue = np.multiply(blue_shifted,butterworh_hp_filter)
    high_pass_green = np.multiply(green_shifted,butterworh_hp_filter)
    high_pass_red = np.multiply(red_shifted,butterworh_hp_filter)

    # take inverse transform of each filtered channel
    filtered_blue,filtered_green,filtered_red = apply_idft_with_shift(high_pass_blue,high_pass_green,high_pass_red)

    # Merge each channel and normalize the final image
    merged = cv.merge([filtered_blue,filtered_green,filtered_red])
    normalized = cv.normalize(merged,None,alpha=0,beta=255,norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

    return normalized

###############################################################################################################

############################################## BAND PASS REJECT ###############################################

def band_pass_filter(blue_channel,green_channel,red_channel,cutoff_freq,bandwith):
    # Apply fourier transform to each channel
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    # Shift the transformed image to the center
    blue_shifted,green_shifted,red_shifted = apply_shift(blue_ft,green_ft,red_ft)

    # Shape of the image
    shape = blue_shifted.shape

    bp_filter = get_BP_ideal(cutoff_freq,bandwith,shape[0],shape[1])
    save_filter(bp_filter,shape[0],shape[1],"band_pass_filter")

    # apply gaussian high pass filter to each channel
    band_pass_blue = np.multiply(blue_shifted,bp_filter)
    band_pass_green = np.multiply(green_shifted,bp_filter)
    band_pass_red = np.multiply(red_shifted,bp_filter)

    # take inverse transform of each filtered channel
    filtered_blue,filtered_green,filtered_red = apply_idft_with_shift(band_pass_blue,band_pass_green,band_pass_red)

    # Merge each channel and normalize the final image
    merged = cv.merge([filtered_blue,filtered_green,filtered_red])
    normalized = cv.normalize(merged,None,alpha=0,beta=255,norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

    return normalized

def band_reject_filter(blue_channel,green_channel,red_channel,cutoff_freq,bandwith):
    # Apply fourier transform to each channel
    blue_ft,green_ft,red_ft = apply_dft(blue_channel,green_channel,red_channel)

    # Shift the transformed image to the center
    blue_shifted,green_shifted,red_shifted = apply_shift(blue_ft,green_ft,red_ft)

    # Shape of the image
    shape = blue_shifted.shape

    br_filter = get_BR_ideal(cutoff_freq,bandwith,shape[0],shape[1])
    save_filter(br_filter,shape[0],shape[1],"band_reject")

    # apply ideal band reject filter to each channel
    band_reject_blue = np.multiply(blue_shifted,br_filter)
    band_reject_green = np.multiply(green_shifted,br_filter)
    band_reject_red = np.multiply(red_shifted,br_filter)

    # take inverse transform of each filtered channel
    filtered_blue,filtered_green,filtered_red = apply_idft_with_shift(band_reject_blue,band_reject_green,band_reject_red)

    # Merge each channel and normalize the final image
    merged = cv.merge([filtered_blue,filtered_green,filtered_red])
    normalized = cv.normalize(merged,None,alpha=0,beta=255,norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

    return normalized

###############################################################################################################

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    #### FOURIER, HADAMARD, COSINE transform for Image1 ####

    # Read Image 1
    img1 = read_image(INPUT_PATH + "1.png")
    blue_channel,green_channel,red_channel = split_channels(img1)

    # Do transforms
    ft_img = fourier_transform(blue_channel,green_channel,red_channel)
    ht_img = hadamard_transform(img1)
    ct_img = cosine_transform(blue_channel,green_channel,red_channel)

    # Write transformed images
    write_image(ft_img,OUTPUT_PATH + "F1.png")
    write_image(ht_img,OUTPUT_PATH + "H1.png")
    write_image(ct_img,OUTPUT_PATH + "C1.png")

    ##########################################################


    #### FOURIER, HADAMARD, COSINE transform for Image2 ####

    # Read Image 2
    img2 = read_image(INPUT_PATH + "2.png")
    blue_channel,green_channel,red_channel = split_channels(img2)

    # Do transforms
    ft_img = fourier_transform(blue_channel,green_channel,red_channel)
    ht_img = hadamard_transform(img2)
    ct_img = cosine_transform(blue_channel,green_channel,red_channel)

    # Write transformed images
    write_image(ft_img,OUTPUT_PATH + "F2.png")
    write_image(ht_img,OUTPUT_PATH + "H2.png")
    write_image(ct_img,OUTPUT_PATH + "C2.png")

    ##########################################################


    #################### LOW PASS FILTERS ####################

    # Read Image 3
    img3 = read_image(INPUT_PATH + "3.png")
    blue_channel,green_channel,red_channel = split_channels(img3)

    # Apply filter with 3 different cutoff frequencies
    ideal_low_pass_img1 = ideal_low_pass_filter(blue_channel,green_channel,red_channel,R1)
    ideal_low_pass_img2 = ideal_low_pass_filter(blue_channel,green_channel,red_channel,R2)
    ideal_low_pass_img3 = ideal_low_pass_filter(blue_channel,green_channel,red_channel,R3)

    # Write images
    write_image(ideal_low_pass_img1,OUTPUT_PATH + "ILP_r1.png")
    write_image(ideal_low_pass_img2,OUTPUT_PATH + "ILP_r2.png")
    write_image(ideal_low_pass_img3,OUTPUT_PATH + "ILP_r3.png")


    # Apply filter with 3 different cutoff frequencies
    gaussian_low_pass_img1 = gaussian_low_pass_filter(blue_channel,green_channel,red_channel,R1)
    gaussian_low_pass_img2 = gaussian_low_pass_filter(blue_channel,green_channel,red_channel,R2)
    gaussian_low_pass_img3 = gaussian_low_pass_filter(blue_channel,green_channel,red_channel,R3)


    # Write images
    write_image(gaussian_low_pass_img1,OUTPUT_PATH + "GLP_r1.png")
    write_image(gaussian_low_pass_img2,OUTPUT_PATH + "GLP_r2.png")
    write_image(gaussian_low_pass_img3,OUTPUT_PATH + "GLP_r3.png")


    # Apply filter with 3 different cutoff frequencies
    butterworh_low_pass_img1 = butterworh_low_pass_filter(blue_channel,green_channel,red_channel,R1)
    butterworh_low_pass_img2 = butterworh_low_pass_filter(blue_channel,green_channel,red_channel,R2)
    butterworh_low_pass_img3 = butterworh_low_pass_filter(blue_channel,green_channel,red_channel,R3)

    # Write images
    write_image(butterworh_low_pass_img1,OUTPUT_PATH + "BLP_r1.png")
    write_image(butterworh_low_pass_img2,OUTPUT_PATH + "BLP_r2.png")
    write_image(butterworh_low_pass_img3,OUTPUT_PATH + "BLP_r3.png")

    ##########################################################


    ################### HIGH PASS FILTERS ####################

    # Apply filter with 3 different cutoff frequencies
    ideal_high_pass_img1 = ideal_high_pass_filter(blue_channel,green_channel,red_channel,R1)
    ideal_high_pass_img2 = ideal_high_pass_filter(blue_channel,green_channel,red_channel,R2)
    ideal_high_pass_img3 = ideal_high_pass_filter(blue_channel,green_channel,red_channel,R3)

    # Write images
    write_image(ideal_high_pass_img1,OUTPUT_PATH + "IHP_r1.png")
    write_image(ideal_high_pass_img2,OUTPUT_PATH + "IHP_r2.png")
    write_image(ideal_high_pass_img3,OUTPUT_PATH + "IHP_r3.png")


    # Apply filter with 3 different cutoff frequencies
    gaussian_high_pass_img1 = gaussian_high_pass_filter(blue_channel,green_channel,red_channel,R1)
    gaussian_high_pass_img2 = gaussian_high_pass_filter(blue_channel,green_channel,red_channel,R2)
    gaussian_high_pass_img3 = gaussian_high_pass_filter(blue_channel,green_channel,red_channel,R3)


    # Write images
    write_image(gaussian_high_pass_img1,OUTPUT_PATH + "GHP_r1.png")
    write_image(gaussian_high_pass_img2,OUTPUT_PATH + "GHP_r2.png")
    write_image(gaussian_high_pass_img3,OUTPUT_PATH + "GHP_r3.png")


    # Apply filter with 3 different cutoff frequencies
    butterworh_high_pass_img1 = butterworh_high_pass_filter(blue_channel,green_channel,red_channel,R1)
    butterworh_high_pass_img2 = butterworh_high_pass_filter(blue_channel,green_channel,red_channel,R2)
    butterworh_high_pass_img3 = butterworh_high_pass_filter(blue_channel,green_channel,red_channel,R3)

    # Write images
    write_image(butterworh_high_pass_img1,OUTPUT_PATH + "BHP_r1.png")
    write_image(butterworh_high_pass_img2,OUTPUT_PATH + "BHP_r2.png")
    write_image(butterworh_high_pass_img3,OUTPUT_PATH + "BHP_r3.png")
    
    ##########################################################


    ################### BAND REJECT/PASS FILTERS ####################

    # Read Image 4
    img4 = read_image(INPUT_PATH + "4.png")
    blue_channel,green_channel,red_channel = split_channels(img4)

    band_pass_4 = band_pass_filter(blue_channel,green_channel,red_channel,30,90)
    band_reject_4 = band_reject_filter(blue_channel,green_channel,red_channel,30,90)

    write_image(band_pass_4,OUTPUT_PATH + "BP1.png")
    write_image(band_reject_4,OUTPUT_PATH + "BR1.png")

    # Read Image 5
    img5 = read_image(INPUT_PATH + "5.png")
    blue_channel,green_channel,red_channel = split_channels(img5)

    band_reject_5 = band_reject_filter(blue_channel,green_channel,red_channel,40,100)
    band_pass_5 = band_pass_filter(blue_channel,green_channel,red_channel,40,100)

    write_image(band_reject_5,OUTPUT_PATH + "BR2.png")
    write_image(band_pass_5,OUTPUT_PATH + "BP2.png")



    ###### EXPERIMENTAL ######

    #f4 = fourier_transform(img4)
    #f5 = fourier_transform(img5)
    #a = fourier_transform(band_reject_4)
    #write_image(a, "a.png")
    
    #b = fourier_transform(band_pass_4)
    #write_image(b,"b.png")"""

    #c = fourier_transform(band_reject_5)
    #write_image(c, "c.png")
    #d = fourier_transform(band_pass_5)
    #write_image(d,"d.png")

    #lp5 = ideal_low_pass_filter(img5,8)
    #write_image(lp5,"trial.png")

    #write_image(f4,"./image4_fourier.png")
    #write_image(f5,"./image5_fourier.png")

    ############################

    #################################################################

    ###################### CONTRAST IMPROVING #######################
    img6 = read_image(INPUT_PATH + "6.png")
    blue_channel,green_channel,red_channel = split_channels(img6)
    
    img6 = improve_contrast(img=img6,clipLimit=3,tileSize=(3,3),kernelSize=(3,3),sigma=6)

    write_image(img6,OUTPUT_PATH + "Space6.png")


    img7 = read_image(INPUT_PATH + "7.png")
    blue_channel,green_channel,red_channel = split_channels(img7)

    img7 = improve_contrast(img=img7,clipLimit=3,tileSize=(3,3),kernelSize=(3,3),sigma=6)

    write_image(img7,OUTPUT_PATH + "Space7.png")

    #################################################################