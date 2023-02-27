######### CENG 466 THE3 #########
# Berke Can Ünlü        2381028 #
# Buğra Burak Altıntaş  2380079 #
#################################


import numpy as np
import cv2 as cv
import os
import time

INPUT_PATH = './THE3_Images/'
OUTPUT_PATH = './Outputs/'

# Calculate distance between two pixels
def calculateDistance(point1, point2):
    return np.sqrt(np.sum((point1 - point2)**2))

class KMeans:
    def __init__(self, dataset, K=2):
        """
        :param dataset: 2D numpy array, the whole dataset to be clustered
        :param K: integer, the number of clusters to form
        """
        self.K = K
        self.dataset = dataset
        # each cluster is represented with an integer index
        # self.clusters stores the data points of each cluster in a dictionary
        self.clusters = {i: [] for i in range(K)}
        # cluster 0 -> p1,p2,...
        # cluster 1 -> p5,p6,...

        # self.cluster_centers stores the cluster mean vectors for each cluster in a dictionary
        self.cluster_centers = {i: None for i in range(K)}
        # cluster 0 -> mean0
        # cluster 1 -> mean1
        # you are free to add further variables and functions to the class
    
    def __initialize(self):
        print("Initializing kmeans...")
        min_, max_ = np.min(self.dataset, axis=0), np.max(self.dataset, axis=0)
        centers = [np.random.uniform(min_, max_) for _ in range(self.K)]
        for i in range(self.K):
            self.cluster_centers[i] = centers[i]
    

        #print("centers:", centers)
        for i in range(self.K):
            self.cluster_centers[i] = centers[i]
        print("Initialization done.")

    def __assign(self):
        print("Assigning points to clusters...")
        
        
        self.clusters = {i: [] for i in range(self.K)}
        for point in self.dataset:
            # calculate distance to each cluster center
            min_dist = 100000000000
            min_index = 0
            for i in range(self.K):
                cluster_center = self.cluster_centers[i]
                dist = calculateDistance(point,cluster_center)
                if dist < min_dist:
                    min_dist = dist
                    min_index = i
            cluster = min_index
            # assign to closest cluster center
            self.clusters[cluster].append(point)
        print("Assignment done. ")
     
    def __update_centers(self):
        print("Updating cluster centers...")
        centers = []
        terminate = [False for _ in range(self.K)]
        tol = 0.0001
        for i in range(self.K):
            if len(self.clusters[i]) == 0:
                mean = self.cluster_centers[i]
            else:
                mean = np.array(self.clusters[i]).mean(axis=0)
            centers.append(mean)
            diff = calculateDistance(mean,self.cluster_centers[i])
            if diff < tol:
                terminate[i] = True
            else:
                terminate[i] = False
            
            if not terminate[i]:
                self.cluster_centers[i] = centers[i]
        
        term_cond = True
        for i in range(self.K):
            if not terminate[i]:
                term_cond = False
                break
        print("Updating done.")

        return term_cond

    # Fit the model 
    def run(self):
        """Kmeans algorithm implementation"""
        print("Running kmeans...")
        self.__initialize()
        terminate = False
        # assign points to clusters initially
        self.__assign()
        iter = 0
        # We set iteration limit to 300 to prevent long running times
        while iter < 300:
            print("Iteration: ", iter)
            start = time.time()
            
            # calculate means of each cluster
            terminate = self.__update_centers()

            # if all cluster means does not change anymore, stop
            if terminate:
                break
            
            # assign points to closest cluster center
            self.__assign()
            end = time.time()
            print("This iteration takes: ", "{:.3f}".format(end-start), " seconds.")
            print("---------------------------------------------------")
            iter += 1

        return self.cluster_centers, self.clusters


# Read image
def read_image(img_path, rgb = True):
    img = None
    if rgb == True:
        img = cv.imread(img_path)
    else:
        img = cv.imread(img_path)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return img

# Write image
def write_image(img, output_path):
    cv.imwrite(output_path,img)

