#coding: utf-8
import sys,requests,time,json,os,traceback
from PIL import Image
# from pylab import *
import time,re
import datetime
import random
from lcseque import *
# def get_timemark():
# 	timestr = time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
# 	timemark = timestr+'_'+'%03d'%(random.randint(1,100))
# 	return timemark

# test_dir_list=['hs','xiaobai','zhp']
test_dir_list = ['xiaobai_test']
test_map={}
img_list=[]
total_len=total_dis=0

def strip_chinese(s):
	#print s," ".join(hex(ord(n)) for n in s)
	#s=s.decode('utf-8')
	#return re.sub(ur'[\u4e00-\u9fff]+','',s)
	return  ''.join(re.findall(r"\d+",s))
def caculate_distance2(s1,s2):
	lcs = find_lcseque(s1,s2)
	return len(s1)-len(lcs)

#s1 correct, s2 predict
def caculate_distance(s1,s2):
	len_s2=len(s2)
	len_s1=len(s1)
	dis=0
	i=0
	for c in s1:
		if i<len_s2  and c!=s2[i]: dis+=1
		i+=1
	return dis+abs(len_s2-len_s1)

def get_list(path):
	return [os.path.join(path,f) for f in os.listdir(path)  if f.endswith('.jpg')]

def usage():
	print 'Usage:'
	print 'python %s image_folder_dir api_host[localhost:8080 or 10.39.66.115:8288]' % os.path.basename(sys.argv[0])
	sys.exit(1)


def collect_test_data(base_dir):
	global test_map,img_list
	for dir_name in test_dir_list:
		#collect test result map
		with open(base_dir+"/"+dir_name+"/mark.txt") as f:
			for l in f.readlines():
				l_array=l.strip().split(",")
				test_map[l_array[0]]={'invoice_code':l_array[1],'invoice_number':l_array[2],'invoice_date':strip_chinese(l_array[3]),'pretax_amount':l_array[4]}
			print "%s/mark.txt collect %d result sets" % (dir_name,len(test_map))
		#prepare test set
		img_list+=get_list(base_dir+"/"+dir_name+"/")
		print "%s/ increment collect %d test sets" % (dir_name,len(img_list))


if len(sys.argv)<3:
	usage()

base_dir=sys.argv[1].rstrip("/")
host=sys.argv[2]

collect_test_data(base_dir)

for imagename in img_list:

	payload = [('image_file',('my.jpeg',open(imagename,'rb'),'image/jpeg',))]
	# payload = {'image_file':open(imagename,'rb')}

	t1=time.time()
	try:
		# r = requests.post('http://10.39.66.115:8288/ocr/invoice_4/', files=payload,proxies=None)
		r = requests.post('http://%s/ocr/invoice_4/' % host, files=payload,proxies=None)
		
		try:
			j=json.loads(r.text)['result']
			#print j
		except Exception as  e:
			print "ocr failed"
			#识别失败，所有的正确数据放到准确率计算的分母上
			j['invoice_code1']=j['invoice_number1']=j['invoice_date']=j['pretax_amount']=''
			j['perf']=0

		correct=test_map[imagename.split("/")[-1]]
		
		d1=caculate_distance2(correct['invoice_code'],j['invoice_code1'])
		d2=caculate_distance2(correct['invoice_number'],j['invoice_number1'])
		d3=caculate_distance2(correct['invoice_date'],strip_chinese(j['invoice_date']))
		d4=caculate_distance2(correct['pretax_amount'],j['pretax_amount'])
		text_len=len(correct['invoice_code'])+len(correct['invoice_number'])+len(correct['invoice_date'])+len(correct['pretax_amount'])
		distance=d1+d2+d3+d4
		
		total_len+=text_len
		total_dis+=distance

		# print correct['invoice_code'],correct['invoice_number'],correct['invoice_date'],correct['pretax_amount']
		print imagename.split("/")[-1],j['invoice_code1'],j['invoice_number1'],strip_chinese(j['invoice_date']),j['pretax_amount'],j['perf'],"acc:%.2f%%" % ((1-(float(distance)/float(text_len)))*100),"total_len:%d total_dis:%d" % (total_len,total_dis)
		
	except Exception as e:
		print("exception: "+str(e))	
		traceback.print_exc(file=sys.stdout)

	
print "total mean acc:%.2f%%" % ((1-(float(total_dis)/float(total_len)))*100)