import psycopg2

def recommend_user_by_equipment(input:str):
    # Update connection string information
    host = "127.0.0.1"
    dbname = "postgis_lab"
    user = "postgres"
    password = "0000"
    sslmode = "disable"
    # Construct connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)

    cursor = conn.cursor()
    # cursor.execute("Select u2.uid From user_equipment u1, user_equipment u2 Where u1.uid = " + input + " and u1.uid != u2.uid and st_distance(u1.geog,u2.geog) < 300000;");
    cursor.execute("Select u2.uid, st_distance(u1.geog,u2.geog)/1000 as dis From user_equipment u1, user_equipment u2 Where u1.uid =" + input + "and u1.uid != u2.uid Order by dis asc Limit 100;");
    output = cursor.fetchall()

    # Clean up
    conn.commit()
    cursor.close()
    conn.close()
    return output
	
def postgres_create_user_equipments(uhave_id: int, uid: int, eid: int ,Longitude:float,Latitude:float,Altitude:float):
    # Update connection string information
    host = "127.0.0.1"
    dbname = "postgis_lab"
    user = "postgres"
    password = "0000"
    sslmode = "disable"
    # Construct connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)

    cursor = conn.cursor()
    cursor.execute("SELECT ST_GeomFromText('POINT(" + str(Longitude) + " " + str(Latitude) + ")', 4326);")
    temp = cursor.fetchall()
    geom = temp[0][0]
    cursor.execute("SELECT ST_GeogFromText('SRID=4326;POINT(" + str(Longitude) + " " + str(Latitude) + ")');")
    temp = cursor.fetchall()
    geog = temp[0][0]
    cursor.execute("INSERT INTO user_equipment (uhave_id, UID, EID, longitude, latitude, altitude, geom, geog) VALUES (" + str(uhave_id) + ", " + str(uid) + ", " + str(eid) + ", " + str(Longitude) + ", " + str(Latitude) + ", " + str(Altitude) + ", '" + geom + "', '" + geog + "');")
    # Clean up
    conn.commit()
    cursor.close()
    conn.close()
    return  

def postgres_delete_user_equipments(uhave_id: int):
    # Update connection string information
    host = "127.0.0.1"
    dbname = "postgis_lab"
    user = "postgres"
    password = "0000"
    sslmode = "disable"
    # Construct connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)

    cursor = conn.cursor()
    cursor.execute("Delete From user_equipment Where uhave_id = " + str(uhave_id) + " ;")

    # Clean up
    conn.commit()
    cursor.close()
    conn.close()
    return  

def postgres_output_user_equipment_kml(input: str):
    # Update connection string information
    host = "127.0.0.1"
    dbname = "postgis_lab"
    user = "postgres"
    password = "0000"
    sslmode = "disable"

    # Construct connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)
    print("Connection established")

    cursor = conn.cursor()
    output = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>" + "\n"
    output += "<kml xmlns=\"http://www.opengis.net/kml/2.2\">" + "\n"
    output += "<Document id=\"root_doc\">" + "\n"
    output += "<Schema name=\"equitment_location\" id=\"equitment_location\">" + "\n"
    output += "	<SimpleField name=\"_uid_\" type=\"float\"></SimpleField>" + "\n"
    output += "	<SimpleField name=\"uid\" type=\"float\"></SimpleField>" + "\n"
    output += "	<SimpleField name=\"eid\" type=\"float\"></SimpleField>" + "\n"
    output += "</Schema>" + "\n"
    output += "<Folder><name>equitment_location</name>" + "\n"

    count = 0
    cursor.execute("Select e.uhave_id, e.uid, e.eid, st_askml(e.geog) from user_equipment as e where uid = " + input + " ;")
    temp = cursor.fetchall()

    for i in temp:
	    output += "  <Placemark>" + "\n"
	    output += "	<ExtendedData><SchemaData schemaUrl=\"#equitment_location\">" + "\n"
	    output += "		<SimpleData name=\"_uid_\">" + str(count) + "</SimpleData>" + "\n"
	    output += "		<SimpleData name=\"uhave_id\">" + str(i[0]) + "</SimpleData>" + "\n"
	    output += "		<SimpleData name=\"uid\">" + str(i[1]) + "</SimpleData>" + "\n"
	    output += "		<SimpleData name=\"eid\">" + str(i[2]) + "</SimpleData>" + "\n"
	    output += "	</SchemaData></ExtendedData>" + "\n"
	    output += "      " + i[3] + "\n"
	    output += "  </Placemark>"
	    count = count + 1


    output += "</Folder>" + "\n"
    output += "</Document></kml>" + "\n"
#here
    file = open("user_equipment_location.kml",'w')
    file.write(output)
    file.close()
#here
    # Clean up
    conn.commit()
    cursor.close()
    conn.close()
    return

def postgres_output_project_equipment_kml(input: list):
    # Update connection string information
    host = "127.0.0.1"
    dbname = "postgis_lab"
    user = "postgres"
    password = "0000"
    sslmode = "disable"

    # Construct connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)
    print("Connection established")

    cursor = conn.cursor()
    output = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>" + "\n"
    output += "<kml xmlns=\"http://www.opengis.net/kml/2.2\">" + "\n"
    output += "<Document id=\"root_doc\">" + "\n"
    output += "<Schema name=\"equitment_location\" id=\"equitment_location\">"
    output += "	<SimpleField name=\"_uid_\" type=\"float\"></SimpleField>" + "\n"
    output += "	<SimpleField name=\"uid\" type=\"float\"></SimpleField>" + "\n"
    output += "	<SimpleField name=\"eid\" type=\"float\"></SimpleField>" + "\n"
    output += "</Schema>" + "\n"
    output += "<Folder><name>equitment_location</name>" + "\n"


    count = 0
    for j in input:
        cursor.execute("Select e.uhave_id, e.uid, e.eid, st_askml(e.geom) from user_equipment as e where uhave_id = " + j + " ;")
        temp = cursor.fetchall()
        for i in temp:
            output += "  <Placemark>" + "\n"
            output += "	<ExtendedData><SchemaData schemaUrl=\"#equitment_location\">" + "\n"
            output += "		<SimpleData name=\"_uid_\">" + str(count) + "</SimpleData>" + "\n"
            output += "		<SimpleData name=\"uhave_id\">" + str(i[0]) + "</SimpleData>" + "\n"
            output += "		<SimpleData name=\"uid\">" + str(i[1]) + "</SimpleData>" + "\n"
            output += "		<SimpleData name=\"eid\">" + str(i[2]) + "</SimpleData>" + "\n"
            output += "	</SchemaData></ExtendedData>" + "\n"
            output += "      " + i[3] + "\n"
            output += "  </Placemark>"
            count = count + 1

    output += "</Folder>" + "\n"
    output += "</Document></kml>" + "\n"

    file = open("project_equipment_location.kml",'w')
    file.write(output)
    file.close()

    # Clean up
    conn.commit()
    cursor.close()
    conn.close()
    return
#postgres_create_user_equipments(3003,0,1,123.1,20.1,200.0)
#postgres_delete_user_equipments(3002)
#postgres_output_user_equipment_kml("0")
#input = ["2","3"]
#postgres_output_project_equipment_kml(input)