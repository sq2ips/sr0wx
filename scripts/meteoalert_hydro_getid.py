import requests
import sys

parameters = "Program szukający id regionu hydro (ostrzeżenia hydrologiczne) do modułu meteoalert_sq2ips.py:\n\nParametry:\n-h wyświetlenie listy parametrów\n-a pobranie i wypisanie wszystkich obszarów\n-f pobranie i flitrowanie na podstawie wporwadzonego tekstu"

url = "https://meteo.imgw.pl/dyn/data/zlew.json?v=1.37"

if len(sys.argv) == 1 or sys.argv[1] == "-h":
    print(parameters)
    exit(0)
elif sys.argv[1] == "-a":
    print("Program szukający id obszaru do modułu meteoalert_sq2ips.py")
    print("Pobieranie danych..")
    data = requests.get(url).json()["features"]
    print("Przetwarzanie danych...")
    print(f"Ilość regionów: {len(data)}\n")
    print("miasto/powiat: id stacji")
    for i in data:
        print(f'{i["properties"]["NAZWA"]}: {i["properties"]["KOD"]}')
elif sys.argv[1] == "-f":
    print("Program szukający id stacji do modułu meteoalert_sq2ips.py\n")
    print(f"wyszukiwanie id na podstawie filtra: {sys.argv[2]}")
    print("Pobierane danych...")
    data = requests.get(url).json()["features"]
    print("Przetwarzanie danych...")
    print(f"Ilość regionów: {len(data)}\n")
    print("miasto/powiat: id stacji")
    any = True
    for i in data:
        if i["properties"]["NAZWA"].lower().find(sys.argv[2].lower()) != -1:
            print(f'{i["properties"]["NAZWA"]}: {i["properties"]["KOD"]}')
    if any == False:
        print("Nic nie znaleziono")
else:
    print("Nieznany parametr.")
    print(parameters)
