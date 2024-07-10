import requests
from urllib.parse import urlparse, parse_qs, quote_plus
import bs4 as bs
from tqdm import tqdm
import os
import sys
import glob
import shutil
import json

gender = "female"
lang = "pl"

apikey = None

apicounter = 0

def requestData(url, timeout, repeat, headers=None):
    for i in range(repeat):
        try:
            data = requests.get(url, timeout=timeout, headers=headers)
            if not data.ok:
                raise Exception("Got wrong response")
            else:
                break
        except Exception as e:
            if i < repeat-1:
                print(f"Error: {e}, trying again...")
            else:
                raise e
    return data

def GetKey(apikey):
    if apikey is not None:
        return apikey
    url = 'https://responsivevoice.org/'
    data = requestData(url, 15, 4)
    soup = bs.BeautifulSoup(data.text, 'lxml')
    elem = soup.find('script', attrs={'id': 'responsive-voice-js'})
    src = elem.get('src')
    query = urlparse(src).query
    query_elements = parse_qs(query)
    key = query_elements['key'][0]

    return key

def TrimPl(word):
    word = word\
        .lower()\
        .replace(("ą"), "a_")\
        .replace(("ć"), "c_")\
        .replace(("ę"), "e_")\
        .replace(("ł"), "l_")\
        .replace(("ń"), "n_")\
        .replace(("ó"), "o_")\
        .replace(("ś"), "s_")\
        .replace(("ź"), "z_")\
        .replace(("ż"), "z_")\
        .replace(":", "")\
        .replace(",", "")\
        .replace(" ", "_")
    return (word)

def GetMp3(word, filename, key):
    url = f'https://texttospeech.responsivevoice.org/v1/text:synthesize?lang={lang}&engine=g1&name=&pitch=0.5&rate=0.5&volume=1&key={key}&gender={gender}&text={quote_plus(word)}'
    
    data = requestData(url, 15, 5)
    open(f'mp3/{filename}.mp3', 'wb').write(data.content)

def convert(filename):
    if not os.path.exists("ogg/"):
        os.mkdir("ogg")
    os.system(
        f"ffmpeg -hide_banner -loglevel error -y -i \"mp3/{filename}.mp3\" -af silenceremove=start_periods=1:start_duration=0:start_threshold=-60dB:stop_periods=-1:stop_duration=0:stop_threshold=-60dB -ar 22050 -acodec libvorbis \"ogg/{filename}.ogg\"")
    os.remove(f"mp3/{filename}.mp3")


def GetOgg(l, key):
    filename = l[1]
    word = l[0]
    # print(f"word: {word} | filename: {filename}")
    GetMp3(word, filename, key)
    convert(filename)
    return(os.path.exists(f"ogg/{filename}.ogg"))

if __name__ == "__main__":
    print("Uruchamianie...")
    print("Sprawdzanie katalogu mp3/...")
    if os.path.exists("mp3/"):
        print("Katalog istnieje, usuwanie...")
        shutil.rmtree('mp3')
    print("Tworzenie nowego katalogu mp3/")
    os.mkdir("mp3")
    slownik_list = []

    print("Ładowanie danych z pliku slownik.json...")
    with open("slownik.json", "r") as f:
        data = json.load(f)
    slownik = data["slownik"]
    slownik_auto = data["slownik_auto"]

    print("Tworzenie listy sampli...")

    for slowo in list(slownik.keys()):
        slownik_list.append([slownik[slowo], slowo])
    for slowo in slownik_auto:
        slownik_list.append([slowo, TrimPl(slowo)])

    slownik_list_new = []
    files = glob.glob("ogg/")
    for f in slownik_list:
        if f[1] not in files:
            slownik_list_new.append(f)
    
    print(f"Liczba sampli do wygenerowania: {len(slownik_list)}")
    print(f"Liczba wszystkich sampli: {len(slownik_list)}")
    print("Uruchamianie generatora...")

    c = 0
    notgenerated = []
    key = GetKey(apikey)
    for slowo in tqdm(slownik_list_new, unit="samples"):
        try:
            if GetOgg(slowo, key):
                c+=1
            else:
                raise Exception("Plik nie utwożony.")
        except Exception as e:
            notgenerated.append(slowo)
    print(f"Niewygenerowano {len(notgenerated)}")
    print(f"Wygenerowano {c}/{len(slownik_list)}")

    print("usuwanie katalogu mp3/...")
    os.removedirs("mp3/")
