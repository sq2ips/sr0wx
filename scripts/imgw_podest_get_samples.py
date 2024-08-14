import sys
import getopt
import requests
import json

sys.path.append("../")

from pl_google import trim_pl

url = "https://hydro-back.imgw.pl/list/hydrologic"


def parseName(name):
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
    river = " ".join(river)
    river = river.replace(" - ", " ").replace("-", " ").replace("_", " ")
    river = " ".join(river.split())
    return river


zlewnie = []
wodowskazy = []
all = False
check = False
file = None

try:
    argv = sys.argv[1:]
    if argv == []:
        raise getopt.GetoptError("No options got")
    opts, args = getopt.getopt(argv, "z:w:s:ac")
except getopt.GetoptError:
    print(
        "Program generujący sample nazw rzek i wodowskazów do modułu imgw_podest_sq2ips, parametry:\n-a pobieranie wszystkich sampli\n-z pobieranie sampli z danej zlewni\n-w pobieranie sampli danego wodowskazu\n-fplik json do zapisu nazw sampli"
    )
    exit()

for opt, arg in opts:
    if opt == "-c":
        check = True
    if opt == "-s":
        file = arg
    if opt == "-a":
        all = True
    if opt == "-z":
        zlewnie += [int(z) for z in arg.split(",")]
    elif opt == "-w":
        wodowskazy += [int(w) for w in arg.split(",")]

stations = requests.get(url).json()

samples = []
for s in stations:
    if (
        s["catchment"] is not None
        and int(s["catchment"]) in zlewnie
        or s["code"] is not None
        and int(s["code"]) in wodowskazy
    ) or all:
        samples.append(parseName(s["river"]))
        samples.append(parseName(s["name"]))

samples = list(set(samples))

print(f"Liczba sampli: {len(samples)}")
if check:
    with open("../audio_generator/slownik.json", "r") as f:
        slownik = json.load(f)
    for s in samples:
        if s in [sl.lower() for sl in slownik["slownik_auto"]]:
            print(f"sampel: {s.lower()} jest już w słowniku, pomijanie...")
            del samples[samples.index(s)]

for s in samples:
    if s == "":
        del samples[samples.index(s)]

print(f"Liczba sampli po sprawdzeniu: {len(samples)}")

if len(samples) > 0:
    if file is not None:
        with open(file, "w") as f:
            json.dump(samples, f, ensure_ascii=False)
        print(f"Zapisano sample do pliku {file}")
    else:
        print(json.dumps(samples, indent=4, ensure_ascii=False))
else:
    print("brak brakującyh sampli")
