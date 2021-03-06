# -*- coding: utf-8 -*-
import api.pokelocator_api as api
import datetime
import time
import os
import sys
import math
import traceback
import requests
import pickle
import ast
import commands
import json
import push
from config import *

# ### CONFIG LOOKS LIKE
# creds = {
#         "PTC_USERNAME": ...,
#         "PTC_PASSWORD": ...,
#         "GOOG_USERNAME": ...,
#         "GOOG_PASSWORD": ...,
# }
# emails = {}
# emails["nick"] = ...
# emails["seth"] = ...
# emails["sicheng"] = ...
# emails["gabriel"] = ...
# who = "nick" # or "sicheng" or "seth"
# ### 

hour = datetime.datetime.now().hour + 1.0*datetime.datetime.now().minute/60

email_history = set()
email_history_fname = "history.pkl"
def have_emailed(unique_tuple):
    global email_history
    if not email_history and os.path.isfile(email_history_fname):
        try:
            with open(email_history_fname, "r") as fhist_in:
                email_history = pickle.load(fhist_in)
        except: pass
    return unique_tuple in email_history
def save_email_history():
    with open(email_history_fname, "w") as fhist_out:
        pickle.dump(email_history,fhist_out)
def add_to_email_history(unique_tuple):
    global email_history
    email_history.add(unique_tuple)


def get_unique_tuple(person, num, lat, lng, ts, life):
    return (str(person), int(num), round(float(lat),5),round(float(lng),5),int(ts-(900-float(life)))/100)

def mail(s,b,to):
    print "mailing %s to %s" % (s, to)
    with open("temp.txt", "w") as fhtemp:
        fhtemp.write(b)
    # os.system("cat temp.txt | mail -s \"%s\" %s" % (s, to))
    os.system("""mail -s "$(echo "%s\nContent-Type: text/html")"  %s  <  temp.txt""" % (s, to))

poke_id_map = {}
def pokemon_id_to_name(pid):
    if not poke_id_map:
        with open("api/pokemon.json","r") as fmapin:
            data = ast.literal_eval(fmapin.read())
            for poke in data:
                poke_id_map[int(poke["Number"])] = poke["Name"].replace(" ","")
    return poke_id_map.get(pid, "Unknown")

def get_json(url):
    data = {}
    try:
        stat, out = commands.getstatusoutput("curl -s \"%s\" --max-time 10" % url)
        data = json.loads(out)
    except: print "ERROR fetching json from %s" % url
    return data

def distance(p1, p2):
    lat1, long1 = p1
    lat2, long2 = p2
    radiusEarth = 3956.547 # miles
    milesPerDegLat = math.pi*radiusEarth/180.0
    milesPerDegLong = 2.0*math.pi*radiusEarth*math.cos(lat1*math.pi/180.0)/360.0
    dx = abs(long2-long1)*milesPerDegLong
    dy = abs(lat2-lat1)*milesPerDegLat
    return math.sqrt(dx**2 + dy**2)

def where_is_nick():
    hour = datetime.datetime.now().hour + 1.0*datetime.datetime.now().minute/60
    if 9 < hour < 18: return 34.4140608,-119.8429348 # broida
    else: return 34.4181543,-119.8549256 # san clem

def is_walkable(p1,hour,lifetime_mins):
    return lifetime_mins - 1 >= distance(where_is_nick(), p1) / (3.9) * 60.0

def is_bikeable(dest,lifetime_mins):
    orig = where_is_nick()
    data = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={lat1},{lng1}&destinations={lat2},{lng2}&mode=bicycling&key=AIzaSyBG-WFho0CVYtcuzWaRhNJBoT8DZ884IZI".format(lat1=orig[0],lng1=orig[1],lat2=dest[0],lng2=dest[1])).json()

    dur_mins = int(math.ceil(data["rows"][0]["elements"][0]["duration"]["value"]/60.0))

    return lifetime_mins - 2.0 >= dur_mins

def fetch_ours(coords):
    print "### FETCHING OURS ###"
    new_pokelocs = []
    for lat,lng in coords:
        try:
            new_pokelocs.extend( api.main(lat=lat, lng=lng, creds=creds) )
        except:
            print "SERVER ERROR, so skipping this location"
    return new_pokelocs

