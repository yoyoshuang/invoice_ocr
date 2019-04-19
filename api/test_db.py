from util.config import *
from util.recdao import get_record_id
from util.recdao import update_r,getconn




def creat_r():
	r={"id":"","imagename":"","local":"","local_box":"","invoice_code1":"","invoice_code2":"","invoice_number1":"","invoice_number2":"","invoice_date":"","pretax_amount":"","msg":"","ip":"","reqtime":"","perf1":"","perf2":"","perf3":""}
	
	return r



if __name__ == "__main__":
	r = creat_r()
	#c= getconn()
	print( MYSQL_HOST)
	for i in range(2):
		r['id'] = get_record_id()
		# print(r['id'])
		# pass

		r['imagename'] = 'test'+str(i)
		r['local'] = 'aaa'+str(i)
		r['msg'] = 'haoshuang test'+str(i)
		r['perf1'] = 11000
		update_r(r)

