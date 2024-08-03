import requests
import sys

parameters = "Program szukający id do modułu meteo_yr_sq2ips.py:\n\nParametry:\n-h wyświetlenie listy parametrów\n-f pobranie i flitrowanie na podstawie wporwadzonego tekstu"

url = "https://www.yr.no/api/v0/locations/search?language=en&q="

if len(sys.argv) == 1 or sys.argv[1] == "-h":
    print(parameters)
    exit(0)
elif sys.argv[1] == "-f":
    print("Program szukający id stacji do modułu meteo_yr_sq2ips.py\n")
    print(f"wyszukiwanie id na podstawie filtra: {sys.argv[2]}")
    print("Pobierane danych...")
    r = requests.get(url + sys.argv[2]).json()
    print("Przetwarzanie danych...")
    print(f"Ilość wyników: {r["totalResults"]}\n")
    print("miasto/obszar: id stacji")
    for id in r["_embedded"]["location"]:
        text = f'{id["name"]}, {id["category"]["name"]}, '
        if "subregion" in id:
            text += f"{id["subregion"]["name"]}, "
        if "region" in id:
            text += f"{id["region"]["name"]} "
        text += f"({id["country"]["name"]}), elevation {id["elevation"]}m: "
        text += f"{id["id"]}"
        print(text)
else:
    print("Nieznany parametr.")
    print(parameters)
