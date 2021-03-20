from data.db_session import db_auth
from typing import Optional
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from services.classes import User, Target, Equipments, Project, Schedule
from datetime import datetime, timedelta

import astro.declination_limit_of_location as declination
import astro.astroplan_calculations as schedule
import astro.nighttime_calculations as night
import ephem
import random

graph = db_auth()

#add a new friend relationship for a user
def add_friend(usr: str, f_UID: int):
    query1 = "match (x:user{email:$usr}) match (f:user{UID:$UID}) create (x)-[r:Friend{FID:$FID}]->(f)"
    query2 = "match (x:user{UID:$UID}) match (f:user{email:$usr}) create (x)-[r:Friend{FID:$FID}]->(f)"
    count = graph.run("MATCH (x:user)-[r:Friend]->(f:user) return r.FID as FID order by FID DESC limit 1").data()
    if len(count) == 0:
        cnt = 0
    else:
        cnt = count[0]['FID']+1
    
    graph.run(query1, usr=usr, UID=f_UID, FID=cnt)
    graph.run(query2, UID=f_UID, usr=usr, FID=cnt+1)

#view all the friend relationship  of a user
def view_friend(usr: str):
    query = "MATCH (x:user{email:$usr})-[r:Friend]->(f:user) return f.affiliation as affiliation, f.country as country, f.email as email, f.name as name, f.title as title, f.username as username"
    friend = graph.run(query, usr=usr).data()

    return friend

#delete a friend relationship for a user
def delete_friend(usr: str, f_UID: int):
    query1 = "MATCH (x:user{email:$usr})-[r:Friend]->(f:user{UID:$UID}) delete r"
    query2 = "MATCH (x:user{UID:$UID})-[r:Friend]->(f:user{email:$usr}) delete r"

    graph.run(query1, usr=usr, UID=f_UID)
    graph.run(query2, UID=f_UID, usr=usr)

#check we are friend or not
def check_is_friend(usr: str, f_UID: int):
    query = "MATCH (x:user{email:$usr})-[r:Friend]->(f:user{UID:$UID}) RETURN count(r) as cnt"
    count = graph.run(query, usr=usr, UID=f_UID).data()

    if(count[0]['cnt']) == 0:
        return 0
    else:
        return 1

#recommand a friend based on interest target
def get_a_new_user(usr: str, TID: int):
    query = "MATCH (x:user)-[r:ULikeT]->(t:target{TID:$TID}) where x.email<>$usr RETURN x.UID as UID"
    uid_list = graph.run(query, TID=TID, usr=usr).data()
    random.shuffle(uid_list)
    for uid in uid_list:
        if check_is_friend(usr, uid['UID']) == 0:
            return uid['UID']

    return -1

#get a user's information, can be used to return a friend's information 
def get_user_info(uid_list: list):
    query = "match (x:user{UID:$UID}) return x.UID as UID, x.username as username, x.name as name, x.email as email, x.affiliation as affiliation, x.title as title, x.country as country"
    user_info = []
    for i in range(len(uid_list)):
        user = graph.run(query, UID=uid_list[i][0]).data()
        user_info.append(user[0])

    return user_info