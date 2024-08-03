import requests
import sys

parameters = "Program szukający id regionu do modułu meteoalert_sq2ips.py:\n\nParametry:\n-h wyświetlenie listy parametrów\n-a pobranie i wypisanie wszystkich obszarów\n-f pobranie i flitrowanie na podstawie wporwadzonego tekstu"

url = "https://meteo.imgw.pl/dyn/data/out1proc.json?v=1.2"

if len(sys.argv) == 1 or sys.argv[1] == "-h":
    print(parameters)
    exit(0)
elif sys.argv[1] == "-a":
    print("Program szukający id obszaru do modułu meteoalert_sq2ips.py")
    print("Pobieranie danych..")
    names = requests.get(url).json()
    print("Przetwarzanie danych...")
    print(f"Ilość regionów: {len(names["features"])}\n")
    print("miasto/powiat: id stacji")
    for i in names["features"]:
        print(f'{i["properties"]["jpt_nazwa_"]}: {i["properties"]["jpt_kod_je"]}')
elif sys.argv[1] == "-f":
    print("Program szukający id stacji do modułu meteoalert_sq2ips.py\n")
    print(f"wyszukiwanie id na podstawie filtra: {sys.argv[2]}")
    print("Pobierane danych...")
    names = requests.get(url).json()
    print("Przetwarzanie danych...")
    print(f"Ilość regionów: {len(names["features"])}\n")
    print("miasto/powiat: id stacji")
    any = True
    for i in names["features"]:
        if i["properties"]["jpt_nazwa_"].lower().find(sys.argv[2].lower()) != -1:
            print(f'{i["properties"]["jpt_nazwa_"]}: {i["properties"]["jpt_kod_je"]}')
    if any == False:
        print("Nic nie znaleziono")
else:
    print("Nieznany parametr.")
    print(parameters)
