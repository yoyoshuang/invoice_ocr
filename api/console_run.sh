http_proxy=''
https_proxy=''
export http_proxy https_proxy


kill -9 `ps -ef | grep 'invoice_api:app' | grep -v 'grep' | awk -F ' ' '{print $2}'`
sleep 5
gunicorn invoice_api:app -k gevent -b 0.0.0.0:8080 -w 3 --timeout=120