# Write BGR channels
def write_bgr_channels(img, output_path):
    b,g,r = cv.split(img)
    
    cv.imwrite(output_path + "_b.png",b)
    cv.imwrite(output_path + "_g.png",g)
    cv.imwrite(output_path + "_r.png",r)

# Write HSI channels
def write_hsi_channels(img, output_path):
    h,s,i = cv.split(img)

    cv.imwrite(output_path + "_h.png",h)
    cv.imwrite(output_path + "_s.png",s)
    cv.imwrite(output_path + "_i.png",i)

# Convert BGR image to HSI
def BGR2CIE(img):
    # split image to BGR channels
    b,g,r = cv.split(img)
    shape = img.shape

    # create Intensity channel
    I = np.zeros((shape[0],shape[1]))

    # create empty image for CIE channels
    converted_img = np.zeros((shape[0],shape[1]), dtype=list)

    # for every pixel
    for i in range(shape[0]):
        for j in range(shape[1]):
            # calculate B + G + R
            sum_of_colors = np.int64(b[i][j]) + np.int64(g[i][j]) + np.int64(r[i][j])
            # If sum of colors is 0, set s to a small value to avoid division by 0
            if sum_of_colors == 0:
                s = 0.0001
            else:
                s = sum_of_colors
            
            # calculate normalized B and R and Intensity
            # Intensity is stored to convert CIE image to BGR
            I[i][j] = s / 3
            normalized_b = b[i][j] / s
            normalized_r = r[i][j] / s
            converted_img[i][j] = [normalized_b,normalized_r]

    return converted_img,I

# Convert CIE image to BGR
def CIE2BGR(xy,I):
    shape = xy.shape
    # create empty image for BGR channels
    img = np.zeros((shape[0],shape[1],3))

    # for every pixel
    for i in range(shape[0]):
        for j in range(shape[1]):
            # get x and y values
            x = xy[i][j][0]
            y = xy[i][j][1]
            
            # Blue channel
            img[i][j][0] = I[i][j] * x
            # Green channel
            img[i][j][1] = I[i][j] * (1 - x - y)
            # Red channel
            img[i][j][2] = I[i][j] * y
    return img

# Convert BGR image to HSI
def BGR2HSI(img):
    # split the image into its BGR components
    b,g,r = cv.split(img)
    # convert from BGR to HSV
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    # split the HSV image into its components
    h,s,v = cv.split(hsv)
    
    # get the shape of the image
    shape = v.shape
    
    # create intensity channel
    intensity = np.zeros((shape[0],shape[1]), dtype=np.uint8)
    
    # for every pixel
    for i in range(shape[0]):
        for j in range(shape[1]):
            # Get B G R values
            B = np.int64(b[i][j])
            G = np.int64(g[i][j])
            R = np.int64(r[i][j])
            
            # Calculate intensity and truncate 8-bit values
            BGR = B + G + R 
            intensity[i][j] = BGR / 3
    
    # merge the channels back
    return cv.merge((h,s,intensity))
    
