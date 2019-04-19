# coding: utf-8

from flask import abort, redirect, url_for,Flask,jsonify, render_template,request
from logging import FileHandler,Formatter
from logging.handlers import RotatingFileHandler


import cffi  # requires "pip install cffi"
import time,traceback
import gencrop
import gencrop_DL
import numpy as np
from ctypes.util import find_library
from scipy.misc import imsave
from time import time,sleep,strftime,localtime
from util.recdao import * 
from util.pager import pager
import re

#logging
import logging
from logging import Formatter, FileHandler
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_object(__name__)
app.config['JSON_AS_ASCII'] = False  #解决年月日显示问题


#init logging

LOGGER = logging.getLogger('invoice')
file_handler = RotatingFileHandler('./logs/invoiceapp.log' ,maxBytes=10240000, backupCount=6)
handler = logging.StreamHandler()
file_handler.setFormatter(Formatter(
    '[%(asctime)s] [pid %(process)d] [%(levelname)s]: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
handler.setFormatter(Formatter(
    '[%(asctime)s] [pid %(process)d] [%(levelname)s]: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
LOGGER.addHandler(file_handler)
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.DEBUG)


# PATH_TO_LIBTESS = '/data1/vision_lab/tesseract-lstm/lib/libtesseract.so.4'
# PATH_TO_LIBTESS = '/usr/local/lib/libtesseract.4.dylib'
# PATH_TO_LIBTESS = '/home/tesseract-lstm/lib/libtesseract.so.4'


DEBUG = 1

ffi = cffi.FFI()
ffi.cdef("""
struct Pix;
typedef struct Pix PIX;
PIX * pixRead ( const char *filename );
char * getLeptonicaVersion (  );

typedef struct TessBaseAPI TessBaseAPI ;
typedef struct ETEXT_DESC ETEXT_DESC;
typedef int BOOL;

const char* TessVersion();
const char** TessBaseAPIGetLoadedLanguagesAsVector(TessBaseAPI* handle);
TessBaseAPI* TessBaseAPICreate();
void TessBaseAPIEnd(TessBaseAPI* handle);
void TessBaseAPIDelete(TessBaseAPI* handle);
void pixDestroy ( PIX **ppix );

int TessBaseAPIInit3(TessBaseAPI* handle, const char* datapath, const char* language);

void TessBaseAPISetImage2(TessBaseAPI* handle, struct Pix* pix);

int TessBaseAPIRecognize(TessBaseAPI* handle, ETEXT_DESC* monitor);

void TessBaseAPISetRectangle(TessBaseAPI* handle, int left, int top, int width, int height);

char* TessBaseAPIGetUTF8Text(TessBaseAPI* handle);
void  TessDeleteText(char* text);

BOOL  TessBaseAPIDetectOrientationScript(TessBaseAPI* handle, char** best_script_name, 
                                                            int* best_orientation_deg, float* script_confidence, 
                                                            float* orientation_confidence);
""")

libtess = ffi.dlopen(PATH_TO_LIBTESS)
from ctypes.util import find_library
liblept = ffi.dlopen(find_library('lept'))

tess_version=ffi.string(libtess.TessVersion())

lep_version=ffi.string(liblept.getLeptonicaVersion())
# dawg =libtess.GlobalDawgCache()

api = libtess.TessBaseAPICreate()

# lang='eng+chi_sim'

# t0=current_milli_time()
libtess.TessBaseAPIInit3(api, data_dir, lang)
# print( "init tess in %d ms " % (current_milli_time()-t0) )


loaded_langs = ffi.new('char **')
loaded_langs= libtess.TessBaseAPIGetLoadedLanguagesAsVector(api)

def get_invoice_name():
	# 获取发票图片名，用时间戳+随机数方式唯一标示图片
	timestr = strftime('%Y%m%d_%H%M%S',localtime(time()))
	timemark = timestr+'_'+'%03d'%(np.random.random_integers(1,100))
	return timemark

def creat_r():
	r={"id":"","imagename":"","local":"","local_box":"","invoice_code1":"","invoice_code2":"","invoice_number1":"","invoice_number2":"","invoice_date":"","pretax_amount":"","msg":"","ip":request.remote_addr,"reqtime":"","perf1":"","perf2":"","perf3":""}
	return r

@app.route("/invoice_ocr/list/")
def invoice_ocr_list_index():
	return redirect(url_for('invoice_ocr_list',now_page=1))

@app.route("/invoice_ocr/list/<int:now_page>")
def invoice_ocr_list(now_page):
	p=pager("/invoice_ocr/list/")
	p.set_now_page(now_page)
	total,result_list=get_records(p.get_from_num(),p.get_per_page())
	#print (total,len(result_list))
	p.set_total_result(total)
	
	return render_template('thumbnail_list.html',pager=p.get_page_nav(now_page),list=result_list,total=total)




@app.route('/invoice_ocr/doc/',methods=['GET'])
def invoice_doc():
	# return render_template('index.html',content=get_captcha_doc())
	return render_template('index.html')

@app.route('/ocr/invoice_4/',methods=['POST'])
def invoice_solver():
	global libtess
	flag_cropv2 = 0
	r = creat_r()
	# print type(r)
	_id=-1
	if request.method == 'POST':
		try:
			r['id'] = get_record_id() #init mysql record
			imgfile = request.files['image_file']
			picname = get_invoice_name()
			imgfile.save(LOCALIZE_IMG_PATH+'/'+picname+'.png')
			r['imagename'] = picname
			r['local'] = picname+'.png'	
		except Exception as e:
				r['msg']=str(e)
				update_r(r)
				LOGGER.error("1010: load image %s failed" % imgfile)
				LOGGER.error("msg:%s" % str(e))
				return jsonify(code=1010,message=str(e))
	t1=time()
	try:
		# imgio=Image.open('./invoice_cache/'+picname+'.png')
		imagename = LOCALIZE_IMG_PATH+'/'+picname+'.png'
		# print(imagename)
		# imagename = "./invoice_cache/20171117_155756_007.png"
		# t1=current_milli_time()
		pix = liblept.pixRead(imagename.encode())

		# print("pixRead :",(t2-t1)*1000.0)
			
		# print("pixRead in %d ms " % (current_milli_time()-t1)) 
		libtess.TessBaseAPISetImage2(api, pix)
		
		# print("TessBaseAPISetImage2 :",(t3-t2)*1000.0)
		t2=time()
		try:
			reco_list,imgout = gencrop.compute_crop(imagename)
		except Exception as e:
			flag_cropv2 = 1
		if flag_cropv2==1:
			reco_list,imgout = gencrop_DL.compute_crop(imagename)

		# reco_list,imgout = gencrop.compute_crop(imagename)
		# reco_list,imgout = gencrop2.compute_crop(imagename)
		t3=time()
		print("crop img :",(t3-t2)*1000.0)
		r['perf1'] = "%.2f ms" %((t3-t2)*1000.0)

		if DEBUG:
			imsave(LOCALIZE_IMG_PATH+'/box_'+picname+'.png',imgout)
			r['local_box'] = 'box_'+picname+'.png'	
	except Exception as e:
		# print r
		r['msg']=str(e)
		update_r(r)
		LOGGER.error("1020:  crop image failed")
		LOGGER.error("msg:%s" % str(e))
		traceback.print_exc(file=sys.stdout)
		
		return jsonify(code=1020,message=str(e),picname=picname)

		# print(" pic :",(t2-t1)*1000.0)
		# t2=current_milli_time()
		#ratio=3.715
	
	try:
		t4 = time()	
		ratio=1
		results = []
		for rec in reco_list:
			p1=rec[0]
			p2=rec[1]
			left=int(p1[0]/ratio)
			top=int(p1[1]/ratio)
			width=int(p2[0]/ratio-left)
			height=int(p2[1]/ratio-top)

			libtess.TessBaseAPISetRectangle(api,left,top,width,height)
			text=ffi.new('char **')
			text=libtess.TessBaseAPIGetUTF8Text(api)
			# print(ffi.string(text).strip())
			results.append(ffi.string(text).strip())

		# print( "4 elem reco in  %d ms " % (current_milli_time()-t2))
		t5=time()
		print("4 elem reco :",(t5-t4)*1000.0)
		r['perf2'] = "%.2f ms" %((t5-t4)*1000.0)


		# libtess.TessDeleteText(text)
		# libtess.TessBaseAPIEnd(api);
		# libtess.TessBaseAPIDelete(api);
		
	except Exception as e:
		LOGGER.error("1021:  tesseract recognize failed")
		LOGGER.error("msg:%s" % str(e))

		print r
		r['msg']=str(e)
		update_r(r)
		
		return jsonify(code=1020,message=str(e),picname=picname)


	# 写入结果 code 发票代码 number 发票号码 date发票日期 pretax_amount 发票金额
	if len(results)==6:

		for k in range(6):
			results[k] = ''.join(results[k].split())
		for k in range(5):
			results[k]=filter(str.isdigit, results[k])
			
		results[5] =''.join( re.findall(r"[0-9\.]+",results[5]))

		year = results[4][0:4]+'年'
		month = results[4][4:6]+'月'
		day = results[4][6:8]+'日'

		results[4] =year+month+day		
		
		rout={}
		rout['invoice_code1']=results[0]
		rout['invoice_code2']=results[1]
		rout['invoice_number1']=results[2]
		rout['invoice_number2']=results[3]
		rout['invoice_date']=results[4]
		rout['pretax_amount']=results[5]
		rout['picname']=picname

		r['invoice_code1']=results[0]
		r['invoice_code2']=results[1]
		r['invoice_number1']=results[2]
		r['invoice_number2']=results[3]
		r['invoice_date']=results[4]
		r['pretax_amount']=results[5]


		# r['picname']=picname
		t6=time()
		'''performance'''
		perf= "%.2f ms" % ((t6-t1)*1000.0)
		rout['perf']=perf
		r['perf3'] = perf

		update_r(r)
		LOGGER.info("1000: perf:%s picname:%s  invoice_code1:%s invoice_code2:%s invoice_number1:%s invoice_number2:%s invoice_date:%s pretax_amount:%s" % (perf,picname,results[0],results[1],results[2],results[3],results[4],results[5]))
		return jsonify(retcode = '',retmsg = '',result = rout)
	else:
		r['msg']='results less than 6'
		update_r(r)
		LOGGER.error("1022:  results less than 6")
		LOGGER.error("msg:%s" % 'results less than 6')
		return jsonify(code=1021,message='results less than 6',picname=picname)
		
	return jsonify(code=1.0,message='20171117')


import sys

def ocr_int_handler(signal, frame):
	global libtess,api
	libtess.TessBaseAPIDelete(api)
	sys.exit(0)

def ocr_term_handler(signal, frame):
	global libtess,api
	libtess.TessBaseAPIDelete(api)
	sys.exit(0)


import signal
signal.signal(signal.SIGINT, ocr_int_handler)
signal.signal(signal.SIGTERM, ocr_term_handler)

if __name__ == "__main__":
	app.run()

#libtess.TessDeleteText(text)
#libtess.TessBaseAPIEnd(api)
#libtess.TessBaseAPIDelete(api)


