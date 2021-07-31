from services.classes import Target
from data.db_session import db_auth
from astroquery.simbad import Simbad
import webbrowser, json



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

#get a target's node
def get_targetNode(targetName: str):
    query = "MATCH(t:target{name:$name}) return t"

    targetNode = graph.run(query, name=targetName).data()
    return targetNode

#search a target by keyword
def search_target(text: str):
    query= "MATCH (t:target) where t.name =~ $text return t.name as name order by t.name "
    target = graph.run(query, text = text).data()
    print(target)
    return target

# add target in Simbad to target table
def query_from_simbad(targetName: str):
    limitedSimbad = Simbad()
    limitedSimbad.ROW_LIMIT = 5

    result_table = limitedSimbad.query_object(targetName)

    if result_table:
        ra = result_table[0][1]
        dec = result_table[0][2]

        ra_split = ra.split(" ")
        dec_split = dec.split(" ")

        len_ra = len(ra_split)
        len_dec = len(dec_split)

        # transfer the unit of ra/dec from hms/dms to degrees
        if len_ra == 1:
            ra_degree = float(ra_split[0]) * 15
        elif len_ra == 2:
            ra_degree = (float(ra_split[0]) + float(ra_split[1])/60) * 15
        else:
            ra_degree = (float(ra_split[0]) + float(ra_split[1])/60 + float(ra_split[2])/3600) * 15

        if len_dec == 1:
           dec_degree = float(dec_split[0])
        elif len_dec == 2:
            dec_degree = float(dec_split[0]) + float(dec_split[1])/60
        else:
            dec_degree = float(dec_split[0]) + float(dec_split[1])/60 + float(dec_split[2])/3600
            
        webbrowser.open("https://simbad.u-strasbg.fr/simbad/sim-basic?Ident=" + targetName + "&submit=SIMBAD+search")

        # check if the target exist in target table
        if(not get_targetDetails(targetName)):
            # create the target
            count = graph.run("MATCH (t:target) return t.TID  order by t.TID DESC limit 1 ").data()
            
            target = Target()
            if len(count) == 0:
                target.TID = 0
            else:
                target.TID = count[0]['t.TID']+1
            target.name = targetName
            target.longitude = ra_degree
            target.latitude = dec_degree
            graph.create(target)            
            print("NAME", target.name)

            return [{'name': target.name}]
        else:
            print("Target is already in the target table")
            return [{'name': targetName}]
    else:
        print("Target doesn't exist.")

    
