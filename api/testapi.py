#coding: utf-8
import sys,requests,time,json,os,traceback
from PIL import Image
# from pylab import *
import time
import datetime
import random

# def get_timemark():
# 	timestr = time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
# 	timemark = timestr+'_'+'%03d'%(random.randint(1,100))
# 	return timemark

def get_list(path):
	return [os.path.join(path,f) for f in os.listdir(path) ]

def usage():
	print 'Usage:'
	print 'python testapi.py image_folder_dir'
	sys.exit(1)


imlist = get_list(sys.argv[1])

for imagename in imlist:
	# print impath

	if len(sys.argv)!=2: usage()
	# imagename=sys.argv[1]
	print 'tesing %s' % imagename

	payload = [('image_file',('my.jpeg',open(imagename,'rb'),'image/jpeg',))]
	# payload = {'image_file':open(imagename,'rb')}

	t1=time.time()
	try:
		r = requests.post('http://10.39.66.115:8288/ocr/invoice_4/', files=payload,proxies=None)
		# r = requests.post('http://localhost:8080/ocr/invoice_4/', files=payload,proxies=None)

		print(r.text)
		# j=json.loads(r.text)
		# print(j)

	except Exception as e:
		print("exception: "+str(e))	
		traceback.print_exc(file=sys.stdout)

	time.sleep(10)	