from data.db_session import db_auth
from typing import Optional
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from services.classes import User, Target, Equipments, Project, Schedule
from datetime import datetime, timedelta
from services.accounts_service import get_equipment_project_priority, update_equipment_project_priority

import astro.declination_limit_of_location as declination
import astro.astroplan_calculations as schedule
import astro.nighttime_calculations as night
import ephem
import random

graph = db_auth()

# get a project's information
def get_project_detail(PID: int):
    #get the project's detail
    query = "MATCH (n:project {PID: $PID})" \
    " return n.title as title, n.project_type as project_type, n.PI as PI, n.description as description, n.aperture_upper_limit as aperture_upper_limit, n.aperture_lower_limit as aperture_lower_limit," \
    "n.FoV_upper_limit as FoV_upper_limit, n.FoV_lower_limit as FoV_lower_limit, n.pixel_scale_upper_limit as pixel_scale_upper_limit, n.pixel_scale_lower_limit as pixel_scale_lower_limit," \
    "n.mount_type as mount_type, n.camera_type1 as camera_type1, n.camera_type2 as camera_type2, n.JohnsonB as JohnsonB, n.JohnsonR as JohnsonR, n.JohnsonV as JohnsonV, n.SDSSu as SDSSu," \
    "n.SDSSg as SDSSg, n.SDSSr as SDSSr, n.SDSSi as SDSSi, n.SDSSz as SDSSz, n.PID as PID"
    project = graph.run(query, PID = PID).data()
    return project

# this function will return project which user can join (equipment based)
def get_project(usr: str)->Optional[Project]:
    
    #get the information of user's equipment
    query = "MATCH (x:user {email:$usr})-[rel:UhaveE]->(e:equipments) " \
        " return e.EID as EID,e.mount_type as mount_type, e.camera_type1 as camera_type1, e.camera_type2 as camera_type2,e.JohnsonB as jb,e.JohnsonV as jv, e.JohnsonR as jr, e.SDSSu as su, e.SDSSg as sg, e.SDSSr as sr , e.SDSSi as si, e.SDSSz as sz"
    equipment = graph.run(query, usr = usr).data()

    #get all the currenet project in DB 
    query = "MATCH (n:project) return n.title as title, n.project_type as project_type, n.PI as PI, n.description as description, n.aperture_upper_limit as aperture_upper_limit, n.aperture_lower_limit as aperture_lower_limit," \
        "n.FoV_upper_limit as FoV_upper_limit, n.FoV_lower_limit as FoV_lower_limit, n.pixel_scale_upper_limit as pixel_scale_upper_limit, n.pixel_scale_lower_limit as pixel_scale_lower_limit," \
        "n.mount_type as mount_type, n.camera_type1 as camera_type1, n.camera_type2 as camera_type2, n.JohnsonB as JohnsonB, n.JohnsonR as JohnsonR, n.JohnsonV as JohnsonV, n.SDSSu as SDSSu," \
        "n.SDSSg as SDSSg, n.SDSSr as SDSSr, n.SDSSi as SDSSi, n.SDSSz as SDSSz, n.PID as PID order by PID" 
    project = graph.run(query).data()

    #get the project which user haved already join
    query = "match (x:user{email:$usr})-[r:Member_of]->(p:project) return p.PID as PID"
    joined = graph.run(query,usr =usr).data()
    pid_list = []
    for i in range(len(joined)):
        pid_list.append(joined[i]['PID'])
    
    #filter project
    result = []
    for i in range(len(equipment)):
        for j in range(len(project)):
            if project[j]['PID'] in result: continue
            if any(pid == project[j]['PID'] for pid in pid_list): continue
            if equipment[i]['jb'] == 'n':
                if project[j]['JohnsonB'] == 'y': continue
            if equipment[i]['jv'] == 'n':
                if project[j]['JohnsonV'] == 'y': continue
            if equipment[i]['jr'] == 'n':
                if project[j]['JohnsonR'] == 'y': continue
            if equipment[i]['su'] == 'n':
                if project[j]['SDSSu'] == 'y': continue
            if equipment[i]['sg'] == 'n':
                if project[j]['SDSSg'] == 'y': continue
            if equipment[i]['sr'] == 'n':
                if project[j]['SDSSr'] == 'y': continue
            if equipment[i]['si'] == 'n':
                if project[j]['SDSSi'] == 'y': continue
            if equipment[i]['sz'] == 'n':
                if project[j]['SDSSz'] == 'y': continue
            if equipment[i]['mount_type'] != project[j]['mount_type']: continue
            if equipment[i]['camera_type1'] != project[j]['camera_type1']: continue
            if equipment[i]['camera_type2'] != project[j]['camera_type2']: continue
            # print(project[j])
            n = graph.run("MATCH (x:user{email: $usr}) return x.name as manager_name",usr = usr).data()
            project[j]['manager_name'] = n[0]['manager_name']
            result.append(project[j]) 

    result = get_project_filter(usr, result)

    return result

