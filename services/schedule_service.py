from data.db_session import db_auth
from typing import Optional
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from services.classes import User, Target, Equipments, Project, Schedule
from datetime import datetime, timedelta
from services.project_service import get_project_target

import astro.declination_limit_of_location as declination
import astro.astroplan_calculations as schedule
import astro.nighttime_calculations as night
import ephem
import random

graph = db_auth()

#create a new schedule for a equipment
def create_schedule(eid: int, uhaveid: int):
    # get EID
    # EID = get_eid(uhaveid)

    count = graph.run("MATCH (s:schedule) return s.SID order by s.SID DESC limit 1").data()
    schedule = Schedule()
    if len(count) == 0:
        schedule.SID = 0
    else:
        schedule.SID = count[0]['s.SID']+1
    
    # schedule.date #Y:M:D

    # get nighttime
    observe_section, current_time = get_night_time(uhaveid)

    schedule.observe_section = observe_section
    schedule.last_update = str(current_time)
    graph.create(schedule)
    print(eid)
    query="MATCH (e:equipments {EID: $EID}) MATCH (s:schedule {SID: $SID}) CREATE (e)-[r:EhaveS {ehavesid:$ehavesid}]->(s)"
    count = graph.run("MATCH ()-[r:EhaveS]->() return r.ehavesid  order by r.ehavesid DESC limit 1").data()
    if len(count) == 0:
        cnt = 0
    else:
        cnt = count[0]['r.ehavesid']+1

    graph.run(query, EID=eid, SID=schedule.SID, ehavesid=cnt)

    return schedule.SID

#load a equipmeent's schedule
def load_schedule(uhaveid: int):
    # find the equipment
    EID = get_eid(uhaveid)

    # if the equipment doesn't have a schedule, create one!
    query_count_schedule = "MATCH (e:equipments{EID:$EID})-[r:EhaveS]->(s:schedule) RETURN count(r) as cnt"
    result_count = graph.run(query_count_schedule, EID=EID).data()
    if result_count[0]['cnt'] == 0:
        SID = create_schedule(EID, uhaveid)
    else:
        query_sid = "match (e:equipments{EID:$EID})-[r:EhaveS]->(s:schedule) return s.SID as SID"
        sid = graph.run(query_sid, EID=EID).data()
        SID = sid[0]['SID']

    # get nighttime
    new_observe_section, current_time = get_night_time(uhaveid)

    # find the schedule
    query_schedule = "MATCH (e:equipments{EID:$EID})-[r:EhaveS]->(s:schedule) return s.observe_section as observe_section, s.last_update as last_update"
    result = graph.run(query_schedule, EID=EID).data()
    old_observe_section = result[0]['observe_section']
    previous_time = result[0]['last_update']

    # calculate the updated schedule
    updated_schedule = [-1]*24
    format = '%Y-%m-%d %H:%M:%S'
    gap = current_time - datetime.strptime(previous_time, format)
    if len(str(gap)) > 10:
        updated_schedule = new_observe_section
    else:
        start_index = int(str(gap).split(":")[0])
        j = start_index
        for i in range(24):
            if j < 24:
                updated_schedule[i] = old_observe_section[j]
                j+=1
            else:
                updated_schedule[i] = new_observe_section[i]

    # return the new calculated schedule to front-end
    return updated_schedule, str(current_time), SID

#this function save the schedule 
def save_schedule(SID: int, last_update: str, observe_section: list):
    query_save_schedule = "match (s:schedule{SID:$SID}) set s.last_update=$last_update, s.observe_section=$observe_section"

    graph.run(query_save_schedule, SID=SID, last_update=last_update, observe_section=observe_section)

# 0331 generate default schedule by sorting target
def generate_default_schedule(usr):
    query = "MATCH (x:user {email:$usr}) return x.project_priority"
    pid_list = graph.run(query, usr=usr).data()

    project_target = get_project_target(pid_list[0])
    sorted_target = sort_project_target(project_target)

    return sorted_target

# 0331 sort targets' priority
def sort_project_target(project_target):
    # sort algorithm
    '''TODO'''

    # shuffle for now
    return random.shuffle(project_target)

#get the equipment id
def get_eid(uhaveid):
    query_eid = "MATCH (x:user)-[h:UhaveE{uhaveid:$uhaveid}]->(e:equipments) return e.EID as EID"
    eid = graph.run(query_eid, uhaveid=uhaveid).data()

    eid = int(eid[0]['EID'])

    return eid

