import requests
from urllib.parse import urlparse, parse_qs, quote_plus
import urllib.request
import bs4 as bs
from multiprocessing import Pool
from tqdm import tqdm
import os
import shutil

from slownik import slownik, slownik_auto


def GetKey():
    url = 'https://responsivevoice.org/'

    for i in range(4):
        try:
            data = requests.get(url, timeout=10)
            if data.ok == False:
                raise Exception("Got wrong response")
            break
        except Exception as e:
            if i < 3:
                print(f"Error: {e}, trying again...")
            else:
                raise e

    soup = bs.BeautifulSoup(data.text, 'lxml')
    elem = soup.find('script', attrs={'id': 'responsive-voice-js'})
    src = elem.get('src')
    query = urlparse(src).query
    query_elements = parse_qs(query)
    key = query_elements['key'][0]
    # print(key)
    return (key)


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


def GetMp3(word, filename):

    gender = "female"
    url = f'https://texttospeech.responsivevoice.org/v1/text:synthesize?lang=pl&engine=g1&name=&pitch=0.5&rate=0.5&volume=1&key={GetKey()}&gender={gender}&text={quote_plus(word)}'
    for i in range(4):
        try:
            data = requests.get(url, timeout=10)
            if data.ok == False:
                raise Exception("Got wrong response")
            else:
                break
        except Exception as e:
            if i < 3:
                print(f"Error: {e}, trying again...")
            else:
                raise e
    open(f'mp3/{filename}.mp3', 'wb').write(data.content)


def convert(filename):
    if os.path.exists("ogg/") == False:
        os.mkdir("ogg")
    os.system(
        f"ffmpeg -hide_banner -loglevel error -y -i mp3/{filename}.mp3 -ar 32000  -ab 48000 -acodec libvorbis ogg/{filename}.ogg")
    os.remove(f"mp3/{filename}.mp3")


def GetOgg(l):
    filename = l[1]
    word = l[0]
    # print(f"word: {word} | filename: {filename}")
    GetMp3(word, filename)
    convert(filename)


if __name__ == "__main__":
    if os.path.exists("mp3/") == True:
        shutil.rmtree('mp3')
    os.mkdir("mp3")
    slownik_list = []

    for slowo in list(slownik):
        slownik_list.append([slowo, TrimPl(slownik[slowo])])
    for slowo in slownik_auto:
        slownik_list.append([slowo, TrimPl(slowo)])

    with Pool(processes=len(slownik_list)) as p:
        with tqdm(total=len(slownik_list)) as pbar:
            for _ in p.imap_unordered(GetOgg, slownik_list):
                pbar.update()
    os.removedirs(f"mp3/")