# Detect edges in an image with SOBEL FILTER
def detect_edges(img, type = "BGR"):

    # In order to reduce noise in the image, apply gaussian blur with kernel size (3,3), sigma = 1
    img = cv.GaussianBlur(img, (3,3), 1)
    
    if type == "BGR":
        # split image to BGR channels
        b,g,r = cv.split(img)

        # Calculate horizontal and vertical gradients for each channel
        b_horizontal = cv.Sobel(b, cv.CV_64F, 1, 0, ksize=3)
        b_vertical = cv.Sobel(b, cv.CV_64F, 0, 1, ksize=3)
        
        g_horizontal = cv.Sobel(g, cv.CV_64F, 1, 0, ksize=3)
        g_vertical = cv.Sobel(g, cv.CV_64F, 0, 1, ksize=3)
        
        r_horizontal = cv.Sobel(r, cv.CV_64F, 1, 0, ksize=3)
        r_vertical = cv.Sobel(r, cv.CV_64F, 0, 1, ksize=3)
        
        # Convert the result to 8 bit
        abs_b_h = cv.convertScaleAbs(b_horizontal)
        abs_b_v = cv.convertScaleAbs(b_vertical)
        
        abs_g_h = cv.convertScaleAbs(g_horizontal)
        abs_g_v = cv.convertScaleAbs(g_vertical)
        
        abs_r_h = cv.convertScaleAbs(r_horizontal)
        abs_r_v = cv.convertScaleAbs(r_vertical)
        
        # Calculate the weighted sum of horizontal and vertical gradients
        blue_edge = cv.addWeighted(abs_b_h, 0.5, abs_b_v, 0.5, 0)
        green_edge = cv.addWeighted(abs_g_h, 0.5, abs_g_v, 0.5, 0)
        red_edge = cv.addWeighted(abs_r_h, 0.5, abs_r_v, 0.5, 0)
        
        # Merge the channels back
        edges = cv.merge((blue_edge, green_edge, red_edge))
        
    if type == "HSI":
        # split image to HSI channels
        h,s,i = cv.split(img)

        # Calculate horizontal and vertical gradients for each channel
        h_horizontal = cv.Sobel(h, cv.CV_64F, 1, 0, ksize=3)
        h_vertical = cv.Sobel(h, cv.CV_64F, 0, 1, ksize=3)
        
        s_horizontal = cv.Sobel(s, cv.CV_64F, 1, 0, ksize=3)
        s_vertical = cv.Sobel(s, cv.CV_64F, 0, 1, ksize=3)
        
        i_horizontal = cv.Sobel(i, cv.CV_64F, 1, 0, ksize=3)
        i_vertical = cv.Sobel(i, cv.CV_64F, 0, 1, ksize=3)
        
        # Convert the result to 8 bit
        abs_h_h = cv.convertScaleAbs(h_horizontal)
        abs_h_v = cv.convertScaleAbs(h_vertical)
        
        abs_s_h = cv.convertScaleAbs(s_horizontal)
        abs_s_v = cv.convertScaleAbs(s_vertical)
        
        abs_i_h = cv.convertScaleAbs(i_horizontal)
        abs_i_v = cv.convertScaleAbs(i_vertical)
        
        # Calculate the weighted sum of horizontal and vertical gradients
        hue_edge = cv.addWeighted(abs_h_h, 0.5, abs_h_v, 0.5, 0)
        saturation_edge = cv.addWeighted(abs_s_h, 0.5, abs_s_v, 0.5, 0)
        intensity_edge = cv.addWeighted(abs_i_h, 0.5, abs_i_v, 0.5, 0)
        
        # Merge the channels back
        edges = cv.merge((hue_edge, saturation_edge, intensity_edge))
    
    return edges

# Create colormap from source image
# Our algorithm will use this colormap to colorize the target image
# 1) we convert the source image to grayscale
# 2) we calculate the mean of each channel for each gray level
# 3) we create a color map with the mean values for each gray level.
#    If there is no pixel with a specific gray level, we use the gray level as the mean value for each channel.
def createColorMap(img):
    grayimg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    shape = grayimg.shape
    color_map = np.zeros((256,3), dtype=np.uint8)

    for i in range(256):
        indices = np.where(grayimg == i)
        blue = np.mean(img[indices[0],indices[1],0]) if len(indices[0]) != 0 else i
        green = np.mean(img[indices[0],indices[1],1]) if len(indices[0]) != 0 else i
        red = np.mean(img[indices[0],indices[1],2]) if len(indices[0]) != 0 else i
        color_map[i][0] = blue
        color_map[i][1] = green
        color_map[i][2] = red


    return color_map

