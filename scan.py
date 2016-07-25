import api.pokelocator_api as api
import datetime
import time
import os
import sys
import math
import traceback
import requests
from config import *

# ### CONFIG LOOKS LIKE
# creds = {
#         "PTC_USERNAME": ...,
#         "PTC_PASSWORD": ...,
#         "GOOG_USERNAME": ...,
#         "GOOG_PASSWORD": ...,
# }

# nick_email = ...
# seth_email = ...
# sicheng_email = ...
# gabriel_email = ...
# who = "nick" # or "sicheng" or "seth"
# ### 

hour = datetime.datetime.now().hour + 1.0*datetime.datetime.now().minute/60

def mail(s,b,to):
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


unseen_nick = {128,130,131,132,5,6,8,137,138,139,2,142,143,144,145,146,147,148,149,150,151,31,34,36,45,9,62,65,68,71,73,76,83,85,87,88,89,91,94,3,110,115,122}

unseen_sicheng = {2,3,5,6,8,9,15,28,31,36,40,45,62,65,68,71,76,83,85,87,89,91,94,110,113,114,115,121,122,130,131,132,134,135,136,139,141,142,143,144,145,146,147,148,149,150,151}

unseen_seth = {2,3,5,6,8,9,28,31,34,36,38,40,45,62,64,65,68,71,73,76,83,85,87,88,89,91,93,94,103,105,108,110,112,115,117,122,123,130,131,132,137,138,139,141,142,144,145,146,147,148,149,150,151}

unseen_gabriel = {2,3,5,6,8,9,28,31,34,36,38,40,45,62,64,65,68,71,73,76,83,85,87,88,89,91,93,94,103,105,108,110,112,115,117,122,123,130,131,132,137,138,139,141,142,144,145,146,147,148,149,150,151,114}

apply_screening = True
screening_list = {"Pidgey", "Rattata", "Zubat", "Paras", "Spearow", "Voltorb", "Magnemite", "Caterpie", "Weedle", "Ekans", "Meowth"}

mail_history = set()
suffix = "_1" if who == "nick" else "_2"
with open("pokemon.js", "w") as fhout:
    fhout.write("last_updated%s = \"%s\";\n" % (suffix, datetime.datetime.now()))
    fhout.write("last_updated_ts%s = %i;\n" % (suffix, int(time.time())))
    fhout.write("POKEMON%s = [\n" % suffix)
    for pokeloc in pokelocs:
        print pokeloc
        ts,num,name,lat,lng,life = pokeloc.split(",")
        name = name.replace(" ","")
        lat_goog = int(float(lat)*1e6)
        lng_goog = int(float(lng)*1e6)
        num = int(num)
        life = float(life)
        ts = int(ts)
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
        try:

            b = """
            Found a {name} with {life} mins remaining at https://www.google.com/maps/dir/{lat},{lng}/@{lat},{lng},16z
            Link to custom map: http://uaf-6.t2.ucsd.edu/~namin/dump/pgo/map.html
            """.format(name=name, life=minsleft, lat=str(lat), lng=str(lng))
            s = "[PGo] {name} - {life} mins left".format(name=name, life=minsleft)

            if num in unseen_gabriel and minsleft >= 3 and ("gabriel", str(lat)) not in mail_history:
                mail(s=s, b=b, to=gabriel_email)
                mail_history.add( ("gabriel", str(lat)) )
                
            if num in unseen_seth and minsleft >= 3 and ("seth", str(lat)) not in mail_history:
                mail(s=s, b=b, to=seth_email)
                mail_history.add( ("seth", str(lat)) )

            if num in unseen_sicheng and minsleft >= 3 and ("sicheng", str(lat)) not in mail_history:
                mail(s=s, b=b, to=sicheng_email)
                mail_history.add( ("sicheng", str(lat)) )

            if num in unseen_nick and minsleft > 3 and ("nick", str(lat)) not in mail_history:
                extra = ""
                if is_walkable((float(lat),float(lng)),hour,minsleft): extra = "[walk] "
                s = "[PGo] {extra}{name} - {life} mins left".format(extra=extra, name=name, life=minsleft)
                mail(s=s, b=b, to=nick_email)
                mail_history.add( ("nick", str(lat)) )

        except Exception, err:
            print "Exception!"

            traceback.print_exc()

    fhout.write("];\n" )

os.system("scp pokemon.js uaf:~/public_html/dump/pgo/")
