import requests
from urllib.parse import urlparse, parse_qs, quote_plus
import bs4 as bs
import shutil
from tqdm import tqdm
import json
import glob
import sys
import os
import getopt

sys.path.append("../")

from pl_google import trim_pl

slownik_filename = "slownik.json"
samples_dir = "../pl_google/samples/"
lang = "pl"
gender = "female"

def requestData(url, timeout, repeat):
    for i in range(repeat):
        try:
            data = requests.get(url, timeout=timeout)
            if not data.ok:
                raise Exception("Got wrong response")
            else:
                break
        except Exception as e:
            if i < repeat - 1:
                print(f"Exception getting data: {e}, trying again...")
            else:
                raise e
    return data

def getApiKey():
    print("Uzyskiwanie klucza API... ", end="")
    url = "https://responsivevoice.org/"
    data = requestData(url, 15, 4)
    soup = bs.BeautifulSoup(data.text, "lxml")
    elem = soup.find("script", attrs={"id": "responsive-voice-js"})
    src = elem.get("src")
    query = urlparse(src).query
    query_elements = parse_qs(query)
    key = query_elements["key"][0]
    print("OK")
    return key

def GetMp3(word, filename, key):
    url = f"https://texttospeech.responsivevoice.org/v1/text:synthesize?lang={lang}&engine=g1&name=&pitch=0.5&rate=0.5&volume=1&key={key}&gender={gender}&text={quote_plus(word)}"

    data = requestData(url, 15, 5)
    open(f"mp3/{filename}.mp3", "wb").write(data.content)

def convert(filename):
    if not os.path.exists("ogg/"):
        os.mkdir("ogg")
    code = os.system(f"ffmpeg -hide_banner -loglevel error -y -i \"./mp3/{filename}.mp3\" -af silenceremove=start_periods=1:start_duration=0:start_threshold=-60dB:stop_periods=-1:stop_duration=0:stop_threshold=-60dB -ar 22050 -acodec libvorbis \"./ogg/{filename}.ogg\"")
    if code != 0:
        raise Exception("ffmpeg returned non zero exit code.")
    os.remove(f"mp3/{filename}.mp3")

def GetOgg(phrase, key):
    filename, word = phrase
    if filename in ["", None]:
        raise ValueError("Pusta nazwa pliku")
    if word in ["", None]:
        raise ValueError("Puste słowo")
    GetMp3(word, filename, key)
    convert(filename)
    if not os.path.exists(f"ogg/{filename}.ogg"):
        raise FileExistsError(f"Plik sampla {filename} nie wygenerowany.")

def generate(slownik, key):
    for slowo in tqdm(slownik, unit="samples"):
        try:
            GetOgg(slowo, key)
        except Exception as e:
            print(f"Podczas generowania sampla {slowo} otrzymano błąd: {e}")

def getExistingSamples(path):
    files = glob.glob(path)

    samples = []
    for file in files:
        samples.append(file.split("/")[-1].split(".")[0])
    return samples

def loadSlownik(filename):
    print(f"Ładowanie danych z pliku {filename}... ", end="")
    with open(filename, "r") as f:
        data = json.load(f)
    slownik_custom = data["slownik"]
    slownik_auto = data["slownik_auto"]
    print("OK")

    return slownik_custom, slownik_auto

def makeSamplesList(slownik_custom, slownik_auto):
    print("Tworzenie listy sampli... ", end="")
    
    slownik = []
    if len(slownik_custom) > 0:
        for slowo in list(slownik_custom.keys()):
            slownik.append([slowo, slownik_custom[slowo]])
    if len(slownik_auto) > 0:
        for slowo in slownik_auto:
            slownik.append([trim_pl(slowo), slowo])
    print("OK")
    
    print(f"Liczba wszystkich sampli w słowniku: {len(slownik)}")
    return slownik

def saveSlownikData(filename, slownik_custom, slownik_auto):
    print(f"Zapisywanie danych do pliku {filename}... ", end="")

    with open(filename, "w") as f:
        json.dump({"slownik": slownik_custom, "slownik_auto": slownik_auto}, f, ensure_ascii=False, indent=4)
    print("OK")

print("Uruchamiane...")

opts, args = getopt.getopt(sys.argv[1:], "p:msr")

move = False
saveSlownik = False
regenerate = False
phrases_auto = []
phrases_custom = []
for opt, arg in opts:
    if opt == "-m": #
        move = True
    elif opt == "-p": #
        if len(arg.split(",")) == 1:
            phrases_auto.append(arg)
        elif len(arg.split(",")) == 2:
            phrases_custom.append(arg.split(","))
        else:
            print(f"Invalid phrase format {arg}")
    elif opt == "-s": #
        saveSlownik = True
        move = True
    elif opt == "-r":
        regenerate = True
        move = True

print("Sprawdzanie katalogu mp3/...")
if os.path.exists("mp3/"):
    print("Katalog istnieje, usuwanie...")
    shutil.rmtree("mp3")
print("Tworzenie nowego katalogu mp3/")
os.mkdir("mp3")

slownik = []

if (len(phrases_auto) + len(phrases_custom)) > 0:
    if len(phrases_auto) > 0:
        for slowo in phrases_auto:
            slownik.append([trim_pl(slowo), slowo])
    if len(phrases_custom) > 0:
        slownik += phrases_custom
else:
    slownik_custom, slownik_auto = loadSlownik(slownik_filename)
    slownik = makeSamplesList(slownik_custom, slownik_auto)

slowa_files = getExistingSamples("".join([samples_dir, "*"]))

slownik_new = []

if not regenerate:
    for i, slowo in enumerate(slownik):
        if not slowo[0] in slowa_files:
            slownik_new.append(slowo)

    slownik = slownik_new

if len(slownik) > 0:
    print(f"Liczba sampli do wygenerowania: {len(slownik)}")
else:
    print("Brak sampli do wygenerowania")
    exit()

key = getApiKey()

print("Uruchamianie genertora...")

generate(slownik, key)

print("usuwanie katalogu mp3/...")
os.removedirs("mp3/")

if saveSlownik:
    if (len(phrases_auto) + len(phrases_custom)) > 0:
        slownik_custom, slownik_auto = loadSlownik(slownik_filename)
        if len(phrases_auto) > 0:
            slownik_auto += phrases_auto
        if len(phrases_custom) > 0:
            slownik_custom.update(phrases_custom)
        
        print("Sortowanie... ", end="")
        slownik_custom = dict(sorted(slownik_custom.items()))
        slownik_auto = list(set(list(slownik_auto)))
        slownik_auto = sorted(slownik_auto)
        print("OK")

        saveSlownikData(slownik_filename, slownik_custom, slownik_auto)
    else:
        print("Brak sampli do zapisania.")

if regenerate:
    print("Removing old samples...")
    shutil.rmtree(samples_dir)
    print("OK", end="")
    os.path.mkdir(samples_dir)

if move:
    files = glob.glob("./ogg/*")
    if len(files) > 0:
        print(f"Przenoszenie sampli do {samples_dir}...")
        print(files)
        for file in tqdm(files, unit="files"):
            shutil.move(file, "".join([samples_dir]))
    else:
        print("No files to move.")