# coding: utf-8

import cffi  # requires "pip install cffi"
import time
import gencrop
import gencrop_DL
from util.config import * 
from ctypes.util import find_library

current_milli_time = lambda: int(round(time.time() * 1000))

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

BOOL  TessBaseAPIDetectOrientationScript(TessBaseAPI* handle, char** best_script_name, int* best_orientation_deg, float* script_confidence, 
	float* orientation_confidence);
""")

libtess = ffi.dlopen(PATH_TO_LIBTESS)
liblept = ffi.dlopen(find_library('lept'))
tess_version=ffi.string(libtess.TessVersion())
lep_version=ffi.string(liblept.getLeptonicaVersion())


api = libtess.TessBaseAPICreate()

t0=current_milli_time()
libtess.TessBaseAPIInit3(api, data_dir, lang)
print "init tess in %d ms " % (current_milli_time()-t0) 

loaded_langs = ffi.new('char **')
loaded_langs= libtess.TessBaseAPIGetLoadedLanguagesAsVector(api)
#loaded_langs)

picname = '../data/test_local/img/IMG_20170718_111304.jpg' #问题图
# picname = '../data/test_images/004.jpg' #正常图，确保修改问题图不影响正常图

t1=current_milli_time()
pix = liblept.pixRead(picname.encode())
print "pixRead in %d ms " % (current_milli_time()-t1) 


libtess.TessBaseAPISetImage2(api, pix)


# reco_list,imgout = gencrop.compute_crop(picname)	
reco_list,imgout = gencrop_DL.compute_crop(picname)	

t2=current_milli_time()
#ratio=3.715
ratio=1
for r in reco_list:
	p1=r[0]
	p2=r[1]
	left=int(p1[0]/ratio)
	top=int(p1[1]/ratio)
	width=int(p2[0]/ratio-left)
	height=int(p2[1]/ratio-top)

	libtess.TessBaseAPISetRectangle(api,left,top,width,height)
	text=ffi.new('char **')
	text=libtess.TessBaseAPIGetUTF8Text(api)
	print ffi.string(text).strip()

print "4 elem reco in  %d ms " % (current_milli_time()-t2)

libtess.TessDeleteText(text)
libtess.TessBaseAPIEnd(api);
libtess.TessBaseAPIDelete(api);

#def at /usr/local/include/leptonica/allheaders.h
#liblept.pixDestroy(pix);


'''
 【1100164320】

[(512.5594758064517, 83.109879032258505),(1164.1824596774193, 199.2036290322585)]


【45347190】

[(2729.5756048387102, 68.130040322581408), (3163.9909274193551, 187.96875000000045)]

【2017年04月20日】
[(3051.8331991458681, 315.28828718451359), (3534.3619911086216, 372.73219098960362)]

【¥428.30】
[(2593.344305221166, 1483.0319051719594), (2925.9489130625807, 1558.0121346853416)]

'''
