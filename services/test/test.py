#from log_service import *
import json


#call upload log 
f = open("log.json", "r")
tmp = json.load(f)

t = iter(tmp['log'])
for i in t:
    print(i['tid'])
    print(next(t, None))

f.close()
#upload_log(tmp)
#query_log('test5@gmail.com','2021-05-04')

#call check remain time
#call save schedule
# call query schedule 
