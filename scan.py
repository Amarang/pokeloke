import api.pokelocator_api as api
import datetime
import time
import os
import sys
import traceback
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
# is_nick = False
# ###

hour = datetime.datetime.now().hour + 1.0*datetime.datetime.now().minute/60

def mail(s,b,to):
    with open("temp.txt", "w") as fhtemp:
        fhtemp.write(b)
    os.system("cat temp.txt | mail -s \"%s\" %s" % (s, to))

pokelocs = []

print "TIME: ", datetime.datetime.now()

scan_iv_1 = False
scan_iv_2 = False
scan_broida = False # Can turn on if we are at the office still

if 7 < hour < 18:
    scan_broida = True
elif (hour < 1 or 18 < hour):
    if is_nick:
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


unseen_nick = {2,3,5,6,8,9,15,31,34,36,38,40,45,49,62,65,68,71,73,75,76,78,80,83,85,87,88,89,91,93,94,95,103,110,112,114,115,117,119,122,123,128,130,131,132,137,138,139,140,142,143,144,145,146,147,148,149,150,151}

unseen_sicheng = {2,3,5,6,8,9,15,28,31,34,36,38,40,45,62,65,67,68,70,71,73,76,78,80,83,85,87,88,89,91,94,99,103,110,112,113,114,115,117,119,121,122,128,130,131,132,135,137,139,140,141,142,143,144,145,146,147,148,149,150,151}

unseen_seth = {2,3,5,6,7,8,9,15,26,28,31,34,36,38,40,45,49,61,62,64,65,68,71,73,76,80,83,85,87,88,89,91,93,94,95,98,99,103,105,108,110,112,113,115,117,119,121,122,123,125,126,128,130,131,132,134,135,137,138,139,140,141,142,143,144,145,146,148,149,150,151}-{98, 126, 113, 125, 57, 26, 30, 33, 75, 119, 7, 143}

mail_history = set()
suffix = "_1" if is_nick else "_2"
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
        fhout.write("{ name:\"%s\", lat:%i, lng:%i, num:%i, life:%i, ts:%i },\n" % (name, lat_goog, lng_goog, num, life, ts))

        minsleft = int(life/60)


        # HANDLE UNSEEN

        try:
            b = """
            Found a {name} with {life} mins remaining at https://www.google.com/maps/dir/{lat},{lng}/@{lat},{lng},16z
            Link to custom map: http://uaf-6.t2.ucsd.edu/~namin/dump/pgo/map.html
            """.format(name=name, life=minsleft, lat=str(lat), lng=str(lng))
            s = "[PGo] {name} - {life} mins left".format(name=name, life=minsleft)

            if num in unseen_nick and minsleft > 3 and ("nick", str(lat)) not in mail_history:
                mail(s=s, b=b, to=nick_email)
                mail_history.add( ("nick", str(lat)) )

            if num in unseen_seth and minsleft >= 3 and ("seth", str(lat)) not in mail_history:
                mail(s=s, b=b, to=seth_email)
                mail_history.add( ("seth", str(lat)) )

            if num in unseen_sicheng and minsleft >= 3 and ("sicheng", str(lat)) not in mail_history:
                mail(s=s, b=b, to=sicheng_email)
                mail_history.add( ("sicheng", str(lat)) )
        except Exception, err:
            print "Exception!"

            traceback.print_exc()


    fhout.write("];\n" )

os.system("scp pokemon.js uaf:~/public_html/dump/pgo/")