def fetch_local():
    print "### FETCHING LOCAL POKEVISION ###"
    new_pokelocs = []
    stat,lines = commands.getstatusoutput("tail -n 650 fromlocal.txt")
    if stat == 0:
        for line in lines.splitlines():
            line = line.title()
            line = line.replace("♀","F")
            line = line.replace("♂","M")
            new_pokelocs.append(line)
    return new_pokelocs

def fetch_skiplagged():
    print "### FETCHING SKIPLAGGED ###"
    # STEAL MORE POKEMON FROM skiplagged.com/api/pokemon.php!!!
    new_pokelocs = []
    slag_json = requests.get("https://skiplagged.com/api/pokemon.php?bounds=34.407904,-119.864899,34.41911,-119.828807").json()
    for poke in slag_json["pokemons"]:
        pokeloc = "%i,%i,%s,%s,%s,%i" % (int(time.time()), poke["pokemon_id"], poke["pokemon_name"].replace(" ",""), str(poke["latitude"]), str(poke["longitude"]), poke["expires"]-int(time.time()))
        new_pokelocs.append(pokeloc)
    return new_pokelocs

def fetch_pokevision(lat,lng):
    # STEAL MORE POKEMON FROM pokevision.com!!!
    print "### FETCHING POKEVISION ###"
    new_pokelocs = []
    pvjob_json = get_json("https://pokevision.com/map/scan/%s/%s" % (str(lat),str(lng)))
    if pvjob_json["status"] == "success":
        jobId = pvjob_json["jobId"]
        time.sleep(7)
        pv_json = get_json("https://pokevision.com/map/data/%s/%s/%s" % (str(lat),str(lng),jobId))
        if "pokemon" in pv_json:
            for poke in pv_json["pokemon"]:
                pokeloc = "%i,%i,%s,%s,%s,%i" % (int(time.time()), int(poke["pokemonId"]), pokemon_id_to_name(int(poke["pokemonId"])), str(poke["latitude"]), str(poke["longitude"]), int(poke["expiration_time"])-int(time.time()))
                new_pokelocs.append(pokeloc)
        else:
            print "### WARNING! ### Pokevision is taking it's sweet time to scan. Even after 7 seconds, we didn't get anything. Ignoring for this round."
    else:
        print "### WARNING! ### Pokevision is rate-limiting us right now"
    return new_pokelocs



pokelocs = []
print "TIME: ", datetime.datetime.now()

scan_iv_1 = False
scan_iv_2 = False
scan_broida = False # Can turn on if we are at the office still

if 7 < hour < 18:
    scan_broida = True
# elif (hour < 1 or 18 < hour):
elif (hour <= 7 or 18 < hour): # FIXME
    if who == "nick":
        scan_iv_1 = True
    else:
        scan_iv_2 = True
else:
    print "Sleep time!"
    sys.exit()

coords = []
if scan_broida:
    coords += [
            (34.41416,  -119.84296), # broida
            (34.41230,  -119.84659), # south of broida
            (34.41638,  -119.84642), # campbell
            (34.40946,  -119.85603), # dp close to campus
            # (34.41225,  -119.85530), # freebirds
            # (34.41516,  -119.85521), # north embarcadero del norte
        ]
if scan_iv_1:
    coords += [
            (34.40946,  -119.85603), # dp close to campus
            (34.41225,  -119.85530), # freebirds
            (34.41024,  -119.86169),
            (34.40985,  -119.86534),
            (34.41257,  -119.85886),
    ]
if scan_iv_2:
    coords += [
            (34.41516,  -119.85521), # north embarcadero del norte
            (34.40981,  -119.85886),
            (34.41526,  -119.86023),
            # (34.41250,  -119.86114),
            # (34.41282,  -119.86538),
    ]



# pokelocs.extend( fetch_pokevision(34.41420320229702,-119.85021829605101) )
# pokelocs.extend( fetch_ours(coords) )
pokelocs.extend( fetch_local() )
# pokelocs.extend( fetch_skiplagged() )
# pokelocs.extend( fetch_pokevision(34.412574601595,-119.8613977432251) )



