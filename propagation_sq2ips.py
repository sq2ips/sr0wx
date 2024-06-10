import requests
from xml.etree import ElementTree

import logging
from colorcodes import *

from sr0wx_module import SR0WXModule

class PropagationSq2ips(SR0WXModule):
    """Klasa pobierająca informacje o propagacji"""
    def __init__(self, language, service_url, radioNoise):
        self.__service_url = service_url
        self.__language = language
        self.__radioNoise = radioNoise
        self.__logger = logging.getLogger(__name__)
    def DownloadData(self, url):
        self.__logger.info("::: Odpytuję adres: " + url)

        for i in range(4):
            try:
                response = requests.get(url, timeout=10)
                root = ElementTree.fromstring(response.content)
                if response.ok == False:
                    raise Exception("Non-OK response")
                elif root.tag == 'solar'.encode:
                    print(root.tag)
                    raise Exception("Nieprawidłowy nagłówek")
                break
            except Exception as e:
                if i < 3:
                    self.__logger.warning(COLOR_WARNING + f"Exception getting data:\n{e}\ntrying again..." + COLOR_ENDC)
                else:
                    raise e
        self.__logger.info("::: Otrzymano dane, nagłówek zgodny.")
        return root
    def process(self, root):
        self.__logger.info("::: Przetważanie danych...")
        conditions_day = {}
        conditions_night = {}
        for e in root[0]:
            if e.tag=='calculatedconditions':
                for band in e:
                    if band.attrib['time'] == 'day':
                        conditions_day[band.attrib['name']] = band.text
                    elif band.attrib['time'] == 'night':
                        conditions_night[band.attrib['name']] = band.text
            if e.tag == 'signalnoise':
                noise = e.text.split("-")
                for n in range(len(noise)):
                    noise[n] = noise[n][1:]
        return conditions_day, conditions_night, noise
    def getText(self, conditions):
        band_names = {"80m-40m":"80_i_40_metro_w","30m-20m":"20_metro_w","17m-15m":"15_metro_w","12m-10m":"10_metro_w"}
        conditions_names = {"Poor":"warunki_obnizone","Fair":"warunki_normalne","Good":"warunki_podwyzszone", "Band Closed":"pasmo_zamkniete"}
        text = " _ pasma _ "
        if len(list(set(list(conditions.values())))) == 1:
            text = "na_wszystkich_pasmach " + conditions_names[list(conditions.values())[0]]
        else:
            for band in conditions:
                text += band_names[band] + " " + conditions_names[conditions[band]] + " _ "
        return text
    def getNoise(self, noise):
        levels = {"0":"zero", "1":"jeden", "2":"dwa", "3":"trzy", "4":"cztery", "5":"pie_c_", "6":"szes_c_", "7":"siedem", "8":"osiem", "9":"dziewie_c_", "9+":"dziewie_c_+plus"}
        if len(noise) != 1 and len(noise) != 2:
            return None
        text = ""
        for n in range(len(noise)):
            noise[n] = levels[noise[n]]
        text += noise[0]
        if len(noise)==2:
            text += " do " + noise[1]
        return text

    def get_data(self, connection):
        try:
            root = self.DownloadData(self.__service_url)
            conditions_day, conditions_night, noise = self.process(root)
            text_day = self.getText(conditions_day)
            text_night = self.getText(conditions_night)
            noise_level = None
            if self.__radioNoise:
                noise_level = self.getNoise(noise)
            message = " ".join([
                " _ informacje_o_propagacji ",
                " _ dzien _ ",
                text_day,
                " _ noc _ ",
                text_night
            ])
            if self.__radioNoise:
                if noise_level == None:
                    self.__logger.warning(COLOR_WARNING + "No noise data" + COLOR_ENDC)
                else:
                    message += " _ poziom_zakl_ucen_ " + noise_level
            connection.send({
                "message": message,
                "source": "hamqsl",
            })
            return {
                "message": message,
                "source": "hamqsl",
            }
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
