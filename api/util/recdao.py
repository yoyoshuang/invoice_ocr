import pymysql.cursors
from util.config import *

def getconn():
    c=pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor) 
    return c


# def record_suggestion(r):
#     global app
#     conn=getconn()
#     cursor=conn.cursor()
#     try:
#         # Create a new record
#         sql = "INSERT INTO img_record(src,local,local_box,bounding_boxes,suggestion,ratio,ip,reqtime,perf1,perf2,perf3) VALUES ( %s, %s,%s,%s,%s,%s,%s, now(),%s,%s,%s)"
#         #r['bounding_boxes']
#         cursor.execute(sql, (r['src'],r['local'],r['local_box'],r['bounding_boxes'],r['suggestion'],r['ratio'],r['ip'],r['perf1'],r['perf2'],r['perf3']))
#     except Exception as e:
#         app.logger.error( str(e))
#     finally:
#         cursor.close()
#         conn.commit()
#         conn.close()

def update_r(r):
    global app
    conn=getconn()
    cursor=conn.cursor()
    try:
        sql="update img_record set imagename=%s,local=%s,local_box=%s,invoice_code1=%s,invoice_code2=%s,invoice_number1=%s,invoice_number2=%s,invoice_date=%s,pretax_amount=%s,msg=%s,ip=%s,perf1=%s,perf2=%s,perf3=%s where id=%s"
        cursor.execute(sql, (r['imagename'],r['local'],r['local_box'],r['invoice_code1'],r['invoice_code2'],r['invoice_number1'],r['invoice_number2'],r['invoice_date'],r['pretax_amount'],r['msg'],r['ip'],r['perf1'],r['perf2'],r['perf3'],r['id']))
        r = cursor.fetchone()
    except Exception as e:
        app.logger.error( str(e))
        
    finally:
        cursor.close()
        conn.commit()
        conn.close()

def get_record_id():
    global app
    conn=getconn()
    cursor=conn.cursor()
    _id=-1
    try:
        # Read a single record
        sql="insert into img_record (imagename,local,local_box,invoice_code1,invoice_code2,invoice_number1,invoice_number2,invoice_date,pretax_amount,msg,ip,reqtime,perf1,perf2,perf3) values('','','','','','','','','','','',now(),'','','')"
        cursor.execute(sql, ())
        cursor.execute("SELECT  LAST_INSERT_ID() as id", ())
        r = cursor.fetchone()
        _id=r['id']
    except Exception as e:
        
        app.logger.error( str(e))
    finally:
        cursor.close()
        conn.commit()
        conn.close()
    
    return _id


def get_records(start,step):
    global app
    conn=getconn()
    cursor=conn.cursor()
    
    try:
        # Read a single record
        sql = "SELECT SQL_CALC_FOUND_ROWS  * FROM img_record order by reqtime desc  limit %s,%s"
        cursor.execute(sql, (int(start),int(step)))
        result = cursor.fetchall()

        cursor.execute("SELECT FOUND_ROWS() as total", ())
        r = cursor.fetchone()
    except Exception as e:
        app.logger.error( str(e))
        r={}
        r['total']=0
        result=[]
    finally:
        cursor.close()
        conn.close()
    return r['total'],result


'''
CREATE TABLE `img_record` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `src` varchar(255)  NOT NULL,
    `local` varchar(255)  NOT NULL,
    `bounding_boxes` varchar(255)  NOT NULL,
    `suggestion` varchar(255)  NOT NULL,
    `ratio` float(3,4)  NOT NULL default 1,
    `ip` char(16) not null default '',
    `reqtime` datetime not null,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
AUTO_INCREMENT=1 ;
'''