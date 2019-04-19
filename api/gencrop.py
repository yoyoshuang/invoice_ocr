#coding:utf-8

import numpy as np
from PIL import Image,ImageDraw
from sklearn.cluster import KMeans
from scipy.misc import imsave
from scipy.ndimage import morphology,measurements
from skimage import draw 
from image_process import *
from util.config import * 

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


def compute_crop(imgname):

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

	#计算虚线位置
	ratio_dotline= 0.33
	end_c = int(stamp_w/ratio_dotline+np.max(stamp_points[1]))


	#按比例获取截图区域，右下（金额），右上（发票号，日前），左上（号）三个区域
	ratio_right = 1.15
	ratio_right_r = 7
	start_rt =int(stamp_w/ratio_right+np.max(stamp_points[1])) #列
	end_rt = int(stamp_h/ratio_right_r+np.max(stamp_points[0])) 
	croprighttop = img[0:end_rt,start_rt:end_c,:]
	# gray()
	# figure()
	# imshow(croprighttop)
	# show()


	#对croprighttop 执行局部kmeans,去背景去红色，留蓝色
	croprighttop,kmeansflag = leave_blue(croprighttop)
	if kmeansflag==0:
		croprighttop = leave_blue2(croprighttop)
	
	croprighttop = morphology.binary_erosion(croprighttop,np.ones((2,1)),iterations = 2)
	croprighttop = morphology.binary_dilation(croprighttop,np.ones((2,1)),iterations = 2)
	
	# gray()
	# figure()
	# imshow(croprighttop)
	# show()

	ratio_right2 = 0.28#0.3
	start_rb_r = int(w/2)
	end_rb_r = int(stamp_h/ratio_right2+np.max(stamp_points[0]))
	start_rb_c = int(stamp_w/2+np.max(stamp_points[1]))
	croprightbotm = img[start_rb_r:end_rb_r,start_rb_c:end_c]
	# gray()
	# figure()
	# imshow(croprightbotm)
	# show()

	croprightbotm,kmeansflag = leave_blue(croprightbotm)
	# print kmeansflag
	if kmeansflag==0:
		croprightbotm = leave_blue2(croprightbotm)
	# try:
	# 	gray()
	# 	figure()
	# 	imshow(croprightbotm)
	# 	show()
	# except:
	# 	pass

	ratio_left = 1.15
	ratio_left2 = 0.45
	star_lf_c = int(np.min(stamp_points[1])-(stamp_w/ratio_left2))
	end_lf_c = int(np.min(stamp_points[1])-(stamp_w/ratio_left))
	end_lf_r = int(stamp_x)
	start_lf_r = int(stamp_x-stamp_h/2)
	cropleft = img[start_lf_r:end_lf_r,star_lf_c:end_lf_c,:]

	# figure()
	# imshow(cropleft)
	# show()

	#在局部区域分割四要素

	code1 = ele_box(cropleft)
	code2 = ele_box(croprighttop)
	number1 = ele_box(croprighttop)
	number2 = ele_box(croprighttop)
	date = ele_box(croprighttop)
	money  = ele_box(croprightbotm)

	# 右上提取发票号，编号，日期
	#行方向投影,取最后一行日期
	index =  projection(croprighttop,"row",6)[0]
	# print index
	if (index[1]-index[0])<3:
		index = index[2:]
	index = -np.sort(-index)
	date.r0 = int((index[1]+index[2])/2)#getmaxloc(index)
	# date.r0 = getmaxloc(index)
	number2.r1 = date.r0
	crop_numbers = croprighttop[0:date.r0,:] #不含日期的所有数字区域
	
	# date.showcrop()

	# gray()
	# figure()
	# imshow(crop_numbers)
	# show()

	#对不含日期区域列投影，求中间分隔位置
	index = projection(crop_numbers,"col",5)[0] 
	number1.c0 = int(index[0]-10)
	# print(index)
	#取 index序列中距离最大的两个点求中间位置
	number1.c1 = getmaxloc(index)#
	code2.c0 = number1.c1
	number2.c0 = number1.c1

	crop_numbers1 = croprighttop[0:date.r0,number1.c1:] #右侧两行数字区

	# gray()
	# figure()
	# imshow(crop_numbers1)
	# show()

	index = projection(crop_numbers1,"row",5)[0]
	# print index
	if (index[1]-index[0])<3:
		index = index[2:]
	index = -np.sort(-index)

	# indexmax = getmaxloc()
	code2.r1 = getmaxloc(index)

	# code2.r1 = int((index[1]+index[2])/2)
	code2.r0 = int(index[-1]-10)
	number2.r0 = code2.r1
	number1.r1 = code2.r1

	crop_number1 = number1.getcrop()
	index = projection(crop_number1,"row",5)[0]
	number1.r0 = int(index[0]-10)
	# number1.showcrop()

	crop_data = date.getcrop()
	# date.showcrop()
	index = projection(crop_data,"col",2)[0]
	date.c0 = int(index[0]-20)
	date.c1 = int(index[-1]+20)

	index = projection(crop_data,"row",5)[0]
	date.r1 = date.r0+int(index[-1]+20)

	# money.showcrop()

	#右下提取不含税金额
	index = projection(croprightbotm,"row",5)[0]
	# print index
	row = get_big_row(index)
	# print row
	mh = croprightbotm.shape[0]
	money.r0 = int(row[0]-7)
	money.r1 = np.min((int(row[1]+7),mh))

	#右下提取不含税金额版本2
	# index = projection(croprightbotm,"row",5)[0]
	# index = remove_narrow(index,6)
	# index = -np.sort(-index)
	# mh = croprightbotm.shape[0]
	# money.r0 = int(index[1]-7)
	# money.r1 = np.min((int(index[0]+7),mh))


	# money.showcrop()

	index = projection(money.getcrop(),"col",3)[0]
	index = remove_narrow(index,3)
	money.c0 = int(index[0]-7)


	diff_index = diff_seq_sec(index) 
	# print diff_index
	indexmax = np.argmax(diff_index)*2
	# money.c1 = int((index[indexmax]+index[indexmax-1])/2)
	money.c1 = int(index[indexmax-1]+4)
	# money.showcrop()

	#box = [左，上，右，下]
	code1_box = [star_lf_c+code1.c0,start_lf_r+code1.r0,star_lf_c+code1.c1,start_lf_r+code1.r1]
	code2_box = [start_rt+code2.c0,code2.r0,start_rt+code2.c1,code2.r1]
	number1_box = [start_rt+number1.c0,number1.r0,start_rt+number1.c1,number1.r1]
	number2_box = [start_rt+number2.c0,number2.r0,start_rt+number2.c1,number2.r1] 
	data_box = [start_rt+date.c0,date.r0,start_rt+date.c1,date.r1]
	money_box = [start_rb_c+money.c0,start_rb_r+money.r0,start_rb_c+money.c1,start_rb_r+money.r1]

	crop_multi = []
	crop_multi.append(box2crop(code1_box))
	crop_multi.append(box2crop(code2_box))
	crop_multi.append(box2crop(number1_box))
	crop_multi.append(box2crop(number2_box))
	crop_multi.append(box2crop(data_box))
	crop_multi.append(box2crop(money_box))


	imgout = draw_box(img_org,code1_box,"code1")
	imgout = draw_box(imgout,code2_box,"code2")
	imgout = draw_box(imgout,number1_box,"number1")
	imgout = draw_box(imgout,number2_box,"number2")
	imgout = draw_box(imgout,data_box,"date")
	imgout = draw_box(imgout,money_box,"money")

	# try:
	# 	figure()
	# 	imshow(imgout)
	# 	show()
	# except:
	# 	pass
	# print crop_multi
	return crop_multi,imgout
