from curl_cffi import requests
import bs4 as bs
import shutil
from tqdm import tqdm
import json
import glob
import sys
import os
import getopt
from time import sleep
import urllib.parse
from bs4 import BeautifulSoup

sys.path.append("../")

from pl_google import trim_pl

dictionary_filename = "slownik.json"
samples_dir = "../pl_google/samples/"
lang = "pl"
gender = "female"
delay_time = 60

def requestData(url, timeout, repeat, headers, params):
    for i in range(repeat):
        try:
            data = requests.get(url, timeout=timeout, headers=headers, params=params)
            if not data.ok:
                raise Exception(f"Wrong server response: received {data}")
            else:
                break
        except Exception as e:
            if i < repeat - 1:
                print(f"Exception getting data: {e}, trying again...")
            else:
                raise e
    return data

def getKey():
    url = "https://responsivevoice.org/"  # replace with the target URL

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    script_tag = soup.find("script", id="responsive-voice-js")

    if script_tag:
        src = script_tag.get("src")
        if src:
            key = src.split("=")[1]
            return key
        else:
            print("Error getting key: Script found, but it has no src attribute.")
    else:
        raise Exception("Error getting key: Script with id 'responsive-voice-js' not found.")


def GetMp3(word, filename, key):
    headers = {
    'sec-ch-ua-platform': '"Linux"',
    'Referer': 'https://responsivevoice.org/',
    }

    params = {
        'text': word,
        'lang': 'pl',
        'engine': 'g1',
        'name': '',
        'pitch': '0.5',
        'rate': '0.5',
        'volume': '1',
        'key': key,
        'gender': 'female',
    }

    url = 'https://texttospeech.responsivevoice.org/v1/text:synthesize'

    sample_response = requestData(url, 15, 3, params=params, headers=headers)
    status_code = sample_response.status_code
    if status_code == 200:
        open(f"mp3/{filename}.mp3", "wb").write(sample_response.content)
    elif status_code == 429:
        print(f"Got Too Many Requests error code, waiting {delay_time}s...")
        sleep(delay_time)
        GetMp3(word, filename, key)
    elif status_code == 403:
        print("Got error 403 probably IP is banned, try again later.")
        exit(1)
    else:
        raise Exception(f"Got response code {status_code}")


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
        raise ValueError("Empty file name")
    if word in ["", None]:
        raise ValueError("Empty sample")
    GetMp3(word, filename, key)
    convert(filename)
    if not os.path.exists(f"ogg/{filename}.ogg"):
        raise FileExistsError(f"Sample file {filename} not generated.")
    elif os.path.getsize(f"ogg/{filename}.ogg") == 0:
        raise Exception(f"Sample file {filename} is empty.")
    elif os.system(f"ffmpeg -i ogg/{filename}.ogg -f null -err_detect +crccheck+bitstream+buffer+explode+careful+compliant+aggressive -v error -xerror -") != 0:
        raise Exception(f"Sample file {filename} corrupted.")

def generate(dictionary, key):
    for sample in tqdm(dictionary, unit="samples"):
        try:
            GetOgg(sample, key)
        except Exception as e:
            print(f"While generating sample {sample} got error: {e}")
            if os.path.exists(f"ogg/{sample[0]}.ogg"):
                print(f"Removing file ogg/{sample[0]}.ogg...")
                os.remove(f"ogg/{sample[0]}.ogg")

def getExistingSamples(path):
    files = glob.glob(path)

    samples = []
    for file in files:
        samples.append(file.split("/")[-1].split(".")[0])
    return samples

def loadSlownik(filename):
    print(f"Loading dictionary from file {filename}... ", end="")
    with open(filename, "r") as f:
        data = json.load(f)
    dictionary_custom = data["slownik"]
    dictionary_auto = data["slownik_auto"]
    print("OK")

    return dictionary_custom, dictionary_auto

