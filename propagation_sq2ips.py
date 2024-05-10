import requests
from xml.etree import ElementTree

import logging
from colorcodes import *

from sr0wx_module import SR0WXModule

class PropagationSq2ips(SR0WXModule):
    """Klasa pobierająca informacje o propagacji"""
    def __init__(self, language, service_url):
        self.__service_url = service_url
        self.__language = language
        self.__logger = logging.getLogger(__name__)
    def DownloadData(self, url):
        self.__logger.info("::: Odpytuję adres: " + url)
        response = requests.get(url)
        root = ElementTree.fromstring(response.content)
        if root.tag == 'solar' and response.ok:
            self.__logger.info("::: Otrzymano dane, nagłówek zgodny.")
            return root
        else:
            raise Exception("Otrzymano nieprawidłową odpowiedź.")
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
        return conditions_day, conditions_night
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
    def get_data(self, connection):
        try:
            root = self.DownloadData(self.__service_url)
            conditions_day, conditions_night = self.process(root)
            text_day = self.getText(conditions_day)
            text_night = self.getText(conditions_night)
            message = " ".join([
                " _ informacje_o_propagacji ",
                " _ dzien _ ",
                text_day,
                "_ noc _",
                text_night
            ])
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
