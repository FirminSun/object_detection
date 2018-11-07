import numpy as np
from math import *
import cv2
from skimage import exposure

def hor_flipped(im): #水平翻转
    im = im[:, ::-1, :]  # 图像翻转
    return im

def ver_flipped(im): #竖直翻转
    im = im[::-1, :, :]
    return im

def bright_image(im,gamma): #调整亮度
    im = exposure.adjust_gamma(im, gamma)
    return im

def rotate_image(img,angle): #根据指定旋转角进行旋转
    height,width=img.shape[0],img.shape[1]
    heightNew = int(width * fabs(sin(radians(angle))) + height * fabs(cos(radians(angle))))
    widthNew = int(height * fabs(sin(radians(angle))) + width * fabs(cos(radians(angle))))

    matRotation = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)

    matRotation[0, 2] += (widthNew - width) / 2  # 重点在这步，目前不懂为什么加这步
    matRotation[1, 2] += (heightNew - height) / 2  # 重点在这步

    imgRotation = cv2.warpAffine(img, matRotation, (widthNew, heightNew), borderValue=(0, 0, 0))
    return imgRotation

def shift_image(image, offset, isseg=False): #根据指定平移位置进行平移
    from scipy.ndimage.interpolation import shift
    order = 0
    return shift(image, (int(offset[0]), int(offset[1]), 0), order=order, mode='nearest')

def zoom_image(image, factor_x,factor_y, isseg=False):  
    from scipy.ndimage import interpolation
    order = 0 if isseg == True else 3
    newimg = interpolation.zoom(image, (float(factor_y), float(factor_x), 1.0), order=order, mode='nearest')
    return newimg

def resize_image(image,size):
    resize_im=cv2.resize(image,size)
    return resize_im

def _crop(img,box):
    img=img[box[1]:box[3], box[0]:box[2]]
    return img

def _get_crop_bbox(img_size,crop_size,position):
    crop_bbox=np.zeros((5,4),dtype=int)
    crop_bbox[0]=np.array((0,0,crop_size[0],crop_size[1]))
    crop_bbox[1]=np.array((0,img_size[1]-crop_size[1],crop_size[0],img_size[1]))
    crop_bbox[2]=np.array((img_size[0]-crop_size[0],0,img_size[0],crop_size[1]))
    crop_bbox[3]=np.array((img_size[0]-crop_size[0],img_size[1]-crop_size[1],img_size[0],img_size[1]))
    crop_bbox[4]=np.array((int(img_size[0]/2-crop_size[0]/2),int(img_size[1]/2-crop_size[1]/2),
                           int(img_size[0]/2+crop_size[0]/2),int(img_size[1]/2+crop_size[1]/2)))
    position_list=['lu','ld','ru','rd','m']
    position_index=position_list.index(position)
    return crop_bbox[position_index]

def random_crop_image(img, crop_size,position):
    img_size=(img.shape[1],img.shape[0])
    crop_box = _get_crop_bbox(img_size, crop_size,position)
    crop_img = _crop(img, crop_box)
    return crop_img
