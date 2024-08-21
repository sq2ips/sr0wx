import requests
from urllib.parse import quote
import sys

parameters = "Program szukający id zlewni i wodowskazów do modułu imgw_podest_sq2ips.py:\n\nParametry:\n-h wyświetlenie listy parametrów\n-z wyszukiwanie id zlewni na podstawie nazwy miasta\n-s wyszukiwanie id zlewni i wodowskazu na podstawie nazwy wodowskazu\n-r wyszukiwanie id zlewni i wodowskazów na podstawie nazwy rzeki/akwenu\n-w wyszukiwanie id zlewni na podstawie id wodowskazu"

if len(sys.argv) == 1 or sys.argv[1] == "-h":
    print(parameters)
    exit(0)
elif sys.argv[1] == "-z":
    url = f"https://meteo.imgw.pl/api/geo/v3/search/{quote(sys.argv[2])}"
    print(
        "Wyszukiwanie id zlewni na podstawie nazwy miasta do modułu imgw_podest_sq2ips.py"
    )
    print("Pobieranie danych... ",end="")
    sys.stdout.flush()
    data = requests.get(url).json()
    print("OK")
    print("miasto, powiat, zlewnia: id\n")
    for z in data:
        print(
            f'{z["identifier"]}, pow. {z["district"]}, {z["base_catchment"]["name"]}: {z["base_catchment"]["ID"]}'
        )

elif sys.argv[1] == "-s":
    url = "https://hydro-back.imgw.pl/list/hydrologic"
    print(
        "Wyszukiwanie id zlewni i wodowskazu na podstawie nazwy wodowskazu do modułu imgw_podest_sq2ips.py"
    )
    print("Pobieranie danych... ",end="")
    sys.stdout.flush()
    data = requests.get(url).json()
    print("OK")
    print("rzeka/akwen, wodowskaz: id zlewni, id wodowskazu\n")

    for s in data:
        if sys.argv[2].lower() in s["name"].lower():
            print(f'{s["river"]}, {s["name"]}: {s["catchment"]}, {s["code"]}')

elif sys.argv[1] == "-r":
    url = "https://hydro-back.imgw.pl/list/hydrologic"
    print(
        "wyszukiwanie id zlewni i wodowskazów na podstawie nazwy rzeki/akwenu do modułu imgw_podest_sq2ips.py"
    )
    print("Pobieranie danych... ",end="")
    sys.stdout.flush()
    data = requests.get(url).json()
    print("OK")
    print("rzeka/akwen, wodowskaz: id zlewni, id wodowskazu\n")

    for s in data:
        if sys.argv[2].lower() in s["river"].lower():
            print(f'{s["river"]}, {s["name"]}: {s["catchment"]}, {s["code"]}')
elif sys.argv[1] == "-w":
    url = "https://hydro-back.imgw.pl/list/hydrologic"
    print(
        "Wyszukiwanie id zlewni na podstawie id wodowskazu do modułu imgw_podest_sq2ips.py"
    )
    print("Pobieranie danych... ",end="")
    sys.stdout.flush()
    data = requests.get(url).json()
    print("OK")
    print("rzeka/akwen, wodowskaz: id zlewni\n")

    for s in data:
        if sys.argv[2] == s["code"]:
            print(f'{s["river"]}, {s["name"]}: {s["catchment"]}')