def makeSamplesList(dictionary_custom, dictionary_auto):
    print("Creating samples list... ", end="")
    
    dictionary = []
    if len(dictionary_custom) > 0:
        for sample in list(dictionary_custom.keys()):
            dictionary.append([sample, dictionary_custom[sample]])
    if len(dictionary_auto) > 0:
        for sample in dictionary_auto:
            dictionary.append([trim_pl(sample), sample])
    print("OK")
    
    print(f"Number of all samples in dictionary: {len(dictionary)}")
    return dictionary

def saveSlownikData(filename, dictionary_custom, dictionary_auto):
    print(f"Saving samples to file {filename}... ", end="")

    with open(filename, "w") as f:
        json.dump({"slownik": dictionary_custom, "slownik_auto": dictionary_auto}, f, ensure_ascii=False, indent=4)
    print("OK")

print("Uruchamiane...")

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:msr")
except getopt.GetoptError:
    print("Generator sampli do modułu językowego pl_google:\n\nParametry\n-m przeniesienie wygenerowanych sampli do katalogu ../pl_google/samples/\n-p podane nowych sampli do wygenerowania, w przypadku sampli neregularnych format to -p nazwa_pliku|sampel (każdy kolejny sampel to kolejny parametr)\n-s zapisanie podanych sampli do słownika\n-r ponowne wygenerowanie wszystkich sampli ze słownika")
    exit()

move = False
saveSlownik = False
regenerate = False
phrases_auto = []
phrases_custom = []
for opt, arg in opts:
    if opt == "-m":
        move = True
    elif opt == "-p":
        if len(arg.split("|")) == 1:
            phrases_auto.append(arg)
        elif len(arg.split("|")) == 2:
            phrases_custom.append(arg.split("|"))
        else:
            print(f"Invalid format {arg}")
    elif opt == "-s":
        saveSlownik = True
        move = True
    elif opt == "-r":
        regenerate = True
        move = True

print("Checking directory mp3/...")
if os.path.exists("mp3/"):
    print("Directory exists, usuwanie...")
    shutil.rmtree("mp3")
print("Creating new directory mp3/")
os.mkdir("mp3")

print("Getting key...")
key = getKey()

dictionary = []

if (len(phrases_auto) + len(phrases_custom)) > 0:
    if len(phrases_auto) > 0:
        for sample in phrases_auto:
            dictionary.append([trim_pl(sample), sample])
    if len(phrases_custom) > 0:
        dictionary += phrases_custom
else:
    dictionary_custom, dictionary_auto = loadSlownik(dictionary_filename)
    dictionary = makeSamplesList(dictionary_custom, dictionary_auto)

slowa_files = getExistingSamples("".join([samples_dir, "*"]))

dictionary_new = []

if not regenerate:
    for i, sample in enumerate(dictionary):
        if not sample[0] in slowa_files:
            dictionary_new.append(sample)

    dictionary = dictionary_new

if len(dictionary) > 0:
    print(f"Number of samples to generate: {len(dictionary)}")
else:
    print("No samples to generate")
    exit()

print("Starting generator...")

generate(dictionary, key)

print("removing directory mp3/...")
os.removedirs("mp3/")

if saveSlownik:
    if (len(phrases_auto) + len(phrases_custom)) > 0:
        dictionary_custom, dictionary_auto = loadSlownik(dictionary_filename)
        if len(phrases_auto) > 0:
            dictionary_auto += phrases_auto
        if len(phrases_custom) > 0:
            dictionary_custom.update(phrases_custom)
        
        print("Sorting... ", end="")
        dictionary_custom = dict(sorted(dictionary_custom.items()))
        dictionary_auto = list(set(list(dictionary_auto)))
        dictionary_auto = sorted(dictionary_auto)
        print("OK")

        saveSlownikData(dictionary_filename, dictionary_custom, dictionary_auto)
    else:
        print("No samples to save.")

if regenerate:
    print("Removing old samples...")
    shutil.rmtree(samples_dir)
    print("OK", end="")
    os.mkdir(samples_dir)

if move:
    files = glob.glob("./ogg/*")
    if len(files) > 0:
        print(f"Moving samples to {samples_dir}...")
        for file in tqdm(files, unit="files"):
            shutil.move(file, "".join([samples_dir]))
    else:
        print("No files to move.")