#get the observable time of all the targets in the target list
def get_observable_time(usr: str, uhaveid: int, tid_list: list):
    # hour array
    hour = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]

    # get current time for further calculation
    current_time = datetime.now().replace(microsecond=0, second=0, minute=0) + timedelta(hours=1)
    current_time_sec = str(current_time).split('.')[0]
    current_hour = current_time_sec.split(" ")[1].split(":")[0]

    # create current hour array
    index = hour.index(current_hour)
    current_hour_array = []
    for i in range(24):
        current_hour_array.append(hour[index])
        if index == 23:
            index = 0
        else:
            index += 1
    #print(current_hour_array)
    
    # get information from uhavee and equipment table
    query_relation = "MATCH (x:user)-[h:UhaveE{uhaveid:$uhaveid}]->(e:equipments) return h.longitude as longitude, h.latitude as latitude, h.altitude as altitude, e.elevation_lim as elevation_lim"
    eq_info = graph.run(query_relation, uhaveid=uhaveid).data()

    longitude = float(eq_info[0]['longitude'])
    latitude = float(eq_info[0]['latitude'])
    altitude = float(eq_info[0]['altitude'])
    elevation_lim = float(eq_info[0]['elevation_lim'])

    # get target information and run the ta's schedule function
    format = '%Y-%m-%d %H:%M:%S'
    # tid_list = [856, 266, 377, 488, 5, 100, 348, 7]
    
    target_data = []
    print(len(tid_list))
    for i in range(len(tid_list)):
        # create observation array
        observe = [0]*24

        query_target = "match (t:target) where t.TID=$tid return t.TID as TID, t.name as name, t.longitude as ra, t.latitude as dec"
        tar_info = graph.run(query_target, tid=tid_list[i]['TID']).data()

        tid = int(tar_info[0]['TID'])
        ra = float(tar_info[0]['ra'])
        dec = float(tar_info[0]['dec'])
        name = str(tar_info[0]['name'])

        t_start, t_end = schedule.run(uhaveid, longitude, latitude, altitude, elevation_lim, tid, ra, dec, current_time)
        print(tid)
        print('start observation: %s \nend observation %s' % (t_start, t_end))

        if str(t_start) != 'nan' and str(t_end)  != 'nan':
            t1 = str(t_start).split('.')[0].replace("T", " ")
            t2 = str(t_end).split('.')[0].replace("T", " ")

            time_left2start = datetime.strptime(t1, format) - datetime.strptime(current_time_sec, format)
            time_left2end = datetime.strptime(t2, format) - datetime.strptime(current_time_sec, format)
            # print('time left to start: ', time_left2start)
            # print('time_left to end:   ', time_left2end)

            o1 = int(str(time_left2start).split(":")[0])
            o2 = int(str(time_left2end).split(":")[0])+1
            for j in range(24):
                if j >= o1-1 and j < o2:
                    observe[j] = 1
            t_data = {'TID':tid_list[i]['TID'], 'name':name, 'start':t1.split(" ")[1], 'end':t2.split(" ")[1], 'time_section':observe, 'hour':current_hour_array}
        # else:
        #     observe = [0]*24
        #     t_data = {'TID':tid_list[i]['TID'], 'name':name, 'start':str(t_start), 'end':str(t_end), 'time_section':observe, 'hour':current_hour_array}

            target_data.append(t_data)
        # print(t_data)

    return target_data

#caluclate the night time based on user's time zone
def get_night_time(uhaveid):
    query_eq = "MATCH (x:user)-[r:UhaveE{uhaveid:$uhaveid}]->(e:equipments) RETURN r.longitude as longitude, r.latitude as latitude, r.altitude as altitude"
    eq_info = graph.run(query_eq, uhaveid=uhaveid).data()

    longitude = str(eq_info[0]['longitude'])
    latitude = str(eq_info[0]['latitude'])
    altitude = float(eq_info[0]['altitude'])

    try:
        observe_section, current_time = night.night(longitude, latitude, altitude)
    except ephem.NeverUpError:
        observe_section = [-1]*24
    except ephem.AlwaysUpError:
        observe_section = [-2]*24
    
    return observe_section, current_time