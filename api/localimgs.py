#coding:utf-8

import numpy as np
from PIL import Image,ImageDraw
from sklearn.cluster import KMeans
from scipy.misc import imsave
from scipy.ndimage import morphology,measurements
from skimage import draw 
from image_process import *

if DEBUG == 1:
	from pylab import * 

class ele_box:
	def __init__(self,locationbox):
		self.r0 = 0
		self.r1 = locationbox.shape[0]
		self.c0 = 0
		self.c1 = locationbox.shape[1]
		self.crop = locationbox
	def showcrop(self):
		r0 = self.r0
		r1 = self.r1
		c0 = self.c0
		c1 = self.c1

		gray()
		figure()
		imshow(self.crop[r0:r1,c0:c1])
		show()

	def getcrop(self):
		r0 = self.r0
		r1 = self.r1
		c0 = self.c0
		c1 = self.c1
		return self.crop[r0:r1,c0:c1]


def get_crops(imgname):

	# imgname = './fapiao/001.jpg'

	# time_start=time.time()
	img_org =  Image.open(imgname)
	img = np.array(Image.open(imgname))

	# figure()
	# imshow(img)
	# show()

	#归一化
	img = img/255.0
	w,h,d = tuple(img.shape)

	imgnoBG = img

	# 提取红色信息，包括表格和红章
	imgr = imgnoBG[:,:,0]
	imgg = imgnoBG[:,:,1]
	imgb = imgnoBG[:,:,2]

	maskR1 = imgr>imgg
	maskR2 = imgr>imgb
	maskR = maskR1 * maskR2

	imgcopy = imgnoBG.copy()
	imgcopy[maskR] = 0
	imgR = imgnoBG-imgcopy

	# imsave("fapiaoR.png",imgR)
	# 在红色图上提取红章
	imgRr = imgR[:,:,0]
	imgRg = imgR[:,:,1]
	imgRb = imgR[:,:,2]

	maskstamp = imgRr>(imgRg+imgRb)*0.8
	imgcopy = imgR.copy()
	imgcopy[maskstamp] = 0
	img_stamp = imgR-imgcopy
	thirdw = int(w/3)
	img_stamp_half = img_stamp[0:thirdw,:,:]

	# figure()
	# imshow(img_stamp_half)
	# show()

	# 对红章图进行连通域标记，选择面积第二大的区域为红章区域
	bn_stamp = np.zeros((thirdw,h))
	maskstamp_third = maskstamp[0:thirdw,:]
	bn_stamp[maskstamp_third] = 1

	labels_open,nbr  = measurements.label(bn_stamp)

	# imsave("label.png",labels_open)
	# gray()
	# figure()
	# imshow(stamp_open)
	# show()
	count = np.zeros(nbr)
	for i in range(nbr):
		count[i] = np.sum(labels_open==i)
	
	index = np.argsort(-count)[1]
	# print(index)

	maskstamponly = (labels_open==index)
	stamp_only = np.zeros((thirdw,h))
	stamp_only[maskstamponly] = 1

	# gray()
	# figure()
	# imshow(stamp_only)
	# show()

	#计算红章中心点坐标，计算红章宽高
	stamp_points = np.where(stamp_only==1)
	# print(points)
	stamp_x = np.average(stamp_points[0])
	stamp_y = np.average(stamp_points[1])

	stamp_h = np.max(stamp_points[0])-np.min(stamp_points[0])
	stamp_w = np.max(stamp_points[1])-np.min(stamp_points[1])
	# print(stamp_x,stamp_y,stamp_w,stamp_h)

	# 在原图上绘制红章中心点显示
	# rr, cc=draw.circle(int(stamp_x),int(stamp_y),5)
	# draw.set_color(img,[rr, cc],[0,255,0])
	# figure()
	# imshow(img)
	# show()

	#按比例获取截图区域，右下（金额），右上（发票号，日前），左上（号）三个区域
	ratio_right = 1.15
	ratio_right_r = 7
	c0 = int(np.max(stamp_points[1]))+5
	c1 = h
	end_rt = int(stamp_h/ratio_right_r+np.max(stamp_points[0])) 
	croprighttop = img[0:end_rt,c0:c1,:]

	box_righttop = [0,end_rt,c0,c1]

	# gray()
	# figure()
	# imshow(croprighttop)
	# show()

	ratio_right2 = 0.28#0.3
	start_rb_r = int(w/2)
	end_rb_r = int(stamp_h/ratio_right2+np.max(stamp_points[0]))
	start_rb_c = int(stamp_w/2+np.max(stamp_points[1]))
	croprightbotm = img[start_rb_r:end_rb_r,start_rb_c:h]
	# gray()
	# figure()
	# imshow(croprightbotm)
	# show()
	box_rightbotm = [start_rb_r,end_rb_r,start_rb_c,h]

	ratio_left = 1.15
	ratio_left2 = 0.45

	c0 = 0
	c1 = int(np.min(stamp_points[1]-5))
	r1 = int(stamp_h/ratio_right_r+np.max(stamp_points[0])) #int(stamp_x)
	r0 = 0 #int(stamp_x-stamp_h/2)
	cropleft = img[r0:r1,c0:c1,:]

	# figure()
	# imshow(cropleft)
	# show()

	box_left = [r0,r1,c0,c1]
	
	return box_righttop,box_rightbotm,box_left
