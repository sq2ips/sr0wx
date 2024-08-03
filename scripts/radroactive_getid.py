import requests
import sys

parameters = "Program szukający id stacji do modułu radioactive_sq2ips.py:\n\nParametry:\n-h wyświetlenie listy parametrów\n-a pobranie i wypisanie wszystkich obszarów\n-f pobranie i flitrowanie na podstawie wporwadzonego tekstu"

url = "https://monitoring.paa.gov.pl/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=paa:kcad_siec_pms_moc_dawki_mapa&outputFormat=application/json"

if len(sys.argv) > 1:
    if sys.argv[1] == "-h":
        print(parameters)
        exit(0)
    elif sys.argv[1] == "-a":
        print("Program szukający id stacji do modułu radioactive_sq2ips.py\n")
        print("miasto: id stacji")
        data = requests.get(url).json()
        for i in range(len(data["features"])):
            print(
                f'{data["features"][i]["properties"]["stacja"]}: {data["features"][i]["properties"]["id"]}'
            )
    elif sys.argv[1] == "-f":
        print("Program szukający id stacji do modułu radioactive_sq2ips.py\n")
        print(f"wyszukiwanie id na podstawie filtra: {sys.argv[2]}")
        print("miasto: id stacji")
        data = requests.get(url).json()
        any = False
        for i in range(len(data["features"])):
            if (
                data["features"][i]["properties"]["stacja"]
                .lower()
                .find(
                    sys.argv[2]
                    .lower()
                    .replace(("ą"), "a")
                    .replace(("ć"), "c")
                    .replace(("ę"), "e")
                    .replace(("ł"), "l")
                    .replace(("ń"), "n")
                    .replace(("ó"), "o")
                    .replace(("ś"), "s")
                    .replace(("ź"), "z")
                    .replace(("ż"), "z")
                )
                != -1
            ):
                print(
                    f'{data["features"][i]["properties"]["stacja"]}: {data["features"][i]["properties"]["id"]}'
                )
                any = True
            if any == False:
                print("Nic nie znaleziono")