# return all the interest targets of a user
def get_user_interest(usr: str):
    query = "match (x:user{email:$usr})-[r:ULikeT]->(t) return t.name as name, t.TID as TID"
    interest = graph.run(query, usr=usr).data()

    return interest

# choose the project with user's interested targets (interest based)
def get_project_filter(usr: str, project_list: list):
    random.shuffle(project_list)
    interest = get_user_interest(usr)

    chosen_project = []

    find = 0
    for project in project_list:
        find = 0
        project_target = get_project_target(project['PID'])
        for t in project_target:
            for i in interest:
                if i['TID'] == t['TID']:
                    chosen_project.append(project)
                    find = 1
                    break
            if len(chosen_project) > 10 or find == 1:
                break
        if len(chosen_project) > 10 or find == 1:
            break

    plen = len(project_list)
    if plen < 10:
        goal = plen
    else:
        goal = 10

    # if the total of chosen projects is less than 10 or goal, random append projects to the list
    exist = 0
    if len(chosen_project) < goal:
        for i in range(goal-len(chosen_project)):
            while True:
                exist = 0
                rand_index = random.randint(0, plen-1)
                rand_pid = project_list[rand_index]['PID']
                for chosen in chosen_project:
                    if chosen['PID'] == rand_pid:
                        exist = 1
                        break
                if exist == 0:
                    break
            chosen_project.append(project_list[rand_index])

    return chosen_project

# 0331 rank joined projects
def get_project_default_priority(projects):
    ranked_projects = sorted(projects, key=lambda k:k['project_type'], reverse=True)

    return ranked_projects

# 0331 get user the priority of users' projects
def get_project_orderby_priority(usr):
    query = "MATCH (x:user {email:$usr}) return x.project_priority"
    pid_list = graph.run(query, usr=usr).data()
    
    ori_project_priority = []
    for pid in pid_list:
        query = "MATCH (p:project {PID:$pid}) return p"
        ori_project_priority += graph.run(query, pid=pid).data()

    return ori_project_priority

# 0331 update the priority of users' projects
def upadte_project_priority(usr, pid_list):
    query = "MATCH (x:user {email:$usr}) set x.project_priority=$project_priority"
    graph.run(query, usr=usr, project_priority=pid_list)

#get a project observe target
def get_project_target(pid: int):
    # consider to delete the targets that have reached the goal of observe time

    query = "MATCH x=(p:project{PID:$pid})-[r:PHaveT]->(t:target) RETURN t.name as name, t.latitude as lat, t.longitude as lon, t.TID as TID"
    project_target = graph.run(query, pid=pid).data()

    return project_target

#get a project equipment's target list
def get_project_equipment_TargetList(pid: int, eid: int):
    # consider to delete the targets that have reached the goal of observe time

    query = "MATCH x=(p:project{PID:$pid})-[r:PHaveE]->(e:Equipment{EID:$eid}) RETURN r.target_list as target_list"
    project_target = graph.run(query, pid=pid, eid=eid).data()

    return project_target[0]['target_list']

#create a new project
def create_project(usr: str,title: str,project_type: str,description: str,aperture_upper_limit: float,aperture_lower_limit: float,FoV_upper_limit: float,
        FoV_lower_limit: float,pixel_scale_upper_limit: float,pixel_scale_lower_limit: float,mount_type: str,camera_type1: str,camera_type2: str,JohnsonB: str,
        JohnsonR: str,JohnsonV: str,SDSSu: str,SDSSg: str,SDSSr: str,SDSSi: str,SDSSz: str)->Optional[Project]:
    #this function will create a project  
    count = graph.run("MATCH (p:project) return p.PID  order by p.PID DESC limit 1 ").data()
    project = Project()
    if len(count) == 0:
        project.PID = 0
    else:
        project.PID = count[0]['p.PID']+1
    project.title = title
    project.project_type = project_type
    tmp = graph.run("MATCH (x:user {email: $usr})  return x.UID", usr = usr).data()
    project.PI = tmp[0]['x.UID']
    project.description = description
    project.aperture_upper_limit = aperture_upper_limit
    project.aperture_lower_limit = aperture_lower_limit
    project.FoV_upper_limit = FoV_upper_limit
    project.FoV_lower_limit = FoV_lower_limit
    project.pixel_scale_upper_limit = pixel_scale_upper_limit
    project.pixel_scale_lower_limit = pixel_scale_lower_limit
    project.mount_type = mount_type
    project.camera_type1 = camera_type1
    project.camera_type2 = camera_type2
    project.JohnsonB = JohnsonB
    project.JohnsonR = JohnsonR
    project.JohnsonV = JohnsonV
    project.SDSSu = SDSSu
    project.SDSSg = SDSSg
    project.SDSSr = SDSSr
    project.SDSSi = SDSSi
    project.SDSSz = SDSSz
    graph.create(project)

    query= "MATCH (x:user {email: $usr}) MATCH (p:project {PID: $PID}) create (x)-[m:Manage {umanageid:$umanageid}]->(p)"
    count = graph.run("MATCH ()-[m:Manage]->() return m.umanageid  order by m.umanageid DESC limit 1 ").data()
    if len(count) == 0:
        cnt = 0
    else:
        cnt = count[0]['m.umanageid']+1
    graph.run(query, usr = usr, PID = project.PID,umanageid = cnt)
    return project

