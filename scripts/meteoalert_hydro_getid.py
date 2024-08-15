import requests
import sys

parameters = "Program szukający id zlewni (ostrzeżenia hydrologiczne) do modułu meteoalert_sq2ips.py:\n\nParametry:\n-h wyświetlenie listy parametrów\n-a pobranie i wypisanie wszystkich zlewni\n-f pobranie i flitrowanie na podstawie wporwadzonego tekstu"

url = "https://meteo.imgw.pl/dyn/data/zlew.json?v=1.37"

if len(sys.argv) == 1 or sys.argv[1] == "-h":
    print(parameters)
    exit(0)
elif sys.argv[1] == "-a":
    print("Pobieranie danych... ",end="")
    sys.stdout.flush()
    data = requests.get(url).json()["features"]
    print("OK")
    print("Przetwarzanie danych...")
    print(f"Ilość regionów: {len(data)}\n")
    print("miasto/powiat: id stacji")
    for i in data:
        print(f'{i["properties"]["NAZWA"]}: {i["properties"]["KOD"]}')
elif sys.argv[1] == "-f":
    print("Program szukający id zlewni do modułu meteoalert_sq2ips.py")
    print(f"wyszukiwanie id na podstawie filtra: {sys.argv[2]}")
    print("Pobieranie danych... ",end="")
    sys.stdout.flush()
    data = requests.get(url).json()["features"]
    print("OK")
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
