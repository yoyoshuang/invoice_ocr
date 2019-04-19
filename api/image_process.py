#coding:utf-8

import numpy as np
from PIL import Image,ImageDraw
from sklearn.cluster import KMeans
from scipy.misc import imsave
from scipy.ndimage import morphology,measurements
from PIL.ImageFont import truetype
from skimage import color
from sauvola import *
from util.config import * 

if DEBUG == 1:
	from pylab import * 


def white_balance(img):

	imgout = np.zeros(img.shape)

	imgR = img[:,:,0]  
	imgG = img[:,:,1] 
	imgB = img[:,:,2]
	# print(imgR)
	meanR = np.mean(imgR.flatten())
	meanG = np.mean(imgG.flatten())
	meanB = np.mean(imgB.flatten())

	KB = (meanR + meanG + meanB) / (3 * meanB) 
	KG = (meanR + meanG + meanB) / (3 * meanG)  
	KR = (meanR + meanG + meanB) / (3 * meanR)

	imgout[:,:,0] = (imgR * KR) 
	imgout[:,:,1] = (imgG * KG) 
	imgout[:,:,2] = (imgB * KB)
 
	return imgout


def remove_narrow(index,threshold):

	# print index
	index_width = get_row_width(index)
	# print index_width
	indexout = []
	for i in range(len(index_width)):
		if index_width[i]<threshold:
			index[i*2] = 0
			index[i*2+1] = 0
		else:
			indexout.append(index[i*2])
			indexout.append(index[i*2+1])
	# print index

	return np.array(indexout)

def get_big_row(index):
	# print index
	row_width = get_row_width(index)

	# print row_width
	maxindex = np.argmax(row_width)*2

	# print index[maxindex],index[maxindex+1]

	return tuple((index[maxindex],index[maxindex+1]))



def get_row_width(seq):
	# even 偶数 odd 奇数
	seqlen = len(seq)
	# print(seqlen)
	if seqlen % 2 == 0:
		end = seqlen-1
	else: 
		end = seqlen-2

	seq_odd =  seq[1:end+1:2]
	seq_even = seq[0:end:2]

	# print(seq_odd)
	# print(seq_even)	
	seq_diff = seq_odd-seq_even
	return seq_diff


def getmaxloc(index):
	diff_index = diff_seq_sec(index)
	# print(diff_index)
	indexmax = np.argmax(diff_index)*2

	return int((index[indexmax]+index[indexmax-1])/2)

def mask_img(mask, img):
	
	typeflag = img.shape
	# print typeflag
	imgcopy = img.copy()

	if len(typeflag)>2:
		for i in range(typeflag[-1]):
			imgcopy[mask,i] = 0

	else:
		imgcopy[mask] = 0

	imgout = img-imgcopy
	return imgout

def sauvola_process(img):

	img_gray=color.rgb2gray(img)

	img_gray = img_gray*255
	bi = sauvola(img_gray,0.1,6)
	# gray()
	# figure()
	# imshow(img_gray)
	# show()
	return bi.astype(np.bool)

def leave_blue2(imgin):

	wbimg = white_balance(imgin)

	# gray()
	# figure()
	# imshow(wbimg)
	# show()

	masknobg =sauvola_process(wbimg)
	# gray()
	# figure()
	# imshow(masknobg)
	# show()
	imgin = mask_img(masknobg,imgin)

	# gray()
	# figure()
	# imshow(imgin)
	# show()

	imginB = extract_BLUE(imgin)

	# gray()
	# figure()
	# imshow(imginB)
	# show()

	return imginB

def remove_RED(img):

	imgr = img[:,:,0]
	imgg = img[:,:,1]
	imgb = img[:,:,2]

	maskR1 = imgr>imgg

	maskR1 = imgr>(imgg+imgb)*0.75
	# maskR2 = imgr>imgb*2
	# maskR = maskR1 * maskR2

	maskR_inv = 1- maskR1*1

	return maskR1

# def remove_noise(imgin):
	
# 	# 腐蚀膨胀去横线
# 	imgin = morphology.binary_erosion(imgin,np.ones((2,1)),iterations = 2)
# 	imgin = morphology.binary_dilation(imgin,np.ones((2,1)),iterations = 2)

# 	# 去左右窄竖线
# 	index_col = projection(imgin,'col',3)[0]
# 	print index_col
# 	if (index_col[1]-index_col[0])<5:
# 		imgin[:,index_col[0]:index_col[1]+1] = 0
# 	index_col = -np.sort(-index_col)
# 	if (index_col[0]-index_col[1])<5:
# 		imgin[:,index_col[1]:index_col[0]+1] = 0
# 	gray()
# 	figure()
# 	imshow(imgin)
# 	show()
	
