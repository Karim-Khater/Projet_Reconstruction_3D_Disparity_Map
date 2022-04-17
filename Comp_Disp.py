######################################################################################################################################################
# I tested with only a grill of camera of 4x4 but it should work with 3x3 and above 
# The images provided have to be in order of left to right and top to bottom for the arrays creation
# So starting from (0,0) to (0,3) to at the end (3,3)
# The folder /Validation/WoodenHouse/ is causing problems so i didn't use it  
######################################################################################################################################################
import cv2  # for the reading of images
import numpy as np  # for the arrays
from tqdm import trange # to visualize the progress
import math # for the sqrt function

"""
Function to convert from .exr to .png
and to return an array of path to disparity maps
to make accessing them easier later on

path : the path to the disparity images .
n : the number of images available in the path .

the disparity maps in the folder have to have their name in this format
"Disp_"numberofdisparitymap".exr"
"""
def EXR_2_PNG(path,n):
    size = int(math.sqrt(n))    # to get the size of rows and columns which has to be equal to each other
    disp_array = np.zeros((size,size)).astype(str)  # array of strings(the paths to the disparity maps) shape is 2D (4x4)
    index = 0   # for the name of the disparity map 
    for i in range(size):
        for j in range(size):
            count = path + "Disp_" + str(index) + ".exr"    # path of each disparity map
            disp_array[i,j] = count
            

            # for saving the disparity maps as png to see them
            im_exr = cv2.imread(count,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)  
            
            countEXR = "Disp_2_png/Disp_" + str(index) + ".png"
            index = index + 1
            cv2.imwrite(countEXR,im_exr)

    return disp_array



"""
function to check if the input giving is power of 2 to have only the same number of rows and columns for the camera grill
"""
def is_power_of_two(n):
    return (n != 0) and (n & (n-1) == 0)

"""
This function is for calculating the error visually
Blue means that there is no difference between the image projected and the image of reference
Red means that the pixel projected is behind the image of reference
Green means that the pixel projected is in front of the image of reference
"""
def diff_error_calculation_img(diff):
    rows, cols,_ = diff.shape
    out_of_bound_min = 0
    out_of_bound_max = 0
    in_bound = 0
    for i in range(rows):
        for j in range(cols):
            for k in range(3):
                if(diff[i,j,k] < 0):
                    out_of_bound_min = 1
                elif (diff[i,j,k] > 0):
                    out_of_bound_max = 1
                elif (diff[i,j,k] ==0):
                    in_bound = 1
            if(out_of_bound_min ==1) :
                diff[i,j] =(0,0,255) #red
                out_of_bound_min = 0
            elif(out_of_bound_max == 1):
                diff[i,j] =(0,255,0) #green
                out_of_bound_max = 0
            elif(in_bound == 1):
                diff[i,j] =(255,0,0) #blue
                in_bound = 0
    return diff

"""
 function to check the position of every camera in the grid of cameras.
 givin a path and the number of images in this path
 it will return an array of images representing a grid of cameras .
 works exactly like EXR_2_PNG
"""
def cam_pos(path,n):
    if(is_power_of_two(n)):
        size = int(math.sqrt(n)) # to get the number of columns and rows 
        imgs_array = np.zeros((size,size)).astype(str)
        index = 0
        for i in range(size):
            for j in range(size):
                imgs_array[i,j] = str(path) + "Image_" + str(index) + ".png" # path of each image
                index = index +1
    return imgs_array

