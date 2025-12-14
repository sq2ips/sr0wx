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
        .replace(" iii", " trzeciego")\
        .replace(" ii", " drógiego")\
        .replace("wlkp.", "wielkopolski")\
        .replace("gen.", "generała")\
        .replace("ul.", "ulica")\
        .replace("wyb.", "wybrzeże")\
        .replace("os.", "osiedle")\
        .replace("kard.", "kardynała")\
        .replace("al.", "aleja ")\
        .replace("pl.", "plac")\
        .replace(" ak ", " armii krajowej ")\
        .replace("ks.", "księdza")\
        .replace("św.", "świętego")\
        .replace("imgw", "IMGW")\
        .replace("imigw", "IMGW")\
        .replace("kpn", "KPN")\
        .replace("rpn", "RPN")\
        .replace(" mpn", " MPN")\
        .replace("igf pan", "IGF PAN")\
        .replace("100", "stó")
    text = text.split()
    
    return " ".join(text)

url = "https://api.gios.gov.pl/pjp-api/v1/rest/station/findAll?size=500"
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
for station in data["Lista stacji pomiarowych"]:
    stations[station["Identyfikator stacji"]] = station["Nazwa stacji"]
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

print(f"Liczba sampli: {len(stations_dict)}")

if update:
    with open(slownik_file, "r") as f:
        slownik = json.load(f)

    stations_dict_new = {}
    for station in (stations_dict.keys()):
        if station not in slownik["slownik"]:
            stations_dict_new[station] = stations_dict[station]
        else:
            print(f"Sampel {station} jest już w słowniku")

    print(f"Liczba sampli po sprawdzeniu: {len(stations_dict_new)}")
    stations_dict = stations_dict_new
            
    slownik["slownik"].update(stations_dict)

    with open(slownik_file, "w") as f:
        json.dump({"slownik": slownik["slownik"], "slownik_auto": slownik["slownik_auto"]}, f, indent=4, ensure_ascii=False)
else:
    print(json.dumps(stations_dict, indent=4, ensure_ascii=False))