import sys
import getopt
import requests
import json

sys.path.append("../")

from pl_google import trim_pl

url = "https://hydro-back.imgw.pl/list/hydro"
slownik_file = "../audio_generator/slownik.json"

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
update = False
file = None

try:
    argv = sys.argv[1:]
    if argv == []:
        raise getopt.GetoptError("No options got")
    opts, args = getopt.getopt(argv, "z:w:s:acu")
except getopt.GetoptError:
    print(
        "Program generujący sample nazw rzek i wodowskazów do modułu imgw_podest_sq2ips, parametry:\n-a pobieranie wszystkich sampli\n-z pobieranie sampli z danej zlewni (na podstawie id zlewni)\n-w pobieranie sampli danego wodowskazu (na podstawie id wodowskazu)\n-f plik json do zapisu nazw sampli\n-u aktualizacja słownika (zamienne z -f)\n-c sprawdzenie istniejących sampli w słowniku"
    )
    exit()

for opt, arg in opts:
    if opt == "-c":
        check = True
    if opt == "-s":
        if not update:
            file = arg
    if opt == "-a":
        all = True
    if opt == "-u":
        update = True
        file = None
    if opt == "-z":
        zlewnie += [z for z in arg.split(",")]
    elif opt == "-w":
        wodowskazy += [w for w in arg.split(",")]

if not all and zlewnie == [] and wodowskazy == []:
    raise Exception("Brak sampli do wyszukania, użyj -a, -z lub -w")

print("Pobieranie danych... ", end="")
sys.stdout.flush()
stations = requests.get(url).json()
print("OK")

samples = []
for s in stations:
    if (s["catchment"] is not None and s["catchment"] in zlewnie or s["code"] is not None and s["code"] in wodowskazy) or all:
        samples.append(parseName(s["river"]))
        samples.append(parseName(s["name"]))

samples = sorted(list(set(samples)))

print(f"Liczba sampli: {len(samples)}")

samples_new = []

if check:
    print("Sprawdzanie isniejących sampli w słowniku...")
    with open(slownik_file, "r") as f:
        slownik = json.load(f)
    for s in samples:
        if s.lower() in [sl.lower() for sl in slownik["slownik_auto"]]:
            print(f"sampel: {s.lower()} jest już w słowniku, pomijanie...")
        else:
            samples_new.append(s)
    samples = samples_new

for s in samples:
    if s == "":
        del samples[samples.index(s)]

print(f"Liczba sampli po sprawdzeniu: {len(samples)}")
if len(samples) > 0:
    if file is not None:
        print(f"Zapisywanie sampli do pliku {file}... ", end="")
        sys.stdout.flush()
        with open(file, "w") as f:
            json.dump(samples, f, indent=4, ensure_ascii=False)
        print("OK")
    elif update:
        print("Aktualizowanie słownika (nie zapomnij wygenerować sampli)... ", end="")
        sys.stdout.flush()
        if slownik is None:
            with open(slownik_file, "r") as f:
                slownik = json.load(f)
        with open(slownik_file, "w") as f:
            json.dump({"slownik": slownik["slownik"], "slownik_auto": sorted(list(set(slownik["slownik_auto"]+samples)))}, f, indent=4, ensure_ascii=False)
        print("OK")
            
    else:
        print(json.dumps(samples, indent=4, ensure_ascii=False))
else:
    print("Brak brakującyh sampli.")
