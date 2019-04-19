#coding:utf-8

import numpy as np
from PIL import Image,ImageDraw
from sklearn.cluster import KMeans
from scipy.misc import imsave
from scipy.ndimage import morphology,measurements
from skimage import draw 
from image_process import *
from localimgs import *
from util.config import * 
import sys,requests,time,json,os,traceback

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

localtxtpath = '/Users/haoshuang/invoice_ocr/data/test_local/local/'

def boxlist_fromfile(imgname,localtxtpath):
	mainname = imgname.split('/')[-1].split('.')[0]
	txtname = localtxtpath+mainname+'.txt'

	boxlist = []
	f = open(txtname,'r')
	linelist = f.readlines()
	# line_num = len(f.readlines())
	for line in linelist:
		line=line.strip().strip('[]') 
		boxs = line.split(' ')
		while '' in boxs:
			boxs.remove('')
		boxarr = np.array(boxs)
		boxarr = boxarr.astype(np.int16)
		onebox = [boxarr[0],boxarr[1],boxarr[6],boxarr[7]]#左上右下
		boxlist.append(onebox)

		# print(boxarr)
	return boxlist

def box_in_crop(boxlist,crop):
	boxesarr = np.array(boxlist)
	# print boxesarr.shape
	top = crop[0]
	bottom = crop[1]
	left = crop[2]
	right = crop[3]

	index = where(np.logical_and(np.logical_and(boxesarr[:,0]>=left,boxesarr[:,2]<=right),np.logical_and(boxesarr[:,1]>=top, boxesarr[:,3]<=bottom)))

	# print boxesarr[index]

	box_in = boxesarr[index]

	boxesout = []
	for i in range(len(box_in)):
		flagok = isarow(box_in[i])
		if flagok:
			boxesout.append(box_in[i])
	return boxesarr[index]

def isarow(boxin):
	width = boxin[2]-boxin[0]
	height = boxin[3]-boxin[1]

	if width/height>2:
		return True
	else:
		return False

def compute_left_crop(boxes,crop):
	#判断最左上角的文字条是否在正确范围内（暂时不用）
	#去掉不在范围内的文字条
	#？？？？？？

	#取最左上角的文字条为结果
	# print boxes
	row = np.min(boxes[:,1])
	index_row = where(boxes[:,1]==row)

	boxes_byrow = boxes[index_row]
	col = np.max(boxes_byrow[:,2])

	# print row,col

	index = where(np.logical_and(boxes[:,1]==row,boxes[:,2]==col))

	boxout = boxes[index]
	# print boxout

	return boxout[0]

def compute_rightbotm_crop(boxes,crop):
	
	col = np.min(boxes[:,0])
	index_col = where(boxes[:,0]==col)

	boxes_bycol = boxes[index_col]

	row = np.max(boxes_bycol[:,1]) 

	index = where(np.logical_and(boxes[:,1]==row,boxes[:,0]==col))
 	boxout = boxes[index]
	return boxout[0]

def remove_boxes(removebox,boxes):

	boxout = []
	for box in boxes:
		if (box!=removebox).any():
			boxout.append(box)
	return np.array(boxout)

def compute_righttop_crop(boxes,crop):
	# boxes[0,1,2,3] = 左上右下
	# 计算data
	# print boxes
	row = np.max(boxes[:,1])
	index_row = where(boxes[:,1]==row)

	boxes_byrow = boxes[index_row]
	col = np.max(boxes_byrow[:,2]) 
	index = where(np.logical_and(boxes[:,1]==row,boxes[:,2]==col))
 	box_data = boxes[index]

 	# print "box_data" ,box_data

 	next_boxes = remove_boxes(box_data,boxes)

 	# print next_boxes
	# 计算number1
	col = np.min(next_boxes[:,0])
	index_col = where(next_boxes[:,0]==col)
	boxes_bycol = next_boxes[index_col]
	row = np.min(boxes_bycol[:,1])

	index = where(np.logical_and(next_boxes[:,1]==row,next_boxes[:,0]==col))
 	box_number1 = next_boxes[index]
 	next_boxes = remove_boxes(box_number1,next_boxes)
 	# print "box_number1" ,box_number1
 	# print next_boxes
	
	# 计算number2
	row = np.max(next_boxes[:,1])
	index_row = where(next_boxes[:,1]==row)
	boxes_byrow = next_boxes[index_row]

	col = np.max(boxes_byrow[:,2])
	index = where(np.logical_and(next_boxes[:,1]==row,next_boxes[:,2]==col))
 	box_number2 = next_boxes[index]
 	next_boxes = remove_boxes(box_number2,next_boxes)
 	# print "box_number2" ,box_number2
 	# print next_boxes
	# 计算code2
	row = np.max(next_boxes[:,1])
	index_row = where(next_boxes[:,1]==row)
	boxes_byrow = next_boxes[index_row]

	col = np.max(boxes_byrow[:,2])
	index = where(np.logical_and(next_boxes[:,1]==row,next_boxes[:,2]==col))
 	box_code2 = next_boxes[index]
 	# next_boxes = remove_boxes(box_number2,next_boxes)
 	# print "box_code2" ,box_code2

	return box_number1[0],box_number2[0],box_code2[0],box_data[0]

def boxlist_fromapi(imgname):
	payload = [('image_file',('my.jpeg',open(imgname,'rb'),'image/jpeg',))]
	r = requests.post('http://10.39.14.233:8388/text_detection/detector/', files=payload,proxies=None)
	j=json.loads(r.text)

	boxes = j['boxes']

	boxlist = []
	for b in boxes:
		onebox = [b[0][0],b[0][1],b[1][0],b[1][1]]
		# print onebox
		boxlist.append(onebox)
	return boxlist

def compute_crop(imgname):

	crop_righttop,crop_rigthbottom,crop_left = get_crops(imgname)
	# boxlist = boxlist_fromfile(imgname,localtxtpath)

	boxlist = boxlist_fromapi(imgname)



	boxes_righttop = box_in_crop(boxlist,crop_righttop)
	boxes_rightbotm = box_in_crop(boxlist,crop_rigthbottom)
	boxes_left = box_in_crop(boxlist,crop_left)


	code1_box = compute_left_crop(boxes_left,crop_left)
	number1_box,number2_box,code2_box,data_box = compute_righttop_crop(boxes_righttop,crop_righttop)
	money_box = compute_rightbotm_crop(boxes_rightbotm,crop_rigthbottom)


	crop_multi = []
	crop_multi.append(box2crop(code1_box))
	crop_multi.append(box2crop(code2_box))
	crop_multi.append(box2crop(number1_box))
	crop_multi.append(box2crop(number2_box))
	crop_multi.append(box2crop(data_box))
	crop_multi.append(box2crop(money_box))


	img_org =  Image.open(imgname)

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

	return crop_multi,imgout
