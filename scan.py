import api.pokelocator_api as api
import datetime
import time
import os
import sys
import math
import traceback
import requests
import pickle
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
    os.system("cat temp.txt | mail -s \"%s\" %s" % (s, to))

def distance(p1, p2):
    lat1, long1 = p1
    lat2, long2 = p2
    radiusEarth = 3956.547 # miles
    milesPerDegLat = math.pi*radiusEarth/180.0
    milesPerDegLong = 2.0*math.pi*radiusEarth*math.cos(lat1*math.pi/180.0)/360.0
    dx = abs(long2-long1)*milesPerDegLong
    dy = abs(lat2-lat1)*milesPerDegLat
    return math.sqrt(dx**2 + dy**2)

def where_is_nick(hour):
    if 9 < hour < 18: return 34.4140608,-119.8429348 # broida
    else: return 34.4181543,-119.8549256 # san clem

def is_walkable(p1,hour,lifetime_mins):
    return lifetime_mins - 1 >= distance(where_is_nick(hour), p1) / (3.9) * 60.0

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
        (34.413946, -119.8448427),  # BROIDA
        (34.4137253, -119.851935),  # THUNDERDOME
        (34.416255, -119.845971),   # Campbell
        (34.4147015, -119.841241),  # KITP
        (34.4121409, -119.8445374), # BREN
        (34.4126464, -119.8422689), # MARINE SCIENCE BLDG
        ]
if scan_iv_1:
    coords += [
        (34.4179524, -119.8547982), # San Clem
        (34.4150936, -119.855745),  # IV St. Mark's
        (34.4137792, -119.8541089), # IV Kappa Kappa Gamma
        (34.4132827, -119.8581308), # IV Blaze
        (34.4102330, -119.854927),  # IV Studio Plaza
        (34.4102500, -119.865666),  # IV DP Sea Lookout Park
    ]
if scan_iv_2:
    coords += [
        (34.4131220, -119.855372),  # IV Pardall
        (34.4167965, -119.8566609), # IV Tropicana Del Norte
        (34.4097480, -119.858685),  # IV Del Playa
        (34.4149920, -119.862408),  # IV Children's Park
        (34.4102330, -119.854927),  # IV Tiki House
    ]


for lat,lng in coords:
    try:
        pokelocs.extend( api.main(lat=lat, lng=lng, creds=creds) )
    except:
        print "SERVER ERROR, so skipping this location"

# STEAL MORE POKEMON FROM skiplagged.com/api/pokemon.php!!!
slag_json = requests.get("https://skiplagged.com/api/pokemon.php?bounds=34.407904,-119.864899,34.41911,-119.828807").json()
for poke in slag_json["pokemons"]:
    pokeloc = "%i,%i,%s,%s,%s,%i" % (int(time.time()), poke["pokemon_id"], poke["pokemon_name"].replace(" ",""), str(poke["latitude"]), str(poke["longitude"]), poke["expires"]-int(time.time()))
    pokelocs.append(pokeloc)



unseen = {}
unseen["nick"] = {130,131,132,5,6,8,137,138,139,2,142,143,144,145,146,147,148,149,150,151,31,34,36,45,9,62,65,68,71,76,83,85,87,88,89,91,94,3,115,122}
unseen["sicheng"] = {2,3,5,6,8,9,28,31,36,40,45,62,65,68,71,76,83,87,89,91,94,110,113,114,115,121,122,130,131,132,134,135,136,139,141,142,143,144,145,146,147,148,149,150,151}
unseen["seth"] = {2,3,6,8,9,31,34,36,40,45,62,65,68,71,76,83,87,88,89,91,94,103,105,110,115,122,130,131,132,137,138,139,142,144,145,146,148,149,150,151}
unseen["gabriel"] = {2,3,5,6,9,12,15,30,31,34,36,40,45,51,59,61,65,68,70,71,76,83,91,94,105,108,110,113,114,115,122,130,131,132,134,135,139,141,142,143,144,145,146,148,149,150,151}

apply_screening = True
screening_list = {"Pidgey", "Rattata", "Zubat", "Paras", "Spearow", "Voltorb", "Magnemite", "Caterpie", "Weedle", "Ekans", "Meowth"}

suffix = "_1" if who == "nick" else "_2"
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
        if distance(where_is_nick(hour), (float(lat),float(lng))) > 7.0: continue

        # or if the pokemon has an unphysical lifetime
        if not (0 <= life <= 900): continue

        # needed for log file
        print pokeloc
        
        if apply_screening:
            skipping = False
            for blah in screening_list:
                if name == blah:
                    print name, "is found, but not bother showing it on the map."
                    skipping = True
            if skipping:
                continue
        fhout.write("{ name:\"%s\", lat:%i, lng:%i, num:%i, life:%i, ts:%i },\n" % (name, lat_goog, lng_goog, num, life, ts))

        minsleft = int(life/60)

        # HANDLE UNSEEN
        b = """
        Found a {name} with {life} mins remaining at https://www.google.com/maps/dir/{lat},{lng}/@{lat},{lng},16z
        Link to custom map: http://uaf-6.t2.ucsd.edu/~namin/dump/pgo/map.html
        """.format(name=name, life=minsleft, lat=str(lat), lng=str(lng))
        s = "[PGo] {name} - {life} mins left".format(name=name, life=minsleft)

        for person in unseen.keys():
            if num not in unseen[person]: continue
            if minsleft < 3: continue 

            unique_tuple =  get_unique_tuple(person, num, lat, lng, ts, life)
            if have_emailed(unique_tuple): continue

            mail(s=s, b=b, to=emails[person])
            add_to_email_history(unique_tuple)

    fhout.write("];\n" )

os.system("scp pokemon.js uaf:~/public_html/dump/pgo/")

save_email_history()
