
import math
import requests
from pprint import pprint
# crab_JetHT_Run2016B_v1
orig=34.4133825,-119.8410173
dest=34.409053,-119.860592





data = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={lat1},{lng1}&destinations={lat2},{lng2}&mode=bicycling&key=AIzaSyBG-WFho0CVYtcuzWaRhNJBoT8DZ884IZI".format(lat1=orig[0],lng1=orig[1],lat2=dest[0],lng2=dest[1])).json()

pprint(data)
dist = data["rows"][0]["elements"][0]["distance"]["text"]
dur_secs = int(math.ceil(data["rows"][0]["elements"][0]["duration"]["value"]/60.0))

print dist, dur_secs
# print data["ROWS"]
# import time
# import requests
# import ast
# import commands
# import json

# poke_id_map = {}
# def pokemon_id_to_name(pid):
#     if not poke_id_map:
#         with open("api/pokemon.json","r") as fmapin:
#             data = ast.literal_eval(fmapin.read())
#             for poke in data:
#                 poke_id_map[int(poke["Number"])] = poke["Name"].replace(" ","")
#     return poke_id_map.get(pid, "Unknown")

# def get_json(url):
#     data = {}
#     try:
#         stat, out = commands.getstatusoutput("curl -s \"%s\"" % url)
#         data = json.loads(out)
#     except: print "ERROR fetching json from %s" % url
#     return data

# # STEAL MORE POKEMON FROM pokevision.com!!!
# pokelocs = []
# pvjob_json = get_json("https://pokevision.com/map/scan/34.41305256378447/-119.8490595817566")
# print pvjob_json
# if pvjob_json["status"] == "success":
#     jobId = pvjob_json["jobId"]
#     pv_json = get_json("https://pokevision.com/map/data/34.41305256378447/-119.8490595817566/%s" % jobId)
#     print pv_json
#     for poke in pv_json["pokemon"]:
#         pokeloc = "%i,%i,%s,%s,%s,%i" % (int(time.time()), int(poke["pokemonId"]), pokemon_id_to_name(int(poke["pokemonId"])), str(poke["latitude"]), str(poke["longitude"]), int(poke["expiration_time"])-int(time.time()))
#         pokelocs.append(pokeloc)
# else:
#     print "Pokevision is rate-limiting us right now"
# print pokelocs
