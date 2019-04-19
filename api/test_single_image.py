#coding: utf-8
import sys,requests,time,json,os,traceback
from PIL import Image
import time
import datetime
import random


def usage():
	print 'Usage:'
	print 'python test_single_image.py [localhost:8080|invoicehost:8288] imagename'
	sys.exit(1)

if len(sys.argv)!=3: usage()
host = sys.argv[1]
imagename = sys.argv[2]


print 'tesing %s' % imagename

payload = [('image_file',('my.jpeg',open(imagename,'rb'),'image/jpeg',))]

t1=time.time()
try:
	r = requests.post('http://%s/ocr/invoice_4/' % host, files=payload,proxies=None)
	print(r.text)
	
except Exception as e:
	print("exception: "+str(e))	
	traceback.print_exc(file=sys.stdout)