#update a project's information
def upadte_project(usr: str,PID: int,umanageid: int,title: str,project_type: str,description: str,aperture_upper_limit: float,aperture_lower_limit: float,FoV_upper_limit: float,
        FoV_lower_limit: float,pixel_scale_upper_limit: float,pixel_scale_lower_limit: float,mount_type: str,camera_type1: str,camera_type2: str,JohnsonB: str,
        JohnsonR: str,JohnsonV: str,SDSSu: str,SDSSg: str,SDSSr: str,SDSSi: str,SDSSz: str)->Optional[Project]:
    print(PID)
    print(umanageid)
    print(usr)
    query ="MATCH rel = (x:user)-[p:Manage {umanageid: $umanageid}]->(m:project) return rel"
    print(graph.run(query,usr = usr,umanageid = umanageid).data())
    query ="MATCH (x:user {email:$usr})-[p:Manage {umanageid: $umanageid}]->(m:project)" \
             f"SET m.title='{title}', m.project_type='{project_type}', m.description='{description}', m.aperture_upper_limit='{aperture_upper_limit}', m.aperture_lower_limit='{aperture_lower_limit}'," \
             f"m.FoV_upper_limit='{FoV_upper_limit}', m.FoV_lower_limit='{FoV_lower_limit}'," \
             f"m.pixel_scale_upper_limit='{pixel_scale_upper_limit}', m.pixel_scale_lower_limit='{pixel_scale_lower_limit}',"\
             f"m.mount_type='{mount_type}', m.camera_type1='{camera_type1}', m.camera_type2='{camera_type2}', m.JohnsonB='{JohnsonB}', m.JohnsonR='{JohnsonR}', m.JohnsonV='{JohnsonV}', " \
             f"m.SDSSu='{SDSSu}', m.SDSSg='{SDSSg}', m.SDSSr='{SDSSr}', m.SDSSi='{SDSSi}', m.SDSSz='{SDSSz}'"  
    project = graph.run(query,usr = usr, umanageid = umanageid)
    return project   

#delete a project
def delete_project(usr: str, PID: int, umanageid: int):
    graph.run("MATCH (x:user {email:$usr})-[m:Manage {umanageid: $umanageid}]->(p:project) DELETE m,p", usr=usr, umanageid = umanageid)

#get the project's manager
def get_project_manager_name(PID: int):
    query = "MATCH (p:project {PID: $PID}) return p.PI as PI"
    result = graph.run(query,PID = PID).data()
    query = "MATCH (x:user {UID: $UID}) return x.name as name, x.affiliation as affiliation, x.title as title"
    manager_name = graph.run(query, UID = result[0]['PI']).data()
    return manager_name

#add a new project manager for a project
def add_project_manager(usr: str, PID: int):
    query= "MATCH (x:user {email: $usr}) MATCH (p:project {PID: $PID}) create (x)-[m:Manage {umanageid:$umanageid}]->(p)"
    count = graph.run("MATCH ()-[m:Manage]->() return m.umanageid  order by m.umanageid DESC limit 1 ").data()
    if len(count) == 0:
        cnt = 0
    else:
        cnt = count[0]['m.umanageid']+1
    graph.run(query, usr = usr, PID = PID,umanageid = cnt)
    return

#get the project list of a project manager
def user_manage_projects_get(usr: str):
    # return the project user manage 
    query="MATCH (x:user {email:$usr})-[m:Manage]->(p:project) return m.umanageid as umanageid, p.title as title, p.project_type as project_type," \
         "p.PI as PI, p.description as description, p.aperture_upper_limit as aperture_upper_limit, p.aperture_lower_limit as aperture_lower_limit," \
        "p.FoV_upper_limit as FoV_upper_limit, p.FoV_lower_limit as FoV_lower_limit, p.pixel_scale_upper_limit as pixel_scale_upper_limit, p.pixel_scale_lower_limit as pixel_scale_lower_limit," \
        "p.mount_type as mount_type, p.camera_type1 as camera_type1, p.camera_type2 as camera_type2, p.JohnsonB as JohnsonB, p.JohnsonR as JohnsonR, p.JohnsonV as JohnsonV, p.SDSSu as SDSSu," \
        "p.SDSSg as SDSSg, p.SDSSr as SDSSr, p.SDSSi as SDSSi, p.SDSSz as SDSSz, p.PID as PID "
    project = graph.run(query,usr = usr)
    return project

