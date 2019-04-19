import os

BASE = os.path.dirname(os.path.realpath(__file__))
LOCALIZE_IMG_PATH=os.path.abspath(BASE+"/../static/img_dir/")


'''  db config '''
MYSQL_HOST='invoice_db'
MYSQL_DB='invoice_ocr'
MYSQL_USER='invoice'
MYSQL_PASSWORD='67ntgo8c'

#  for mac
if 'root' in os.environ.get('LOGNAME'):
	PATH_TO_LIBTESS = '/usr/local/lib/libtesseract.4.dylib'
	data_dir="/usr/local/share"
	lang='eng+chi_sim'
	DEBUG = 1

# for CentOS
if os.environ.get('HOSTNAME')=='invoice-production':
	data_dir="/data1/vision_lab/tesseract-lstm/share/tessdata/"
	PATH_TO_LIBTESS = '/data1/vision_lab/tesseract-lstm/lib/libtesseract.so.4'
	lang='eng+chi_sim'
	DEBUG = 0

# for ubuntu
if os.environ.get('LOGNAME')=='super':

	#data_dir="/home/tesseract-lstm/tessdata_fast/"
	data_dir="/home/tesseract-lstm/tessdata_hs/"
	PATH_TO_LIBTESS = '/home/tesseract-lstm/lib/libtesseract.so.4'
	lang='eng+chi_sim'
	DEBUG = 0
	
print "loading data_dir %s\nloading libtess_dir %s\nlang config:%s" % (data_dir,PATH_TO_LIBTESS,lang)
