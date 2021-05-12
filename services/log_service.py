from data.db_session import db_auth
import pymongo
from datetime import datetime
import json

graph = db_auth()
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["SpaceLink"]
observe_log = db['Observe_Log']
schedule_col = db['Schedule']

def upload_log(log:dict):
    observe_log.insert(log)
    for i in log["log"]:
        query1 = "match x=(p:project{PID:$pid})-[r:PHaveT]->(t:target{TID:$tid}) set r.Time_to_Observe={ramain:$remain} return r.Time_to_Observe" #update new time_to_observe
        query2 = "match x=(p:project{PID:$pid})-[r:PHaveT]->(t:target{TID:$tid}) return r.Time_to_Observe"  #query old time_to_observe
        dateformat = '%Y-%m-%d %H:%M:%S.%f'
        start = datetime.strptime(i['start_time'],dateformat)
        end = datetime.strptime(i['end_time'],dateformat)

        delta = end - start 
        observe_time = delta.seconds//60

        print("tid ", i['tid'], ", start time:", i['start_time'], ", end_time: ",i['end_time'])
        print("observe_time: ",delta, ",  ",observe_time)
        #TODO : here can optimize by preftching next item 
        remain_time = graph.run(query2,pid = int(i['pid']),tid = int(i['tid'])).data()
        remain_time[i['fliter_type']] = remain_time[i['fliter_type']] - observe_time
        graph.run(query1, pid = int(i['pid']),tid = int(i['tid']), remain = remain_time)
         
def query_log(user:str,date:str):
    for result in observe_log.find({'user_email':user, 'date': {'$regex': date, '$options': 'i'}}):
        print(result)

def save_schedule(schedule:str):
    schedule.insert(schedule)

def query_schedule(user:str,date:str):
    for result in schedule_col.find({'user_email':user, 'date': {'$regex': date, '$options': 'i'}}):
        print(result)