# Colorize the target image using color map originated from the source image
def color_images(source,img):
    # Create the color map
    color_map = createColorMap(source)
    shape = img.shape

    # create the channels for the new image
    new_b = np.zeros((shape[0],shape[1]), dtype=np.uint8)
    new_g = np.zeros((shape[0],shape[1]), dtype=np.uint8)
    new_r = np.zeros((shape[0],shape[1]), dtype=np.uint8)

    # for each pixel
    for i in range(shape[0]):
        for j in range(shape[1]):
            # get the corresponding color from the color map for each channel
            new_b[i][j] = color_map[img[i][j]][0]
            new_g[i][j] = color_map[img[i][j]][1]
            new_r[i][j] = color_map[img[i][j]][2]

    # merge the channels back
    return cv.merge((new_b,new_g,new_r))



def detect_faces_hsv(img, K):
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    h,s,v = cv.split(hsv_img)

    shape = img.shape
    dataset = []

    for i in range(shape[0]):
        for j in range(shape[1]):
            dataset.append([h[i][j],s[i][j],v[i][j]])

    dataset = np.array(dataset)
    kmeans = KMeans(dataset, K)
    cluster_centers, clusters = kmeans.run()

    new_h = np.zeros((shape[0],shape[1]))
    new_s = np.zeros((shape[0],shape[1]))   
    new_i = np.zeros((shape[0],shape[1]))

    for i in range(shape[0]):
        for j in range(shape[1]):
            color = [h[i][j],s[i][j],v[i][j]]
            color = np.array(color)
            distances = [] 
            min_dist = 100000000000
            min_index = 0
            for k in range(kmeans.K):
                dist = calculateDistance(color, cluster_centers[k])
                distances.append(dist)
                if dist < min_dist:
                    min_dist = dist
                    min_index = k
            cluster = min_index
            new_h[i][j] = int(cluster_centers[cluster][0])
            new_s[i][j] = int(cluster_centers[cluster][1])
            new_i[i][j] = int(cluster_centers[cluster][2])

    return cv.merge((new_h,new_s,new_i))
    

def detect_faces(img, K):
    b,g,r = cv.split(img)
    shape = img.shape
    dataset = []

    for i in range(shape[0]):
        for j in range(shape[1]):
            dataset.append([b[i][j],g[i][j],r[i][j]])

    print("preprocessing done")
    dataset = np.array(dataset)
    kmeans = KMeans(dataset, K)
    print("kmeans object creation done")
    cluster_centers, clusters = kmeans.run()

    new_b = np.zeros((shape[0],shape[1]))
    new_g = np.zeros((shape[0],shape[1]))   
    new_r = np.zeros((shape[0],shape[1]))

    for i in range(shape[0]):
        for j in range(shape[1]):
            color = [b[i][j],g[i][j],r[i][j]]
            color = np.array(color)
            distances = [] 
            min_dist = 100000000000
            min_index = 0
            for k in range(kmeans.K):
                dist = calculateDistance(color, cluster_centers[k])
                distances.append(dist)
                if dist < min_dist:
                    min_dist = dist
                    min_index = k
            cluster = min_index
            new_b[i][j] = int(cluster_centers[cluster][0])
            new_g[i][j] = int(cluster_centers[cluster][1])
            new_r[i][j] = int(cluster_centers[cluster][2])

    return cv.merge((new_b,new_g,new_r))


def detect_faces_cie(img, K):
    xy, intensity = BGR2CIE(img)
    shape = img.shape
    dataset = []

    for i in range(shape[0]):
        for j in range(shape[1]):
            dataset.append([xy[i][j][0],xy[i][j][1]])
    dataset = np.array(dataset)
    kmeans = KMeans(dataset, K)
    cluster_centers, clusters = kmeans.run()

    new_b = np.zeros((shape[0],shape[1]))
    new_r = np.zeros((shape[0],shape[1]))

    for i in range(shape[0]):
        for j in range(shape[1]):
            color = [xy[i][j][0],xy[i][j][1]]
            color = np.array(color)
            distances = [] 
            min_dist = 100000000000
            min_index = 0
            for k in range(kmeans.K):
                dist = calculateDistance(color, cluster_centers[k])
                distances.append(dist)
                if dist < min_dist:
                    min_dist = dist
                    min_index = k
            cluster = min_index
            new_b[i][j] = int(cluster_centers[cluster][0])
            new_r[i][j] = int(cluster_centers[cluster][1])

    new_img = CIE2BGR(np.dstack((new_b,new_r)),intensity)
    return new_img
    


