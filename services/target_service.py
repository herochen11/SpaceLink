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

#return all the target in the DB, this version limit the number to 100 
def get_target():
    # this function will return all target
    query = "MATCH(t:target) return t.name as name order by t.TID limit 100"
    # "MATCH(t:target) where t.tid>100 return t.name as name order by t.TID limit 100"
    target = graph.run(query)
    return target

#get a target's information
def get_targetDetails(targetName: str):
    query = "MATCH(t:target{name:$name}) return t.longitude as ra, t.latitude as dec, t.TID as TID"

    targetDetails = graph.run(query, name=targetName).data()
    return targetDetails

#search a target by keyword
def search_target(text: str):
    query= "MATCH (t:target) where t.name =~ $text return t.name as name order by t.name "
    target = graph.run(query, text = text).data()
    return target