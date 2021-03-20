import ephem
import datetime

def night(longitude, latitude, altitude):
    # nighttime array, 0 for daytime and 1 for nighttime
    night = [-2]*24

    # round up current time
    current = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=1)
    a_day = datetime.timedelta(days=1)
    last_d = current-a_day

    # initialize equipment information
    equipment = ephem.Observer()
    equipment.lat = latitude
    equipment.lon = longitude
    equipment.elevation = altitude
    equipment.date = current

    sun = ephem.Sun()

    # calcultime sunrise and sunset from today
    n_rise = ephem.localtime(equipment.next_rising(sun))
    n_set = ephem.localtime(equipment.next_setting(sun))

    date_list = [n_rise, n_set]

    # calcultime sunrise and sunset from yesterday
    equipment.date = last_d
    n_rise = ephem.localtime(equipment.next_rising(sun))
    n_set = ephem.localtime(equipment.next_setting(sun))

    date_list.append(n_rise)
    date_list.append(n_set)
    date_list.append(current)
    # 1 for sunrise, 2 for sunset, 3 for current time
    mark = [1, 2, 1, 2, 3]
    zipped = zip(date_list, mark)
    sorted_list = sorted(zipped, key=lambda x: x[0])

    for i in range(len(sorted_list)):
        if sorted_list[i][1] == 3:
            if sorted_list[i+1][1] == 1:
                print("sun rise first")
                n1 = int(str(sorted_list[i+1][0]-current).split(':')[0])+1
                n2 = int(str(sorted_list[i+2][0]-current).split(':')[0])
                for j in range(24):
                    if j < n1 or j >= n2:
                        night[j] = -1
            else:
                print("sun set first")
                n1 = int(str(sorted_list[i+1][0]-current).split(':')[0])
                n2 = int(str(sorted_list[i+2][0]-current).split(':')[0])+1
                for j in range(24):
                    if j >= n1 and j < n2:
                        night[j] = -1
    
    return night, current