######### CENG 466 THE4 #########
# Berke Can Ünlü        2381028 #
# Buğra Burak Altıntaş  2380079 #
#################################

import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from skimage import segmentation, color
from skimage.future import graph
import matplotlib.pyplot as plt
import cv2 as cv
import os
from enum import Enum
import networkx as nx
from netgraph import Graph

INPUT_PATH = './THE4_Images/'
OUTPUT_PATH = './Outputs/'


class ColorSpace(Enum):
    BGR = 0
    HSV = 1
    LAB = 2
    YUV = 3

# Read image
def read_image(img_path : str, rgb = True) -> cv.Mat:    
    if rgb == True:
        img = cv.imread(img_path)
        return img

    img = cv.imread(img_path)
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img

# Write image
def write_image(img : cv.Mat, output_path : str):
    cv.imwrite(output_path,img)

# Detect Flowers using morphological operations
def detect_flowers(img : cv.Mat, img_name: str, colorspace : ColorSpace, dilation_kernel_size : tuple, erosion_kernel_size : tuple, dilation_iterations : int, erosion_iterations : int) -> cv.Mat:
    ### Convert image to the given colorspace
    if colorspace == ColorSpace.HSV:
        img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    elif colorspace == ColorSpace.LAB:
        img = cv.cvtColor(img, cv.COLOR_BGR2LAB)
    elif colorspace == ColorSpace.YUV:
        img = cv.cvtColor(img, cv.COLOR_BGR2YUV)
    
    # convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # blur the image to reduce noise
    blurred = cv.GaussianBlur(gray,(5,5),1)

    # convert the grayscale image to binary image
    ret, thresh = cv.threshold(blurred,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)

    # negate the image to make flowers white and background black
    negative = cv.bitwise_not(thresh)

    # MORPHOLOGICAL OPERATIONS TO DETECT FLOWERS
    
    # Create kernel with kernel size
    dilation_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, dilation_kernel_size)
    erosion_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, erosion_kernel_size)

    # Erode the image
    eroded = cv.erode(negative, erosion_kernel, iterations=erosion_iterations)

    # Dilate the eroded image
    dilated = cv.dilate(eroded, dilation_kernel, iterations=dilation_iterations)


    # Find contours
    contours, hierarchy = cv.findContours(dilated, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)


    ### Convert image to the given colorspace
    if colorspace == ColorSpace.HSV:
        img = cv.cvtColor(img, cv.COLOR_HSV2BGR)
    elif colorspace == ColorSpace.LAB:
        img = cv.cvtColor(img, cv.COLOR_LAB2BGR)
    elif colorspace == ColorSpace.YUV:
        img = cv.cvtColor(img, cv.COLOR_YUV2BGR)

    # Draw contours
    img_contours = cv.drawContours(image=img, contours=contours, contourIdx=-1, color=(255,255,0), thickness=9)

    print('The number of flowers in image ' + img_name + ' is ' + str(len(contours)))

    return img_contours, dilated

# Mean Shift Segmentation
def mean_shift_segmentation(img : cv.Mat, img_name : str, quantile : float, n_samples : int):
    print("Starting Mean Shift segmentation for image : " + img_name)
    shape = img.shape
    dataset = []
    
    img = np.array(img)

    print("Creating dataset...")
    dataset = img.reshape((shape[0]*shape[1],3))
    print("--------------------")

    #estimate bandwidth for meanshift
    print("Estimating bandwidth...")
    bandwidth = estimate_bandwidth(dataset, n_jobs=-1,n_samples=n_samples, quantile=quantile)
    print("Estimated bandwidth : ", bandwidth)
    print("--------------------")

    #meanshift
    print("Performing Mean Shift...")
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    print("--------------------")
    print("Fitting dataset...")
    ms.fit(dataset)
    print("--------------------")
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_

    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    print("number of estimated clusters : %d" % n_clusters_)
    
    #create segmented image
    print("Creating segmented image...")
    segmented_image = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            segmented_image[i][j] = cluster_centers[labels[i*shape[1]+j]]
    print("--------------------")

    segmented_image_cv = segmented_image.astype(np.uint8)
    segmented_image_cv = cv.cvtColor(segmented_image_cv, cv.COLOR_BGR2RGB)

    rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    labels = labels.reshape(shape[0],shape[1])

    print("writing segmented image")
    prepare_plots(rgb_img, segmented_image_cv, img_name+"_mean_shift",labels)
    print("--------------------")
    print("N-cut segmentation finished for image : " + img_name)

# N-cut Segmentation
def ncut_segmentation(img : cv.Mat, img_name : str, n_segments : int, sigma : float):
    print("Starting N-cut segmentation for image : " + img_name)
    # Convert image to RGB
    print("converting to RGB from BGR...")
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    print("------------------")

    print("Starting preprocessing using k-means segmentation to use in N-cut...")
    labels1 = segmentation.slic(img, compactness=30, n_segments=n_segments,
                            start_label=1)
    print("------------------")

    out1 = color.label2rgb(labels1, img, kind='avg', bg_label=0)

    print("Creating RAG mean color...")
    g = graph.rag_mean_color(img, labels1, mode='similarity', sigma=sigma)
    print("------------------")

    print("N-cut segmentation...")
    labels2 = graph.cut_normalized(labels1, g)
    print("------------------")
    print("Creating segmented image...")
    segmented_img = color.label2rgb(labels2, img, kind='avg', bg_label=0)
    print("------------------")

    print("Plotting...")
    prepare_plots(img, segmented_img, img_name+"_ncut", labels2)
    print("------------------")
    print("N-cut segmentation finished for image : " + img_name)
    





