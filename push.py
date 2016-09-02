import os
import sys

def send_push(name):
    if not os.getenv("USER") == "namin": return

    apikey = "o.Jc3IobArEh5OL0wlxoMJlLbJeiOmbh4G"
    body = "Found a %s" % name
    title = "%s" % name
    cmd = """curl --header 'Access-Token: %s' --header 'Content-Type: application/json' --data-binary '{"body":"%s","title":"%s","type":"note"}' --request POST https://api.pushbullet.com/v2/pushes"""
    cmd = cmd % (apikey, body, title)
    os.system(cmd)