#add a new target for project
def create_project_target(usr: str, PID: int, TID: int, JohnsonB: str, JohnsonR: str, JohnsonV: str,SDSSu: str,SDSSg: str,SDSSr: str,SDSSi: str,SDSSz: str, time2observe: dict):
    query="MATCH (p:project {PID: $PID}) MATCH (t:target {TID:$TID}) create (p)-[pht:PHaveT {phavetid:$phavetid, JohnsonB:$JohnsonB, JohnsonV:$JohnsonV, JohnsonR:$JohnsonR, SDSSu:$SDSSu, SDSSg:$SDSSg, SDSSr:$SDSSr, SDSSi:$SDSSi, SDSSz:$SDSSz, Time_to_Observe:$time2observe}]->(t) return pht.phavetid"
    update_project_equipment_observe_list(usr,PID,TID,JohnsonB, JohnsonR, JohnsonV,SDSSu,SDSSg,SDSSr,SDSSi,SDSSz)
    count = graph.run("MATCH ()-[pht:PHaveT]->() return pht.phavetid  order by pht.phavetid DESC limit 1 ").data()
    if len(count) == 0:
        cnt = 0
    else:
        cnt = count[0]['pht.phavetid']+1
    result = graph.run(query, PID = PID, TID = TID, phavetid = cnt, JohnsonB = JohnsonB, JohnsonR = JohnsonR, JohnsonV = JohnsonV, SDSSg = SDSSg, SDSSi = SDSSi, SDSSr = SDSSr, SDSSu = SDSSu, SDSSz = SDSSz, Time_to_Observe= time2observe).data()
    return result

#
def get_qualified_equipment(usr: str, PID: int):
    query_eid = "MATCH (x:user{email:$usr})-[r:UhaveE]->(e:equipments) RETURN e.EID as EID, e.JohnsonB as jb,e.JohnsonV as jv, e.JohnsonR as jr, e.SDSSu as su, e.SDSSg as sg, e.SDSSr as sr , e.SDSSi as si, e.SDSSz as sz, r.declination_limit as declination"
    equipment = graph.run(query_eid, usr=usr).data()
    project_target = graph.run("MATCH (p:project {PID: $PID})-[pht:PHaveT]->(t:target) " \
        " return pht.JohnsonB as JohnsonB, pht.JohnsonV as JohnsonV, pht.JohnsonR as JohnsonR, pht.SDSSu as SDSSu, pht.SDSSg as SDSSg, pht.SDSSr as SDSSr , pht.SDSSi as SDSSi, pht.SDSSz as SDSSz"
    ", t.TID as TID, t.name as name, t.latitude as dec", PID=PID).data()
    
    qualified_eid_list = dict()
    for i in range(len(equipment)):
        for j in range(len(project_target)):
            if equipment[i]['jb'] == 'n':
                if project_target[j]['JohnsonB'] == 'y': continue
            if equipment[i]['jv'] == 'n':
                if project_target[j]['JohnsonV'] == 'y': continue
            if equipment[i]['jr'] == 'n':
                if project_target[j]['JohnsonR'] == 'y': continue
            if equipment[i]['su'] == 'n':
                if project_target[j]['SDSSu'] == 'y': continue
            if equipment[i]['sg'] == 'n':
                if project_target[j]['SDSSg'] == 'y': continue
            if equipment[i]['sr'] == 'n':
                if project_target[j]['SDSSr'] == 'y': continue
            if equipment[i]['si'] == 'n':
                if project_target[j]['SDSSi'] == 'y': continue
            if equipment[i]['sz'] == 'n':
                if project_target[j]['SDSSz'] == 'y': continue
            # filter with equipment declination limit
            if float(equipment[i]['declination']) <= 0 and float(project_target[j]['dec']) < float(equipment[i]['declination']):
                continue
            if float(equipment[i]['declination']) > 0 and float(project_target[j]['dec']) > float(equipment[i]['declination']):
                continue

            qualified_eid_list.append({'EID':int(equipment[i]['EID']), 'declination':float(equipment[i]['declination'])})
            break

    return qualified_eid_list