if __name__ == '__main__':
    # Create output folder if not exists
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    ####### READ IMAGES #######
    source_1 = read_image(INPUT_PATH + '1_source.png')
    source_2 = read_image(INPUT_PATH + '2_source.png')
    source_3 = read_image(INPUT_PATH + '3_source.png')
    source_4 = read_image(INPUT_PATH + '4_source.png')

    # one iteration of kmeans takes 6 minutes, so we decided to rescale the image 2
    scaled_source_2 = cv.resize(source_2, (int(source_2.shape[1]/10), int(source_2.shape[0]/10)), interpolation = cv.INTER_AREA)
    
    
    gray_1 = read_image(INPUT_PATH + '1.png', False)
    # This is done due to the fact that the image is rotated 90 degrees when read by opencv
    gray_1 = cv.rotate(gray_1, cv.ROTATE_90_COUNTERCLOCKWISE)

    gray_2 = read_image(INPUT_PATH + '2.png', False)
    gray_3 = read_image(INPUT_PATH + '3.png', False)
    gray_4 = read_image(INPUT_PATH + '4.png', False)

    ####### FACE DETECTION #######

    print('Detecting faces for image1 bgr...')
    faces_1 = detect_faces(source_1, 3)
    print('------------------------------------')

    print("Writing 1_faces.png bgr...")
    write_image(faces_1,OUTPUT_PATH + '1_faces.png')
    print('------------------------------------')

    print('Detecting faces for image2 bgr...')
    faces_2 = detect_faces(scaled_source_2, 5)
    print('------------------------------------')

    print("Writing 2_faces.png bgr...")
    write_image(faces_2,OUTPUT_PATH + '2_faces.png')
    print('------------------------------------')

    print('Detecting faces for image3 bgr...')
    faces_3 = detect_faces(source_3, 6)
    print('------------------------------------')
    
    print("Writing 3_faces.png bgr...")
    write_image(faces_3,OUTPUT_PATH + '3_faces.png')
    print('------------------------------------')
    
    ####### PSEUDO COLORING #######
    
    ####### IMAGE 1 #######
    
    print('Creating color map for image 1...')
    color_map_1 = createColorMap(source_1)
    print('------------------------------------')
    
    # bgr colored image
    print('Creating BGR colored image for image 1...')
    bgr_pseudo_colored_1 = color_images(source_1, gray_1)
    print('------------------------------------')

    
    # convert bgr to hsi
    print('Creating HSI colored image for image 1...')
    hsi_pseudo_colored_1 = BGR2HSI(bgr_pseudo_colored_1)
    print('------------------------------------')
    
    # Detect edges with Sobel filter for HSI and BGR images
    print('Detecting edges for source image 1 in BGR...')
    bgr_edges_1 = detect_edges(source_1, "BGR")
    print('------------------------------------')

    hsi_source_1 =BGR2HSI(source_1)
    
    print('Detecting edges for source image 1 in HSI...')
    hsi_edges_1 = detect_edges(hsi_source_1, "HSI")
    print('------------------------------------')
    
    # Save image
    print('Writing pseudo colored bgr image 1...')
    write_image(bgr_pseudo_colored_1, OUTPUT_PATH + '1_colored.png')
    print('------------------------------------')
    
    print('Writing edges in rgb image 1...')
    write_image(bgr_edges_1, OUTPUT_PATH + '1_rgb_colored_edges.png')
    print('------------------------------------')
    
    print('Writing edges in hsi image 1...')
    write_image(hsi_edges_1, OUTPUT_PATH + '1_hsi_colored_edges.png')
    print('------------------------------------')
    
    ####### END OF IMAGE 1 #######
    
    ####### IMAGE 2 #######
    
    # create color map
    print('Creating color map for image 2...')
    color_map_2 = createColorMap(source_2)
    print('------------------------------------')
    
    # bgr colored image
    print('Creating BGR colored image for image 2...')
    bgr_pseudo_colored_2 = color_images(source_2, gray_2)
    print('------------------------------------')
    
    # convert bgr to hsi
    print('Creating HSI colored image for image 2...')
    hsi_pseudo_colored_2 = BGR2HSI(bgr_pseudo_colored_2)
    print('------------------------------------')
    
    # Detect edges with Sobel filter for HSI and BGR images
    print('Detecting edges for source image 2 in BGR...')
    bgr_edges_2 = detect_edges(source_2, "BGR")
    print('------------------------------------')

    hsi_source_2 = BGR2HSI(source_2)
    
    print('Detecting edges for source image 2 in HSI...')
    hsi_edges_2 = detect_edges(hsi_source_2, "HSI")
    print('------------------------------------')
    
    # Save image
    print('Writing pseudo colored bgr image 2...')
    write_image(bgr_pseudo_colored_2, OUTPUT_PATH + '2_colored.png')
    print('------------------------------------')

    print('Writing edges in rgb image 2...')
    write_image(bgr_edges_2, OUTPUT_PATH + '2_rgb_colored_edges.png')
    print('------------------------------------')

    print('Writing edges in hsi image 2...')
    write_image(hsi_edges_2, OUTPUT_PATH + '2_hsi_colored_edges.png')
    print('------------------------------------')
    
    ####### END OF IMAGE 2 #######
    
    ####### IMAGE 3 #######
    
    # create color map
    print('Creating color map for image 3...')
    color_map_3 = createColorMap(source_3)
    print('------------------------------------')
    
    # bgr colored image
    print('Creating BGR colored image for image 3...')
    bgr_pseudo_colored_3 = color_images(source_3, gray_3)
    print('------------------------------------')

    # convert bgr to hsi
    print('Creating HSI colored image for image 3...')
    hsi_pseudo_colored_3 = BGR2HSI(bgr_pseudo_colored_3)
    print('------------------------------------')
    
    # Detect edges with Sobel filter for HSI and BGR images
    print('Detecting edges for source image 3 in BGR...')
    bgr_edges_3 = detect_edges(source_3, "BGR")
    print('------------------------------------')

    hsi_source_3 = BGR2HSI(source_3)
    
    print('Detecting edges for source image 3 in HSI...')
    hsi_edges_3 = detect_edges(hsi_source_3, "HSI")
    print('------------------------------------')
    
    # Save image
    print('Writing pseudo colored bgr image 3...')
    write_image(bgr_pseudo_colored_3, OUTPUT_PATH + '3_colored.png')
    print('------------------------------------')
    
    print('Writing edges in rgb image 3...')
    write_image(bgr_edges_3, OUTPUT_PATH + '3_rgb_colored_edges.png')
    print('------------------------------------')
    
    print('Writing edges in hsi image 3...')
    write_image(hsi_edges_3, OUTPUT_PATH + '3_hsi_colored_edges.png')
    print('------------------------------------')
    
    ####### END OF IMAGE 3 #######
    
    ####### IMAGE 4 #######
    
    # create color map
    print('Creating color map for image 4...')
    color_map_4 = createColorMap(source_4)
    print('------------------------------------')
    
    # bgr colored image
    print('Creating BGR colored image for image 4...')
    bgr_pseudo_colored_4 = color_images(source_4, gray_4)
    print('------------------------------------')
    
    # convert bgr to hsi
    print('Creating HSI colored image for image 4...')
    hsi_pseudo_colored_4 = BGR2HSI(bgr_pseudo_colored_4)
    print('------------------------------------')
    
    # Save image
    print('Writing pseudo colored bgr image 4...')
    write_image(bgr_pseudo_colored_4, OUTPUT_PATH + '4_colored.png')
    print('------------------------------------')