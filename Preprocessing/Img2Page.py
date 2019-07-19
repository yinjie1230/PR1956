import os
import numpy as np
import cv2
import json

def MahalonobisDistance(x, mean, cov):
    # definition of M-distance, not used in this file
    v = x - mean
    dis = np.dot(v, np.linalg.inv(cov))
    dis = np.dot(dis, v.T)
    return dis ** 0.5


def SegByMahalonobisDistance(matrix, mean, cov, thr):
    # fast implementation
    cov_inv = np.linalg.inv(cov)
    mat1 = matrix[:, :, 0] - mean[0]
    mat2 = matrix[:, :, 1] - mean[1]
    dis = np.multiply(mat1, mat1) * cov_inv[0, 0] + np.multiply(mat2, mat2) * cov_inv[1, 1] + np.multiply(mat1, mat2) * \
          cov_inv[0, 1] * 2
    return dis < thr ** 2  # mask for segmentation

def order_points(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
    (tr, br) = rightMost

    return np.array([tl, tr, br, bl])

def CropRect(img, rect):
    box = cv2.boxPoints(rect)
    box = order_points(box)
    # get width and height of the detected rectangle
    if rect[2]<-45:
        height,width = int(rect[1][0]),int(rect[1][1])
    else:
        width,height = int(rect[1][0]),int(rect[1][1])

    src_pts = box.astype("float32")
    # corrdinate of the points in box points after the rectangle has been
    # straightened
    dst_pts = np.array([[0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1],
                        [0, height - 1]], dtype="float32")

    # the perspective transformation matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # directly warp the rotated rectangle to get the straightened rectangle
    warped = cv2.warpPerspective(img, M, (width, height))
    return warped


def TrainGaussian(file):
    img = cv2.imread(file)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(img_hsv)

    data = np.concatenate((h.reshape(1, -1), s.reshape(1, -1)), axis=0)

    # parameters to estimate
    mean = np.mean(data, axis=1)
    cov = np.cov(data)
    return mean, cov


def Zeropadding(filename):
    filename = filename.split('.')[0]
    book, f, n = filename.split('_')
    f = f[0] + f[1:].zfill(4)   #zeropadding
    n = n
    return book + '_' + f + '_' + n

def OutputRect(outputdir,filename,rect,splitPage=False):
    if splitPage:
        #split the rect to two smaller rects (two pages)
        if rect[2] < -45:
            height, width = int(rect[1][0]), int(rect[1][1])
            theta = np.deg2rad(rect[2] + 90)
            norm = width / 4
            vect = [norm * np.sin(theta), norm * np.cos(theta)]
            rect0 = [[rect[0][0] - vect[0], rect[0][1] - vect[0]], [height, width / 2], rect[2]]
            rect1 = [[rect[0][0] + vect[1], rect[0][1] + vect[1]], [height, width / 2], rect[2]]
        else:
            width, height = int(rect[1][0]), int(rect[1][1])
            theta = np.deg2rad(rect[2])
            norm = width / 4
            vect = [norm * np.sin(theta), norm * np.cos(theta)]
            rect0 = [[rect[0][0] - vect[0], rect[0][1] - vect[0]], [width / 2, height], rect[2]]
            rect1 = [[rect[0][0] + vect[1], rect[0][1] + vect[1]], [width / 2, height], rect[2]]
        with open(os.path.join(outputdir, filename + '_0.json'), 'w') as outfile:
            json.dump(rect0, outfile)
            print('writing results to ' + os.path.join(outputdir, filename + '_0.json'))
        with open(os.path.join(outputdir, filename + '_1.json'), 'w') as outfile:
            json.dump(rect1, outfile)
            print('writing results to ' + os.path.join(outputdir, filename + '_1.json'))
    else:
        with open(os.path.join(outputdir, filename), 'w') as outfile:
            json.dump(rect, outfile)
            print('writing results to ' + os.path.join(outputdir, filename))

#file = 'trainset/1.tif'
#mean, cov = TrainGaussian(file)
mean=np.array([20.76549421, 68.80967093])
cov=np.array([[ 2.00308826, -7.05376449],
       [-7.05376449, 46.9934228 ]])
thr = 2.5

inputdir = '../../data'
outputdir = '../../output'
if not os.path.isdir(outputdir):
    os.mkdir(outputdir)
    print('creating directory ' + outputdir)
clean_names = lambda x: [i for i in x if i[0] != '.']

target_names = os.listdir(inputdir)
target_names = clean_names(target_names)
for target_name in target_names:
    print("processing ",target_name)

    img = cv2.imread(os.path.join(inputdir, target_name))

    img_downsample = cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(img)))
    k = 2 ** 3
    img_rgb = cv2.cvtColor(img_downsample, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

    mask = SegByMahalonobisDistance(img_hsv[:, :, 0:2], mean, cov, thr)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.erode(mask.astype(np.uint8), kernel, iterations=1)

    ret, labels = cv2.connectedComponents(mask.astype(np.uint8))
    size1,label1=0,0
    size2,label2=0,0
    # find the largest two regions
    for i in range(1,ret):
        if np.sum((labels==i).astype(int))>size1:
            size2,label2=size1,label1
            size1=np.sum((labels==i).astype(int))
            label1=i
        elif np.sum((labels==i).astype(int))>size2:
            size2=np.sum((labels==i).astype(int))
            label2=i
    # fit a rect
    cnts, _ = cv2.findContours((labels == label1).astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rect0 = cv2.minAreaRect(cnts[0] * k)

    filename=Zeropadding(target_name)
    # seg pages to page if necessary
    if rect0[1][0]*rect0[1][1]>0.8*img.shape[0]*img.shape[1]:
        OutputRect(outputdir,filename,rect0,splitPage=True)
    elif rect0[1][0]*rect0[1][1]>0.38*img.shape[0]*img.shape[1]:
        #page(s) may be detected seperately
        cnts1,_ = cv2.findContours((labels==label2).astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
        rect1=cv2.minAreaRect(cnts1[0]*k)
        if rect1[1][0]*rect1[1][1]>0.38*img.shape[0]*img.shape[1]:
            if rect0[0][0]<rect1[0][0]:
                OutputRect(outputdir,filename + '_0.json',rect0)
                OutputRect(outputdir,filename + '_1.json',rect1)
            else:
                OutputRect(outputdir,filename + '_1.json',rect1)
                OutputRect(outputdir,filename + '_0.json',rect0)
        else:
            OutputRect(outputdir,filename + '_0.json',rect0)
            print("warning: only one output for "+target_name)
    else:
        print("warning: no output for "+target_name)

    import pdb;

    pdb.set_trace()