#this function is uesd for test, the user will auto join the project
def auto_join(usr: str, PID: int):
    # create user-project relationship
    query = "MATCH (x:user {email:$usr}) MATCH (p:project {PID:$PID})  create (x)-[:Member_of {memberofid: $memberofid, join_time: $join_time}]->(p)"
    time = graph.run("return datetime() as time").data() 
    count = graph.run("MATCH ()-[rel:Memberof]->() return rel.memberofid  order by rel.memberofid DESC limit 1 ").data()
    time = graph.run("return datetime() as time").data() 
    if len(count) == 0:
        cnt = 0
    else:
        cnt = count[0]['rel.memberofid']+1
    graph.run(query, usr = usr, PID = PID, memberofid = cnt, join_time = time[0]['time'])
    # create equipment-project relationship
    qualified_eid_list = get_qualified_equipment(usr, PID)
    query = "MATCH (p:project {PID:$PID}) MATCH (e:equipments {EID:$EID}) CREATE (p)-[rel:PhaveE {phaveeid:$phaveeid, target_list:$target_list, declination_limit: $declination}]->(e)"
    for i in range(len(qualified_eid_list)):
        count = graph.run("MATCH ()-[rel:PhaveE]->() return rel.phaveeid order by rel.phaveeid DESC limit 1").data()
        if len(count) == 0:
            cnt = 0
        else:
            cnt = count[0]['rel.phaveeid']+1
        target_list = initial_equipment_target_list(usr,qualified_eid_list[i]['EID'],PID)
        graph.run(query, PID=PID, EID=qualified_eid_list[i]['EID'], phaveeid=cnt,declination = qualified_eid_list[i]['declination'], target_list = target_list )
        
        #add the project to the last in the prioritty list
        old_priority = get_equipment_project_priority(usr,int(qualified_eid_list[i]['EID']))
        if(old_priority == None):
            list = []
            list.append(PID)
            update_equipment_project_priority(usr,int(qualified_eid_list[i]['EID']))
        else:
            old_priority.append(PID)
            update_equipment_project_priority(usr,int(qualified_eid_list[i]['EID']))


#this function is uesd to test, the user will auto leave the project
def auto_leave(usr: str, PID: int):
    # delete user-project relationship
    query_user_bye = "MATCH (x:user {email:$usr})-[rel:Memberof]->(p:project{PID:$PID}) delete rel"
    graph.run(query_user_bye, usr=usr, PID=PID)

    # delete project-equipment relationship
    qualified_eid_list = get_qualified_equipment(usr, PID)
    query_equipment_bye = "MATCH (p:project {PID:$PID})-[rel:PhaveE]->(e:equipments{EID:$EID}) delete rel"
    
    for i in range(len(qualified_eid_list)):
        graph.run(query_equipment_bye, PID=PID, EID=qualified_eid_list[i])


def apply_project(usr: str,PID: int)->int:
    # this function will create an apply_to relationship to the project
    # return value
    # 1 : apply success

    query = "MATCH (x:user {email:$usr}) MATCH (p:project {PID:$PID})  create (x)-[:Apply_to {applyid: $applyid, status: $status, apply_time: $apply_time}]->(p)"
    time = graph.run("return datetime() as time").data() 
    count = graph.run("MATCH ()-[apply:Apply_to]->() return apply.applyid  order by apply.applyid DESC limit 1 ").data()
    if len(count) == 0:
        cnt = 0
    else:
        cnt = count[0]['apply.applyid']+1
    graph.run(query, usr = usr, PID = PID, applyid = cnt,status ='waiting', apply_time = time[0]['time'])
    return 1

def apply_project_status(usr: str, PID: int)->int:
    # this function will chechk whether user apply to the project or not 
    # 0 : error
    # 1 : no 
    # 2 : yes, waiting
    # 3 : yes, already join
    query = "MATCH (x:user {email:$usr})-[rel:Apply_to]->(p:project {PID:$PID}) return rel.status "
    result = graph.run(query, usr = usr, PID = PID).data()
    

    if len(result) == 0 or result[len(result)-1] == 'reject':
        return 1
    elif result[len(result)-1]['rel.status'] == 'accept':
        return 3
    elif result[len(result)-1]['rel.status'] == 'waiting':
        return 2
    else:
        return 0

def get_apply_waiting(usr: str):
    # this function will return the list of user's applied project which status is waiting
    query = "MATCH (x:user {email:$usr})-[:Apply_to {status: $status}]->(p:project) return p.PID as PID"
    waitiing_list = graph.run(query, usr = usr, status = 'waiting').data()
    return waitiing_list

def get_apply_history(usr: str):
     #this function will return the apply history of an user 
    query = "MATCH (x:user {email:$usr})-[rel:Apply_to]->(p:project) return p.PID as PID, rel.status as status, p.title as title, rel.apply_time as time"
    apply_history = graph.run(query, usr = usr).data()
    print(apply_history)
    return apply_history