"""
this function is responsable for projecting an image by using the data from the image's disparity map and
another image in the grid and that image's disparity map

disp1 is the disparity map of img_source
disp2 is the disparity map of img_resnei
i1,j1 = img_source coordinates in the grid of cameras
i2,j2 = img_res coordinates in the grid of cameras

img_res = image projected
"""
def project_img(img_source,img_res,disp1,disp2,i1,j1,i2,j2):
    rows,columns,_ = img_source.shape
    for x1 in trange(rows):
        for y1 in range(columns):
            x2 = x1 + ((i1 - i2) * disp1[x1,y1])    # x2  = x1 + (i1-i2).δ
            y2 = y1 + ((j1 - j2) * disp1[x1,y1])    # y2  = y2 + (j1-j2).δ
            
            if(x2 > rows-1 or y2 > columns-1 or x2 < 0 or y2 <0 ) :  # to check if x2 or y2 are out of range of the rows and columns
                continue
            
            if(np.sum(disp1[x1,y1]) >= np.sum(disp2[x2,y2])):   # If the value of disparity of the source is closer we will use it else we will keep the current value in the pixel
                img_res[x2,y2] = img_source[x1,y1]

    return img_res
"""
this function is responsable for projecting a disparity map by using data from another disparity map of an image in the grid

i1,j1 = disp_source coordinates in the grid of cameras
i2,j2 = disp_res coordinates in the grid of cameras

disp_res = disparity map projected from another disparity map
"""
def project_disp(disp_source,disp_res,i1,j1,i2,j2):
    rows , columns = disp_source.shape
    print(disp_source.shape)
    for x1 in trange(rows):
        for y1 in range(columns):
            x2 = x1 + ((i1 - i2) * disp_source[x1,y1])  # x2  = x1 + (i1-i2).δ
            y2 = y1 + ((j1 - j2) * disp_source[x1,y1])  # y2  = y2 + (j1-j2).δ

            if(x2 > rows-1 or y2 > columns-1 or x2 < 0 or y2 <0 ) :   # to check if x2 or y2 are out of range of the rows and columns
                continue
            if(np.sum(disp_source[x1,y1]) >= np.sum(disp_res[x2,y2])): # If the value of disparity of the source is closer we will use it else we will keep the current value in the pixel
                disp_res[x2,y2] = disp_source[x1,y1]
           
    return disp_res

def project_disp_float(disp_float_source,disp_float_res,disp_source,disp_res,i1,j1,i2,j2):
    rows , columns = disp_source.shape
    print(disp_source.shape)
    for x1 in trange(rows):
        for y1 in range(columns):
            x2 = x1 + ((i1 - i2) * disp_source[x1,y1])  # x2  = x1 + (i1-i2).δ
            y2 = y1 + ((j1 - j2) * disp_source[x1,y1])  # y2  = y2 + (j1-j2).δ

            if(x2 > rows-1 or y2 > columns-1 or x2 < 0 or y2 <0 ) :   # to check if x2 or y2 are out of range of the rows and columns
                continue
            if(np.sum(disp_source[x1,y1]) >= np.sum(disp_res[x2,y2])): # If the value of disparity of the source is closer we will use it else we will keep the current value in the pixel
                disp_float_res[x2,y2] = disp_float_source[x1,y1]
           
    return disp_float_res

"""
Function to call project_disp and project_img 
"""
def project(img1,img2,disp1,disp2,x1,y1,x2,y2):
   
    #read image path
    img1 = cv2.imread(img1)     #[x1,y1]
    img2 = cv2.imread(img2)     #[x2,y2]  
    disp1 = cv2.imread(disp1,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH) #[x1,y1]
    disp2 = cv2.imread(disp2,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH) #[x2,y2]
    #transform to array
    disp1 = np.asarray(disp1).astype(int)
    disp2 = np.asarray(disp2).astype(int)

    # OBJECTIF 1 PROJECTION OF DISPARITY MAP ONTO ANOTHER POINT OF VIEW

    disp_projected = np.zeros_like(disp1)
    print(" START DISPARITY PROJECTION ")
    disp_projected = project_disp(disp1,disp_projected,x1,y1,x2,y2)
    diff_disp = disp_projected - disp2
    cv2.imwrite("Diff_Disparity_projected_once.png",diff_disp)
    cv2.imwrite("Disp_Projected_once.png",disp_projected)

    # OBJECTIF 2 PROJECTION OF IMAGE
    img_projected = np.zeros_like(img1)
    img_projected = project_img(img1,img_projected,disp1,disp2,x1,y1,x2,y2)
    #print(img_projected)
    diff_img = img_projected - img2
    diff_img = diff_error_calculation_img(diff_img)
    print("START IMAGE PROJECTION")
    cv2.imwrite("Diff_projected_Image_once.png",diff_img)
    cv2.imwrite("Image_Projected_once.png",img_projected)


