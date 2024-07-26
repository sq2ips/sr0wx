import sys
import getopt
import requests
import json

sys.path.append('../')

from pl_google import trim_pl

url = "https://hydro-back.imgw.pl/list/hydrologic"

def parseRiverName(name):
    na = ["(", ")", "jez.", "morze"]
    river = []
    for r in name.lower().split():
        dne = True
        for n in na:
            if n in r:
                dne = False
                break
        if dne:
            river.append(r)
    river = "_".join(river)
    return river

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, "z:w:")
zlewnie = []
wodowskazy = []
for opt, arg in opts:
    if opt == "-z":
        zlewnie += [int(z) for z in arg.split(",")]
    elif opt == "-w":
        wodowskazy += [int(w) for w in arg.split(",")]

stations = requests.get(url).json()

samples = []
for s in stations:
    if s["catchment"] is not None and int(s["catchment"]) in zlewnie or s["code"] is not None and int(s["code"]) in wodowskazy:
        samples.append(trim_pl(parseRiverName(s["river"])))
        samples.append(trim_pl(s["name"]))
    
print(json.dumps(samples, indent=4))