def get_want_to_join_project(usr: str, PID : int):
    # project manage can get ther list of who want to join his project
    query = "MATCH (x:user)-[rel:Apply_to {status: $status}]->(p:project {PID: $PID}) return x.name as name, rel.applyid as applyid, rel.time as time "
    apply_list = graph.run(query, status = 'waiting', PID = PID).data()
    return apply_list

def reject_join_project(usr: str, PID: int, UID: int, applyid: int):
    # reject user'apply
    # 1 : success, 0: error
    query = "MATCH (x:user {email: $UID})-[rel:Apply_to {applyid: $applyid}]->(p:project {PID: $PID}) SET rel.status = $status return  rel.status as status"
    result = graph.run(query, status = 'reject', PID = PID, UID = UID, applyid = applyid).data()
    if len(result) == 1  and result[0]['status'] == 'reject':
        return 1
    else:
        return 0

def accept_join_project(usr: str, PID: int, UID: int, applyid: int):
    # accept a user'apply
    query = "MATCH (x:user {email: $UID})-[rel:Apply_to {applyid: $applyid}]->(p:project {PID: $PID}) SET rel.status = $status return  rel.status as status"
    result = graph.run(query, status = 'accept', PID = PID, UID = UID, applyid = applyid).data()
    if len(result) == 1  and result[0]['status'] == 'accept':
        
        query = "CREATE (x:user {email: $UID})-[rel: Member_of {memberofid: $memberofid}]->(p:project {PID: $PID})"
        count = graph.run("MATCH ()-[rel:Memberof]->() return rel.memberofif  order by rel.memberofid DESC limit 1 ").data()
        if len(count) == 0:
            cnt = 0
        else:
            cnt = count[0]['rel.memberofid']+1
        graph.run(query, UID = UID, PID =PID, memberofid = cnt)
        return 1
    else:
        return 0


def get_project_member(usr: str, PID: int):
    # return the user in this project
    query = "MATCH (x:user)-[rel:Member_of]->(p:project {PID: $PID}) return  x.name as name"
    member = graph.run(query, PID =PID).data()
    return member

def get_project_equipment(PID: int):
    # return the equipments in this project
    query = "MATCH (p:project {PID:$PID})-[rel:PhaveE]->(e:equipments) return e.EID as eid,"\
        "e.aperture as aperture, e.Fov as Fov, e.pixel_scale as pixel_scale, e.tracking_accuracy as accuracy, e.lim_magnitude as lim_magnitude, e.elevation_lim as elevation_lim,"\
        "e.mount_type as mount_type, e.camera_type1 as camera_type1, e.camera_type2 as camera_type2, e.JohnsonB as JohnsonB, e.JohnsonR as JohnsonR, e.JohnsonV as JohnsonV, e.SDSSu as SDSSu,"\
        "e.SDSSg as SDSSg, e.SDSSr as SDSSr, e.SDSSi as SDSSi,e.SDSSz as SDSSz, rel.declination as declination"
    eq_list = graph.run(query, PID =PID).data()
    return eq_list

def get_project_join(usr: str):
    #get all the project user have already joined
    query = "MATCH (x:user {email:$usr})-[rel:Member_of]->(p:project) return p.title as title, p.project_type as project_type, p.PI as PI, p.description as description, p.aperture_upper_limit as aperture_upper_limit, p.aperture_lower_limit as aperture_lower_limit," \
        "p.FoV_upper_limit as FoV_upper_limit, p.FoV_lower_limit as FoV_lower_limit, p.pixel_scale_upper_limit as pixel_scale_upper_limit, p.pixel_scale_lower_limit as pixel_scale_lower_limit," \
        "p.mount_type as mount_type, p.camera_type1 as camera_type1, p.camera_type2 as camera_type2, p.JohnsonB as JohnsonB, p.JohnsonR as JohnsonR, p.JohnsonV as JohnsonV, p.SDSSu as SDSSu," \
        "p.SDSSg as SDSSg, p.SDSSr as SDSSr, p.SDSSi as SDSSi, p.SDSSz as SDSSz, p.PID as PID order by PID"
    join_list = graph.run(query, usr = usr).data()
    return  join_list