"""
This function is  responsable on getting the neighbours of a camera in the grill givin it's position

example :
i = 1
j = 2

0xxx
0x1x
0xxx
0000

it will return an array of all the positions of x  
the array is 1-dimensional
"""
def neighbours(nb_total,i,j):
    #To determine the size of the array and to check corners and conditions
    if (nb_total > 4):
        size = int(math.sqrt(nb_total))
        if((i==0 and (j ==0 or j==size-1))or (i==size-1  and (j == size -1 or j==0))):
            neighbors = 3
        elif(i==0 or j==0 or i==size-1 or j==size-1):
            neighbors = 5
        else:
            neighbors = 8

    array_pos = np.zeros((neighbors*2))
    count = 0
    for x in range(size):
        for y in range(size):
            if(x == i and y == j ):
                continue
            if((x < i+2 and y <j+2)and (x> i-2 and y > j-2 )):
                array_pos[count] = x
                count = count + 1
                array_pos[count] = y
                count = count + 1
                if(count == neighbors*2):
                    break
        if(count == neighbors*2):
                break
    return array_pos   

"""
disps : array of string include path to disparity maps

For testing it is recommended to use the image at position 2,2 to project on
so i=2 j=2 and compare the result with the image in the folder Church/Disp_11.png

"""

def multiple_projection_img(disps,imgs,i,j):

    neighbours_cams = neighbours(imgs.size,i,j)
    
    img_init = cv2.imread(imgs[i,j])
    img_projected = np.zeros_like(img_init)
    img_projected = np.asarray(img_projected).astype(int)

    disp_init = cv2.imread(disps[i,j],  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    disp_projected = np.zeros_like(disp_init)
    disp_projected = np.asarray(disp_projected).astype(int)
    # To apply the function project_img multiple times depending on the projected image neighbours
    # It increment by 2 because it is one dimensional and includes the position x and y of each camera
    # so to project with each image the position of x has to be pair and y has to be odd
    for x in range(0,len(neighbours_cams),2):   
        # Position of a neighbours camera 
        pos_x1 = int(neighbours_cams[x])
        pos_y1 = int(neighbours_cams[x+1])

        # Init of source Image
        img_source = cv2.imread(imgs[pos_x1,pos_y1])       
        img_source = np.asarray(img_source).astype(int)
        
        # Init of Disparity of Source Image
        disp_source = cv2.imread(disps[pos_x1,pos_y1],  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)       
        disp_source = np.asarray(disp_source).astype(int)
  
        # Init of Disparity of Projected Image
        disp_projected = project_disp(disp_source,disp_projected,pos_x1,pos_y1,i,j)
        
        img_projected = project_img(img_source,img_projected,disp_source,disp_projected,pos_x1,pos_y1,i,j)
        """
        # For seeing the process with each projection
        string_img = "imgs_Projected_multiples"+str(x)+".png"
        cv2.imwrite(string_img,img_projected)
        """
    cv2.imwrite("imgs_Projected_multiples.png",img_projected)   
    
    diff_img = img_projected - img_init
    diff_img = diff_error_calculation_img(diff_img)
    cv2.imwrite("Diff_imgs_multiples.png",diff_img)


def multiple_projection_disp_float(disps,i,j):
    neighbours_cams = neighbours(disps.size,i,j)
    disp_init = cv2.imread(disps[i,j],  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    disp_projected = np.zeros_like(disp_init)
    disp_projected = np.asarray(disp_projected).astype(int)
    disp_float_res = np.zeros_like(disp_init)
    # To apply the function project_disp multiple times depending on the projected disparity neighbours
    for x in range(0,len(neighbours_cams),2):
        # Position of a neighbours camera 
        pos_x1 = int(neighbours_cams[x])
        pos_y1 = int(neighbours_cams[x+1])

        # Init of Disparity map of the image source
        disp_source = cv2.imread(disps[pos_x1,pos_y1],  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)       
        disp_source = np.asarray(disp_source).astype(int)
        disp_float_source = cv2.imread(disps[pos_x1,pos_y1],  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)       

        disp_projected = project_disp_float(disp_float_source,disp_float_res,disp_source,disp_projected,pos_x1,pos_y1,i,j)

    cv2.imwrite("Disps_Projected_multiples.png",disp_projected)   
    
    diff_disp = disp_projected - disp_init
    print(diff_disp)
    cv2.imwrite("Diff_Disparity_disp_multiples.png",diff_disp)

def multiple_projection_disp(disps,i,j):
    neighbours_cams = neighbours(disps.size,i,j)
    disp_init = cv2.imread(disps[i,j],  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    disp_projected = np.zeros_like(disp_init)
    disp_projected = np.asarray(disp_projected).astype(int)
    # To apply the function project_disp multiple times depending on the projected disparity neighbours
    for x in range(0,len(neighbours_cams),2):
        # Position of a neighbours camera 
        pos_x1 = int(neighbours_cams[x])
        pos_y1 = int(neighbours_cams[x+1])

        # Init of Disparity map of the image source
        disp_source = cv2.imread(disps[pos_x1,pos_y1],  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)       
        disp_source = np.asarray(disp_source).astype(int)

        disp_projected = project_disp(disp_source,disp_projected,pos_x1,pos_y1,i,j)
    
    cv2.imwrite("Disps_Projected_multiples.png",disp_projected)   
    
    diff_disp = disp_projected - disp_init
    cv2.imwrite("Diff_Disparity_disp_multiples.png",diff_disp)



def multiple_projection(imgs,disps,i,j):

    # OBJECTIF 3 : PROJETER PLUSIEURS IMAGES SUR LE MEME POINT DE VUE
    print(" START DISPARITIES PROJECTION ")
    multiple_projection_disp_float(disps,i,j)

    print(" START IMAGES PROJECTION ")
    multiple_projection_img(disps,imgs,i,j)
    




"""
THE GRILL OF CAMERAS HAS TO BE IN A SQUARE SHAPE AND 4x4 TO BE MOST EFFECIENT

"""
def main():

    path = "Validation/Church/"
    nb_cameras = 16
    imgs = cam_pos(path,nb_cameras)
    disps = EXR_2_PNG(path,nb_cameras)
    # positions from [0;3]
    pos_i1 = 2
    pos_i2 = 3
    pos_j1 = 2
    pos_j2 = 3

    img1 = imgs[pos_i1,pos_j1]
    img2 = imgs[pos_i2,pos_j2]
    
    disp1 = disps[pos_i1,pos_j1]
    disp2 = disps[pos_i2,pos_j2]

    # OBJECTIF 1 & 2 :
    print(" <<<<<<<<<<<<<<<<<<<<<<< START SOLO PROJECTION >>>>>>>>>>>>>>>>>>>>>> ")
    project(img1,img2,disp1,disp2,pos_i1,pos_j1,pos_i2,pos_j2)
    
    
    # OBJECTIF 3 :
    # positions from [0;3]
    pos_to_project_x = 2
    pos_to_project_y = 2
    
    # To check the neighbours of the camera
    #pos_array = neighbours(nb_cameras,pos_to_project_x,pos_to_project_y)
    #print(pos_array)
    

    print(" <<<<<<<<<<<<<<<<<<<<<<< START MULTIPLE PROJECTION >>>>>>>>>>>>>>>>>>>>>> ")
    multiple_projection(imgs,disps,pos_to_project_x,pos_to_project_y)


if __name__ == '__main__':
    main()
