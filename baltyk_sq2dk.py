#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

# additional libraries required: tqdm and pydub

import os.path
from tqdm import tqdm
import requests
import urllib.request
import urllib.error
import urllib.parse
import re
import logging
import pytz
import os
import glob

# from pydub import AudioSegment
from datetime import datetime
from sr0wx_module import SR0WXModule
from responsive_voice import ResponsiveVoice

# engine = ResponsiveVoice(lang="pl-PL", gender=ResponsiveVoice.FEMALE)

# kolejność działania
# - załaduj prognozę z www
# - w pierwszej części okreśł ważność prognozy: prognoza wydawana co 6 godzin UTC - 0,6,12,18
# - wynajdź daty i zamień je na format mówiony
# - wynajdź początek prognozy na region
# -


class BaltykSq2dk(SR0WXModule):
    """Klasa pobierająca dane o stanie morza"""

    def __init__(self, language, service_url, region_id):
        self.__service_url = service_url
        self.__region_id = region_id
        self.__language = language
        self.__logger = logging.getLogger(__name__)

    def downloadFile(self, url):
        webFile = urllib.request.urlopen(url)
        return webFile.read()

    def validityText(self, string):
        pos1 = string.find("validity".encode())
        pos2 = string.find('"'.encode(), pos1+11, pos1+255)
        valiString = string[11+pos1:pos2]
        valiString = valiString.replace(
            "Ważność od".encode(), "waz_na_od_godziny".encode())
        firstDatePos = valiString.find("UTC".encode(), 0)+4
        firstDotPos = valiString.find(".".encode(), firstDatePos)
        secondDotPos = valiString.find(".".encode(), firstDotPos+1)
        firstDay = valiString[firstDatePos:firstDotPos]
        firstMonth = valiString[firstDotPos+1:secondDotPos]
        firstYear = valiString[secondDotPos+1:secondDotPos+5]

        secondDatePos = valiString.find("UTC".encode(), firstDatePos)+4
        thirdDotPos = valiString.find(".".encode(), secondDatePos)
        fourthDotPos = valiString.find(".".encode(), thirdDotPos+1)
        secondDay = valiString[secondDatePos:thirdDotPos]
        secondMonth = valiString[thirdDotPos+1:fourthDotPos]
        secondYear = valiString[fourthDotPos+1:fourthDotPos+5]

        firstDay = str(int(firstDay))
        if int(firstDay) > 19:
            firDay = str(int(int(firstDay)/10)*10)+"-go "
            if (int(firstDay)-(int(int(firstDay)/10)*10)) > 0:
                firstDay = firDay + \
                    str(int(firstDay)-(int(int(firstDay)/10)*10))+"-go"
            else:
                firstDay = firDay
        else:
            firstDay = firstDay+"-go"

        secondDay = str(int(secondDay))
        if int(secondDay) > 19:
            secDay = str(int(int(secondDay)/10)*10)+"-go "
            if (int(secondDay)-(int(int(secondDay)/10)*10)) > 0:
                secondDay = secDay + \
                    str(int(secondDay)-(int(int(secondDay)/10)*10))+"-go"
            else:
                secondDay = secDay
        else:
            secondDay = secondDay+"-go"

        monthVer = {("1", " stycznia "), ("2", " lutego "), ("3", " marca "),
                    ("4", " kwietnia "), ("5", " maja "), ("6",
                                                           " czerwca "), ("7", " lipca "),
                    ("8", " sierpnia "), ("9",
                                          " września "), ("10", " października "),
                    ("11", " listopada "), ("12", " grudnia ")}

        for k, v in monthVer:
            firstMonth = firstMonth.replace(k.encode(), v.encode())
        for k, v in monthVer:
            secondMonth = secondMonth.replace(k.encode(), v.encode())
        space = " ".encode()
        return valiString[0:firstDatePos]+space+firstDay.encode()+space+firstMonth+space+firstYear+space+valiString[secondDotPos+5:secondDatePos]+secondDay.encode()+space+secondMonth+space+secondYear

    def regionPos(self, string):
        return string.find(self.__region_id.encode(), 0)+len(self.__region_id)+1

    def alertDescr(self, string):
        pos1 = string.find("alert_level".encode(), self.regionPos(string))
        pos2 = string.find('"'.encode(), pos1+14, pos1+16)
        alert_level = string[pos1+14:pos2]
        alert_level = alert_level.replace('"'.encode(), ''.encode())
        return "baltyk_alert_".encode()+alert_level

    def forecast_now(self, string):
        pos1 = string.find("forecast_now".encode(), self.regionPos(string))
        pos2 = string.find('"'.encode(), pos1+15, pos1+1000)

        return string[pos1+15:pos2]

    def forecast_next(self, string):
        posfn1 = string.find("forecast_next".encode(), self.regionPos(string))
        if posfn1 > 0:
            posfn2 = string.find('"'.encode(), posfn1+16, posfn1+1000)
        else:
            posfn2 = 0
        forcnext12 = string[posfn1+16:posfn2]

        return forcnext12

    def polSign(self, value):
        return value\
            .replace(("ą"), "a_").replace(("Ą"), "a_")\
            .replace(("ć"), "c_").replace(("Ć"), "c_")\
            .replace(("ę"), "e_").replace(("Ę"), "e_")\
            .replace(("ł"), "l_").replace(("Ł"), "l_")\
            .replace(("ń"), "n_").replace(("Ń"), "n_")\
            .replace(("ó"), "o_").replace(("Ó"), "o_")\
            .replace(("ś"), "s_").replace(("Ś"), "s_")\
            .replace(("ź"), "z_").replace(("Ź"), "z_")\
            .replace(("ż"), "z_").replace(("Ż"), "z_")\
            .replace(":", "_")\
            .replace(",", "")\
            .replace(".", " _ ")\
            .lower()

    def checkFrazy(self, string):
        plik_frazy_adr = "./baltyk_frazy.txt"
        self.__logger.info(":-sprawdzam frazy "+plik_frazy_adr)
        plik_frazy = open(plik_frazy_adr, "r")
        frazy = plik_frazy.read()
        frazy = frazy.lower()
        frazy = frazy.replace("\r", "")
        prog_spl = frazy.split("\n")

        for wyrazy in prog_spl:
            fraza = self.polSign(wyrazy.strip())
            fraza = fraza.replace(" ", "_")
            string = string.replace(wyrazy.strip(), fraza)
        return string

    def getMissingSample(self, string):
        engine = ResponsiveVoice(lang="pl-PL", gender=ResponsiveVoice.FEMALE)
        # set paths to folders
        oggpath = "./pl_google/"
        mp3path = "./pl_google/mp3/"
        samplename = self.polSign(string.strip())

        # get mp3 sample file
        pat = mp3path+samplename+".mp3"
        self.__logger.info(string)
        self.__logger.info(pat)
        # , lang=None, pitch=None, rate=None, vol=None, gender=None)
        engine.get_mp3(string, pat)

        # convert mp3 sample to oog -   done by separate rutine - all files at once
        mp3name = ((mp3path+samplename+".mp3"))
        oggname = ((oggpath+samplename+".ogg"))
        os.system("ffmpeg -hide_banner -y -i " + mp3name +
                  " -ar 32000 -ab 48000 -acodec libvorbis " + oggname)

        # song = AudioSegment.from_mp3(mp3path+samplename+".mp3")
        # song.export(oggpath+samplename+".ogg", format="ogg",parameters=["-ar", "16000"])

        self.__logger.info(":::  == zaladowalem brakujacy sampel: "+string)

    def checkForMissingSamples(self, string):

        string = string.replace(".", "")
        string = string.replace(",", "")
        prog_spl = string.split(" ")
        for wyrazy in prog_spl:
            plik_naz = self.polSign(wyrazy)
            if not os.path.isfile("./pl_google/"+plik_naz+".ogg"):
                if wyrazy.strip() > "":
                    self.getMissingSample(wyrazy.strip())

    def covert_all_mp3(self):
        b = 0
        a = (glob.glob("./pl_google/mp3/*.mp3"))
        c = len(a)
        while b < len(a):
            print((str(b/len(a)*100) + "%"))
            wyj = a[b].replace('.mp3', '') + ".ogg"
            self.__logger.info(("--- konwertowanie " + a[b] + " na " + wyj))
            os.system("ffmpeg -hide_banner -y -i " +
                      a[b] + " -ar 32000  -ab 48000 -acodec libvorbis " + wyj)
            b = b + 1
        # os.system("cp *.ogg ..")
        # os.system("mv *.ogg old")
        # move all new ogg files to higher folder
        os.system("mv *.ogg ..")
        # purge all mp3 files, otherwise they will be converted again next time
        os.system("rm *.mp3")

    def get_data(self):
        self.__logger.info("::: Pobieram dane...")
        html = self.downloadFile(self.__service_url)

        self.__logger.info("::: Przetwarzam dane...\n")
        data = "prognoza_na_obszar "
        if self.__region_id == "WESTERN BALTIC":
            regionText = "baltyku_w "
        if self.__region_id == "SOUTHERN BALTIC":
            regionText = "baltyku_s "
        if self.__region_id == "SOUTHEASTERN BALTIC":
            regionText = "baltyku_se "
        if self.__region_id == "CENTRAL BALTIC":
            regionText = "baltyku_c "
        if self.__region_id == "NORTHERN BALTIC":
            regionText = "baltyku_n "
        if self.__region_id == "POLISH COASTAL WATERS":
            regionText = "baltyku_psb "
        data = data+regionText
        validText = self.validityText(html)
        data = data+validText.decode()+" "+self.alertDescr(html).decode()+".   "
        data = data+self.forecast_now(html).decode()
        data12 = self.forecast_next(html)
        if data12 > "".encode():
            data = data+" prognoza_orientacyjna_12 "
        data = data+self.forecast_next(html).decode()

        data = data.lower()
        # data=data.replace("."," _ ")
        data = data.replace("°c", " stopni_celsjusza")

        data = self.checkFrazy(data)

        self.checkForMissingSamples(data)

        # self.convert_all_mp3()

        # data=data.replace("°c"," stopni_celsjusza")
        data = data.replace(" i ", " _i ")
        data = data.replace(" w ", " _w ")
        data = data.replace(" z ", " _z ")

        data = self.polSign(data)

        return {
            "message": data,
            "source": "baltyk_pogodynka_pl",
        }
