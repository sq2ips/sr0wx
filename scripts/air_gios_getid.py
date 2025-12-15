import sys
import requests
from pprint import pprint

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
    return text

url = "https://api.gios.gov.pl/pjp-api/v1/rest/station/findAll?size=500"
params = "Skrypt wyszukujący ID stacji jakości powietrza GIOŚ:\n\nParametry:\n-h: lista parametrów\n-a: pobierz listę ID wszystkich stacji\n-f: wyszukaj ID stacji na podstawie nazwy"

if len(sys.argv) == 1:
    print(params)
elif sys.argv[1] == "-a":
    print("Pobieranie danych... " ,end="")
    sys.stdout.flush()
    response = requests.get(url)
    if not response.ok:
        raise Exception("Not-OK response.")
    print("OK")
    response = response.json()
    stations = {}
    print("ID stacji: nazwa stacji")
    for station in response["Lista stacji pomiarowych"]:
        print(f"{station["Identyfikator stacji"]}: {station["Nazwa stacji"]}")
elif sys.argv[1] == "-f":
    print("Pobieranie danych... " ,end="")
    sys.stdout.flush()
    response = requests.get(url)
    if not response.ok:
        raise Exception("Not-OK response.")
    print("OK")
    response = response.json()
    stations = response["Lista stacji pomiarowych"]

    print("Nazwa stacji: ID stacji")
    for station in stations:
        if trimSpecials(sys.argv[2]) in trimSpecials(station["Nazwa stacji"]):
            print(f"{station["Nazwa stacji"]}: {station["Identyfikator stacji"]}")
else:
    print(params)