#return the project based on user's equipment 
def get_project_join_filter(projectlist: list,usr: str,uhaveid: int):
  
    equipment = graph.run("MATCH (x:user{email: $usr})-[:UhaveE{uhaveid:$uhaveid}]->(e:equipments) " \
        " return e.EID as EID,e.JohnsonB as jb,e.JohnsonV as jv, e.JohnsonR as jr, e.SDSSu as su, e.SDSSg as sg, e.SDSSr as sr , e.SDSSi as si, e.SDSSz as sz" \
        ",e.mount_type as mount_type, e.camera_type1 as camera_type1, e.camera_type2 as camera_type2" ,usr = usr , uhaveid = uhaveid).data()
    
    result = []
    for j in range(len(projectlist)):
        if projectlist[j]['PID'] in result: continue

        p = get_project_detail(projectlist[j]['PID'])

        if equipment[0]['jb'] == 'n':
            if p[0]['JohnsonB'] == 'y': continue
        if equipment[0]['jv'] == 'n':
            if p[0]['JohnsonV'] == 'y': continue
        if equipment[0]['jr'] == 'n':
            if p[0]['JohnsonR'] == 'y': continue
        if equipment[0]['su'] == 'n':
            if p[0]['SDSSu'] == 'y': continue
        if equipment[0]['sg'] == 'n':
            if p[0]['SDSSg'] == 'y': continue
        if equipment[0]['sr'] == 'n':
            if p[0]['SDSSr'] == 'y': continue
        if equipment[0]['si'] == 'n':
            if p[0]['SDSSi'] == 'y': continue
        if equipment[0]['sz'] == 'n':
            if p[0]['SDSSz'] == 'y': continue
        if equipment[0]['mount_type'] != p[0]['mount_type']: continue
        if equipment[0]['camera_type1'] != p[0]['camera_type1']: continue
        if equipment[0]['camera_type2'] != p[0]['camera_type2']: continue
        result.append(projectlist[j])

    return result

def fliter_project_target(usr: str, PID: int):
    #return the target based on user's equipment 
    query = "MATCH (x:user {email:$usr})-[rel:UhaveE]->(e:equipments)" \
        " return e.EID as EID,e.mount_type as mount_type, e.camera_type1 as camera_type1, e.camera_type2 as camera_type2,e.JohnsonB as jb,e.JohnsonV as jv, e.JohnsonR as jr, e.SDSSu as su, e.SDSSg as sg, e.SDSSr as sr , e.SDSSi as si, e.SDSSz as sz, rel.declination_limit as declination"
    equipment = graph.run(query, usr = usr).data()
    #query = "MATCH (x:user {email:$usr})-[rel:UhaveE]->(e:equipments), (n:project {PID: $PID}) where n.mount_type=e.mount_type and n.camera_type1=e.camera_type1 and n.camera_type2=e.camera_type2 " \
    #   "and n.JohnsonB=e.JohnsonB and n.JohnsonV=e.JohnsonV and n.JohnsonR=e.JohnsonR  and n.SDSSu=e.SDSSu  and n.SDSSg=e.SDSSg and n.SDSSr=e.SDSSr and n.SDSSi=e.SDSSi and n.SDSSz=e.SDSSz" \
    #    " return e.EID as EID,e.JohnsonB as jb,e.JohnsonV as jv, e.JohnsonR as jr, e.SDSSu as su, e.SDSSg as sg, e.SDSSr as sr , e.SDSSi as si, e.SDSSz as sz"
    #equipment = graph.run(query, usr = usr, PID = PID).data()
    project_target = graph.run("MATCH (p:project {PID: $PID})-[pht:PHaveT]->(t:target) " \
        " return pht.JohnsonB as JohnsonB, pht.JohnsonV as JohnsonV, pht.JohnsonR as JohnsonR, pht.SDSSu as SDSSu, pht.SDSSg as SDSSg, pht.SDSSr as SDSSr , pht.SDSSi as SDSSi, pht.SDSSz as SDSSz"
    ", t.TID as TID, t.name as name, t.latitude as lat, t.longitude as lon", PID = PID).data()
    print(len(equipment))
    print(len(project_target))
    target = []
    # filter with equipment capability
    for i in range(len(equipment)):
        for j in range(len(project_target)):
            if any(d['TID'] == project_target[j]['TID'] for d in target): continue
            if equipment[i]['jb'] == 'n':
                if project_target[j]['JohnsonB'] == 'y': continue
            if equipment[i]['jv'] == 'n':
                if project_target[j]['JohnsonV'] == 'y': continue
            if equipment[i]['jr'] == 'n':
                if project_target[j]['JohnsonR'] == 'y': continue
            if equipment[i]['su'] == 'n':
                if project_target[j]['SDSSu'] == 'y': continue
            if equipment[i]['sg'] == 'n':
                if project_target[j]['SDSSg'] == 'y': continue
            if equipment[i]['sr'] == 'n':
                if project_target[j]['SDSSr'] == 'y': continue
            if equipment[i]['si'] == 'n':
                if project_target[j]['SDSSi'] == 'y': continue
            if equipment[i]['sz'] == 'n':
                if project_target[j]['SDSSz'] == 'y': continue
            # filter with equipment declination limit
            if float(equipment[i]['declination']) <= 0 and float(project_target[j]['lat']) < float(equipment[i]['declination']):
                continue
            if float(equipment[i]['declination']) > 0 and float(project_target[j]['lat']) > float(equipment[i]['declination']):
                continue

            target.append(project_target[j])
    print(len(target))

    return target