def prepare_plots(img : cv.Mat, segmented_img: cv.Mat, img_name : str, labels):
    ### Image original image
    ### Segmentation map --> mean shift colored image
    ### Boundary Overlay --> contours of the segmented image
    ### Tree relationship structure (See chapter 13, Figure 52 for an example) 
    ### Region adjacency graph (See chapter 13, Figure 58 for an example)
    fig,ax = plt.subplots(2,3,figsize=(20,20))

    # Boundary overlay
    boundary_overlay = segmentation.mark_boundaries(img, labels, (0, 255, 0), mode='thick')
    ####################

    # Tree structure
    copy_img = boundary_overlay.copy()
    copy_img = copy_img.astype(np.uint8)
    gray_img = cv.cvtColor(copy_img, cv.COLOR_RGB2GRAY)
    contours, hierarchy = cv.findContours(gray_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(copy_img, contours, -1, (0,255,0), 1)

    edges = parse_hieararchy(hierarchy)
    G = nx.from_edgelist(edges, create_using=nx.DiGraph)
    


    
    
    ####################

    # Region adjacency graph
    g = graph.rag_mean_color(img, labels, mode='similarity', sigma=1)
    ####################
    
    

    ax[0][0].imshow(img)
    ax[0][0].set_title('Original Image')
    ax[0][1].imshow(segmented_img)
    ax[0][1].set_title('Segmented Image')
    ax[0][2].imshow(boundary_overlay)
    ax[0][2].set_title('Boundary Overlay')
    Graph(G, node_layout='dot', ax = ax[1][0])
    ax[1][0].set_title('Tree Structure')
    graph.show_rag(labels, g, img, img_cmap=None, edge_cmap='plasma', edge_width=1, ax = ax[1][1], border_color=(0,1,0))
    ax[1][1].set_title('Region Adjacency Graph')
    plt.savefig(OUTPUT_PATH + img_name + '_plots.png')
    
def parse_hieararchy(contours,hierarchy):
    edges = []
    for idx in len(contours):
        next = hierarchy[0][idx][0]
        prev = hierarchy[0][idx][1]
        child = hierarchy[0][idx][2]
        parent = hierarchy[0][idx][3]
    return edges

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    ############# OBJECT COUNTING ################

    # Read image A1
    img = read_image(img_path = INPUT_PATH + 'A1.png')

    # Detect flowers using morphological operations
    # (11,11) 8,6 seems okay!
    contour_img, morph_img = detect_flowers(img = img, img_name = 'A1', colorspace = ColorSpace.HSV, 
                                            dilation_kernel_size = (11,11), erosion_kernel_size=(11,11),
                                            dilation_iterations = 8, erosion_iterations = 6)

    # Write image
    write_image(morph_img, OUTPUT_PATH + 'A1.png')

    # Read image A2
    img = read_image(img_path = INPUT_PATH + 'A2.png')

    # Detect flowers using morphological operations
    contour_img, morph_img = detect_flowers(img = img, img_name = 'A2', colorspace=ColorSpace.YUV, 
                                            dilation_kernel_size = (11,11), erosion_kernel_size=(11,11),
                                            dilation_iterations = 18, erosion_iterations = 12)

    # Write image
    write_image(morph_img, OUTPUT_PATH + 'A2.png')

    # Read image A3
    img = read_image(img_path = INPUT_PATH + 'A3.png')

    # Detect flowers using morphological operations
    contour_img, morph_img = detect_flowers(img = img, img_name = 'A3', colorspace=ColorSpace.LAB, 
                                            dilation_kernel_size = (15,15), erosion_kernel_size=(15,15),
                                            dilation_iterations = 10, erosion_iterations = 14)

    # Write image
    write_image(morph_img, OUTPUT_PATH + 'A3.png')

    ############# SEGMENTATION ################

    # Read image B1
    img = read_image(img_path = INPUT_PATH + 'B1.jpg')
    img = cv.resize(img, (int(img.shape[1]/5), int(img.shape[0]/5)), interpolation = cv.INTER_AREA)

    # Segment image
    #mean_shift_segmentation(img = img, img_name = 'B1', quantile=0.07, n_samples=1000)
    ncut_segmentation(img, img_name = 'B1', sigma=160,n_segments=400)
    mean_shift_segmentation(img = img, img_name = 'B1', quantile=0.07, n_samples=1000)

    # Read image B2
    img = read_image(img_path = INPUT_PATH + 'B2.jpg')
    img = cv.resize(img, (int(img.shape[1]/5), int(img.shape[0]/5)), interpolation = cv.INTER_AREA)

    # Segment image
    mean_shift_segmentation(img = img, img_name = 'B2', quantile=0.1, n_samples=10000)
    ncut_segmentation(img, img_name = 'B2', sigma=160,n_segments=400)

    # Read image B3
    img = read_image(img_path = INPUT_PATH + 'B3.jpg')

    # Segment image
    mean_shift_segmentation(img = img, img_name = 'B3', quantile=0.2, n_samples=10000)
    ncut_segmentation(img, img_name = 'B3', sigma=160,n_segments=400)

    # Read image B4
    img = read_image(img_path = INPUT_PATH + 'B4.jpg')
    img = cv.resize(img, (int(img.shape[1]/5), int(img.shape[0]/5)), interpolation = cv.INTER_AREA)


    # Segment image
    mean_shift_segmentation(img = img, img_name = 'B4', quantile=0.1, n_samples=10000)
    ncut_segmentation(img, img_name = 'B4', sigma=160,n_segments=400)