unseen = {}
unseen["nick"] = {130,131,132,5,40,6,137,139,2,142,143,144,145,146,148,149,150,151,31,34,36,45,9,68,71,76,83,87,89,94,3,115,122,134}
unseen["sicheng"] = {6,9,68,71,83,91,94,110,115,122,130,131,132,143,144,145,146,148,149,150,151}
unseen["seth"] = {59,3,6,9,62,76,80,83,103,115,122,130,131,132,134,143,144,145,146,147,148,149,150,151}
# unseen["gabriel"] = {2,3,5,6,9,12,15,30,31,34,36,40,45,51,59,61,65,68,70,71,76,83,91,94,105,108,110,113,114,115,122,130,131,132,134,135,139,141,142,143,144,145,146,148,149,150,151}

# don't write common pokemon to the .js file
apply_screening = True
screening_list = {"Pidgey", "Rattata", "Zubat", "Paras", "Spearow", "Voltorb", "Caterpie", "Weedle", "Ekans", "Meowth", "Venonat", "Rhyhorn", "Tentacool"}

suffix = "_1" if who == "nick" else "_2"
unique_lat_lng = set()
with open("pokemon.js", "w") as fhout:
    fhout.write("last_updated%s = \"%s\";\n" % (suffix, datetime.datetime.now()))
    fhout.write("last_updated_ts%s = %i;\n" % (suffix, int(time.time())))
    fhout.write("POKEMON%s = [\n" % suffix)
    for pokeloc in pokelocs:
        ts,num,name,lat,lng,life = pokeloc.split(",")
        name = name.replace(" ","")
        lat_goog = int(float(lat)*1e6)
        lng_goog = int(float(lng)*1e6)
        num = int(num)
        life = float(life)
        ts = int(ts)

        # skip entirely if the pokemon is more than 7 miles away
        if distance(where_is_nick(), (float(lat),float(lng))) > 7.0: continue

        # or if the pokemon has an unphysical lifetime
        if not (0 <= life <= 900): continue

        
        # skip if this is a duplicate pokemon at same lat, lng
        if (num,lat_goog,lng_goog) in unique_lat_lng: continue
        unique_lat_lng.add( (num,lat_goog,lng_goog) )

        # needed for log file
        print pokeloc

        if apply_screening:
            skipping = False
            for blah in screening_list:
                if name == blah:
                    # print name, "is found, but not bother showing it on the map."
                    skipping = True
            if skipping:
                continue
        fhout.write("{ name:\"%s\", lat:%i, lng:%i, num:%i, life:%i, ts:%i },\n" % (name, lat_goog, lng_goog, num, life, ts))

        minsleft = int(life/60)


        # HANDLE UNSEEN
        b = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head><title></title>
</head>
<body>


        Found a {name} with {life} mins remaining at https://www.google.com/maps/dir//{lat},{lng}/@{lat},{lng},16z
        <br>
        Link to custom map: http://uaf-6.t2.ucsd.edu/~namin/dump/pgo/map.html
        <br>

<img src='https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom=14&size=500x300&markers=color:blue|label:test|{lat},{lng}&key=AIzaSyBPiQcAKq_WjVnZaFHHxRSZR_C8gMkaVWI' />
        

</body>
</html>
        """.format(name=name, life=minsleft, lat=str(lat), lng=str(lng))

        for person in unseen.keys():
            if num not in unseen[person]: continue
            if minsleft < 2: continue 

            unique_tuple =  get_unique_tuple(person, num, lat, lng, ts, life)
            if have_emailed(unique_tuple): continue

            extra = ""
            # this function makes a google maps API call, so we only want to do this if we are about to email
            if is_bikeable((float(lat),float(lng)),minsleft):
                extra += " [bikeable] "
            s = "[PGo]{extra}{name} - {life} mins left".format(extra=extra, name=name, life=minsleft)

            mail(s=s, b=b, to=emails[person])
            add_to_email_history(unique_tuple)

            # push notifications for nick
            if person == "nick" and num in {149,3,142}:
                push.send_push(name)

    fhout.write("];\n" )

os.system("scp pokemon.js uaf:~/public_html/dump/pgo/")

save_email_history()
