import requests
from urllib.parse import urlparse, parse_qs, quote_plus
import urllib.request
import bs4 as bs
from multiprocessing import Pool
from tqdm import tqdm
import os

from slownik import slownik

def GetKey():
    url = 'https://responsivevoice.org/'

    data = requests.get(url).text
    soup = bs.BeautifulSoup(data,'lxml')
    elem = soup.find('script',attrs={'id' : 'responsive-voice-js'})
    src = elem.get('src')
    query = urlparse(src).query
    query_elements = parse_qs(query)
    key = query_elements['key'][0]
    #print(key)
    return(key)
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
                .replace(":","")\
                .replace(",","")\
                .replace("."," _ ")
    return(word)

def GetMp3(word, filename):
    if os.path.exists("mp3/") == False:
        os.mkdir("mp3")
    gender = "female"
    url = f'https://texttospeech.responsivevoice.org/v1/text:synthesize?lang=pl&engine=g1&name=&pitch=0.5&rate=0.5&volume=1&key={GetKey()}&gender={gender}&text={quote_plus(word)}'
    #print(url)
    data = requests.get(url)
    open(f'mp3/{filename}.mp3', 'wb').write(data.content)
def convert(filename):
    if os.path.exists("ogg/") == False:
        os.mkdir("ogg")
    os.system(f"ffmpeg -hide_banner -loglevel error -y -i mp3/{filename}.mp3 -ar 32000  -ab 48000 -acodec libvorbis ogg/{filename}.ogg")
    os.remove(f"mp3/{filename}.mp3")
def GetOgg(l):
    filename = l[0]
    word = l[1]
    GetMp3(word, filename)
    convert(filename)

if __name__ == "__main__":
    slownik_list = []

    for slowo in list(slownik):
        slownik_list.append([TrimPl(slowo), slownik[slowo]])

    with Pool(processes=len(slownik)) as p:
        with tqdm(total=len(slownik)) as pbar:
            for _ in p.imap_unordered(GetOgg, slownik_list):
                pbar.update()