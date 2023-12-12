import requests
import sys

parameters = "Program szukający id stacji do modułu meteoalert_sq2ips.py:\n\nParametry:\n-h wyświetlenie listy parametrów\n-a pobranie i wypisanie wszystkich obszarów\n-f pobranie i flitrowanie na podstawie wporwadzonego tekstu"

url = "https://meteo.imgw.pl/dyn/data/out1proc.json?v=1.2"

if sys.argv[1] == "-h" or len(sys.argv) == 1:
    print(parameters)
    exit(0)
elif sys.argv[1] == "-a":
    print("Program szukający id stacji do modułu meteoalert_sq2ips.py\n")
    print("miasto/powiat: id stacji")
    names = requests.get(url).json()
    for i in range(len(names["features"])):
        print(f'{names["features"][i]["properties"]["jpt_nazwa_"]}: {names["features"][i]["properties"]["jpt_kod_je"]}')
elif sys.argv[1] == "-f":
    print("Program szukający id stacji do modułu meteoalert_sq2ips.py\n")
    print(f"wyszukiwanie id na podstawie filtra: {sys.argv[2]}")
    print("miasto/powiat: id stacji")
    names = requests.get(url).json()
    for i in range(len(names["features"])):
        if names["features"][i]["properties"]["jpt_nazwa_"].lower().find(sys.argv[2].lower()) != -1:
            print(f'{names["features"][i]["properties"]["jpt_nazwa_"]}: {names["features"][i]["properties"]["jpt_kod_je"]}')
else:
    print("Nieznany parametr.")
    print(parameters)