#Update a equipment target list when add new target to project
def update_project_equipment_observe_list(usr: str, PID: int, TID: int, JohnsonB: str, JohnsonR: str, JohnsonV: str,SDSSu: str,SDSSg: str,SDSSr: str,SDSSi: str,SDSSz: str):

    target_lat = graph.run("MATCH(t:target{TID:$TID}) return t.latitude as lat", TID = TID).data()
    
    eq_list = get_project_equipment(PID)
    if count(eq_list) == 0:
        return 0
    else :
        for i in range(len(eq_list)):
            if eq_list[i]['JohnsonB'] == 'n':
                if project_target[j]['JohnsonB'] == 'y': continue
            if eq_list[i]['JohnsonV'] == 'n':
                if project_target[j]['JohnsonV'] == 'y': continue
            if eq_list[i]['JohnsonR'] == 'n':
                if project_target[j]['JohnsonR'] == 'y': continue
            if eq_list[i]['SDSSu'] == 'n':
                if project_target[j]['SDSSu'] == 'y': continue
            if eq_list[i]['SDSSg'] == 'n':
                if project_target[j]['SDSSg'] == 'y': continue
            if eq_list[i]['SDSSr'] == 'n':
                if project_target[j]['SDSSr'] == 'y': continue
            if eq_list[i]['SDSsi'] == 'n':
                if project_target[j]['SDSSi'] == 'y': continue
            if eq_list[i]['SDSSz'] == 'n':
                if project_target[j]['SDSSz'] == 'y': continue

            # filter with equipment declination limit
            if float(eq_list[i]['declination']) <= 0 and float( target_lat[0]['lat']) < float(eq_list[i]['declination']):
                continue
            if float(eq_list[i]['declination']) > 0 and float( target_lat[0]['lat']) > float(eq_list[i]['declination']):
                continue
            
            query = "MATCH (p:project {PID: $PID})-[rel:PHaveE]->(e:equipment{EID:$EID}) return rel.target_list as list"
            target_list = graph.run(query).data()
            target_list.append(TID)
            query = "MATCH (p:project {PID: $PID})-[rel:PHaveE]->(e:equipment{EID:$EID}) set rel.target_list={target_list:$target_list} "
            graph.run(query, PID = PID, EID = eq_list[i]['eid'], target_list = target_list)

#initial a equipment target list when create project_equipment relationship
def initial_equipment_target_list(usr: str, EID: int, PID: int):
            
    project_target = graph.run("MATCH (p:project {PID: $PID})-[pht:PHaveT]->(t:target) " \
        " return pht.JohnsonB as JohnsonB, pht.JohnsonV as JohnsonV, pht.JohnsonR as JohnsonR, pht.SDSSu as SDSSu, pht.SDSSg as SDSSg, pht.SDSSr as SDSSr , pht.SDSSi as SDSSi, pht.SDSSz as SDSSz"
    ", t.TID as TID, t.name as name, t.latitude as lat, t.longitude as lon", PID = PID).data()

    query_eid = "MATCH (x:user{email:$usr})-[r:UhaveE]->(e:equipments{EID:$EID}) RETURN e.EID as EID, e.JohnsonB as jb,e.JohnsonV as jv, e.JohnsonR as jr, e.SDSSu as su, e.SDSSg as sg, e.SDSSr as sr , e.SDSSi as si, e.SDSSz as sz, r.declination_limit as declination"
    equipment = graph.run(query_eid, usr=usr,EID=EID).data()

    target = list()
    for j in range(len(project_target)):
        if equipment[0]['jb'] == 'n':
            if project_target[j]['JohnsonB'] == 'y': continue
        if equipment[0]['jv'] == 'n':
            if project_target[j]['JohnsonV'] == 'y': continue
        if equipment[0]['jr'] == 'n':
            if project_target[j]['JohnsonR'] == 'y': continue
        if equipment[0]['su'] == 'n':
            if project_target[j]['SDSSu'] == 'y': continue
        if equipment[0]['sg'] == 'n':
            if project_target[j]['SDSSg'] == 'y': continue
        if equipment[0]['sr'] == 'n':
            if project_target[j]['SDSSr'] == 'y': continue
        if equipment[0]['si'] == 'n':
            if project_target[j]['SDSSi'] == 'y': continue
        if equipment[0]['sz'] == 'n':
            if project_target[j]['SDSSz'] == 'y': continue
        # filter with equipment declination limit
        if float(equipment[0]['declination']) <= 0 and float(project_target[j]['lat']) < float(equipment[0]['declination']):
            continue
        if float(equipment[0]['declination']) > 0 and float(project_target[j]['lat']) > float(equipment[0]['declination']):
            continue

        target.append(int(project_target[j]['TID']))
    
    return target