# 	return imgin

def leave_blue(imgin):

	imgin = white_balance(imgin)
	# gray()
	# figure()
	# imshow(imgin)
	# show()

	kmeansflag = 1
	w,h,d = tuple(imgin.shape)	
	masknobg,morep = kmeans_process(imgin)
	print (morep*1.00/(w*h))
	if morep<w*h*0.72:
		kmeansflag = 0
		return imgin,kmeansflag
	
	# gray()
	# figure()
	# imshow(masknobg)
	# show()
	imgin = mask_img(masknobg,imgin)

	# figure()
	# imshow(imgin)
	# show()

	imginB = extract_BLUE(imgin)

	return imginB,kmeansflag

def extract_BLUE(img):
	imgr = img[:,:,0]
	imgg = img[:,:,1]
	imgb = img[:,:,2]
	# 方法一
	maskB1 = imgb>imgg
	maskB2 = imgb>imgr
	maskB = maskB1 * maskB2
	# 方法二
	# maskB = imgb>imgg

	return maskB


def extract_RED(img):
	imgr = img[:,:,0]
	imgg = img[:,:,1]
	imgb = img[:,:,2]
	# 方法一
	maskR1 = imgr>imgg
	maskR2 = imgr>imgb
	maskR = maskR1 * maskR2
	# 方法二
	# maskR = imgr>imgb

	return maskR

def img_bineray(img):
	imgout = img[:,:,0]+img[:,:,1]+img[:,:,2]
	mask = imgout>1
	imgout = mask*1
	return imgout


def kmeans_process(img):
	# img = img/255
	w,h,d = tuple(img.shape)
	# print img.shape


	img2D = img.reshape((w*h),d)
	kmeans = KMeans(n_clusters = 2,random_state = 0).fit(img2D)
	labels2D = kmeans.predict(img2D)
	# labels = labels2D.reshape(w,h)

	#多点为背景设为0
	num1 = sum(labels2D)
	morep = max(num1,w*h-num1)
	# print num1
	if num1>w*h/2: 
		labels2D = 1-labels2D
	labels = labels2D.reshape(w,h)
	return labels.astype(np.bool),morep


# font = truetype("./calibri.tff",30)
def box2crop(box):
	x1,y1,x2,y2=box[0],box[1],box[2],box[3]
	p1 = (x1,y1)
	p2 = (x2,y2)
	crop = [p1,p2]
	return crop
	

def diff_seq(seq):
	# seq_tmp = np.array([0])
	seq_tmp2 = np.concatenate((seq,[seq[-1]]))
	seq_tmp3 = np.concatenate(([seq[0]],seq))
	seq_tmp2 = seq_tmp2-seq_tmp3
	return seq_tmp2

def diff_seq_sec(seq):
	# even 偶数 odd 奇数
	seqlen = len(seq)
	# print(seqlen)
	if seqlen % 2 == 0:
		end = seqlen-1
	else: 
		end = seqlen-2


	seq_odd =  np.concatenate(([seq[0]],seq[1:end-1:2]))
	seq_even = seq[0:end:2]
	# seq_even = np.concatenate((np.concatenate((seq[0:end:2]))

	# print(seq_odd)
	# print(seq_even)	
	seq_diff = seq_even-seq_odd
	return seq_diff

def projection(crop,direction,threshold):
	if direction == "row":
		crop_d = np.sum(crop,axis=1,keepdims =True).T
	if direction == "col":
		crop_d = np.sum(crop,axis=0,keepdims =True)

	# plt.plot(crop_d[0])
	# plt.show()

	cropr_d_tmp = (crop_d>threshold) *1

	# plt.plot(cropr_d_tmp[0])
	# plt.show()

	# print(croprighttop_c)
	cropr_d_tmp2 = np.array([0])
	cropr_d_tmp3 = np.concatenate((cropr_d_tmp2,cropr_d_tmp[0]))
	cropr_d_tmp4 = np.concatenate((cropr_d_tmp[0],cropr_d_tmp2))
	cropr_d_tmp4 = cropr_d_tmp4-cropr_d_tmp3
	# print(croprighttop_c_tmp4)
	index = np.where(cropr_d_tmp4 != 0)
	# index = -np.sort(-index[0])

	return index

def draw_box(img,box,text):
	x1,y1,x2,y2=box[0],box[1],box[2],box[3]
	# ImageDraw.Draw(img).line([(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)], fill=(255,0,0), width=4)
	ImageDraw.Draw(img).line([(x1,y1),(x1,y2),(x2,y2),(x2,y1),(x1,y1)], fill=(255,0,0), width=4)
	return img
	