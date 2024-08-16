import requests
import sys
import json
import getopt

sys.path.append("../")

from pl_google import trim_pl

def trimSpecials(text):
    text = text.lower()\
        .replace("-", " ")\
        .replace("/", " ")\
        .replace("_", " ")\
        .replace("(", "")\
        .replace(")", "")\
        .replace("ii", "drógiego")\
        .replace("wlkp.", "wielkopolski")\
        .replace("gen.", "generała")\
        .replace("ul.", "ulica")\
        .replace("wyb.", "wybrzeże")\
        .replace("os.", "osiedle")\
        .replace("kard.", "kardynała")\
        .replace("al.", "aleja")\
        .replace("ks.", "księdza")\
        .replace("św.", "świętego")
    text = text.split()
    
    text_new = []
    for t in text:
        if not (len(t) == 2 and t[1] == "."):
            text_new.append(t)
    
    return " ".join(text_new)

url = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"
slownik_file = "../audio_generator/slownik.json"

try:
    argv = sys.argv[1:]
    if argv == []:
        raise getopt.GetoptError("No options got")
    opts, args = getopt.getopt(argv, "as:u")
except getopt.GetoptError:
    print("Program wyszukujący id stacji pomiarowej do modułu air_pollution_sq9atk\n\nParametry:\n-a wypisanie wszystkich nazw stacji (jako json)\n-s wypisywanie nazw stacji na podstawie podanego id (oddzielanych przecinkiem)\n-u zapis do słownika")
    exit()

all = False
update = False
ids = []

for opt, arg in opts:
    if opt == "-a":
        all = True
    if opt == "-u":
        update = True
    if opt == "-s":
        ids = arg.split(",")
if not all and ids == []:
    print("brak podanych parametrów")
    exit(1)

print("Pobieranie danych... " ,end="")
sys.stdout.flush()
data = requests.get(url).json()
print("OK")

print("Przetwarzanie danych... " ,end="")
sys.stdout.flush()
stations = {}
for station in data:
    stations[station["id"]] = station["stationName"]
print("OK")

stations_selected = []
if all:
    stations = list(stations.values())
else:
    for id in ids:
        stations_selected.append(stations[int(id)])
    stations = stations_selected

stations_dict = {}

for station in stations:
    stations_dict[trim_pl(station)] = trimSpecials(station)

if update:
    with open(slownik_file, "r") as f:
        slownik = json.load(f)

    stations_dict_new = {}
    for station in (stations_dict.keys()):
        if station not in slownik["slownik"]:
            stations_dict_new[station] = stations_dict[station]
            pass
        else:
            print(f"Sampel {station} jest już w słowniku")

    print(len(stations_dict_new), len(stations_dict))
    stations_dict = stations_dict_new
            
    slownik["slownik"].update(stations_dict)

    #with open(slownik_file, "w") as f:
    #    json.dump({"slownik": slownik["slownik"], "slownik_auto": slownik["slownik_auto"]}, f, indent=4, ensure_ascii=False)
else:
    print(json.dumps(stations_dict, indent=4, ensure_ascii=False))