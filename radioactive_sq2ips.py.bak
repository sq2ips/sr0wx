# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import logging

import requests
import json
from datetime import datetime

from sr0wx_module import SR0WXModule


class RadioactiveSq2ips(SR0WXModule):
    """Klasa pobierająca dane o promieniowaniu"""

    def __init__(self, language, service_url, sensor_id):
        self.__service_url = service_url
        self.__sensor_id = sensor_id
        self.__language = language
        self.__logger = logging.getLogger(__name__)

    def request(self, url, id):
        self.__logger.info("Pobieranie danych...")
        data = requests.get(url).json()
        dataw=''
        try:
            for i in range(0, len(data["features"])):
                n = data["features"][i]["properties"]["id"]
                if n.find(id) == False:
                    dataw = data["features"][i]["properties"]
                    break
        except KeyError as e:
            if str(e) == "'features'":
                raise ValueError("Źródło zwraca puste dane")
            else:
                raise KeyError(e)
        if dataw == "":
            raise KeyError("No sensor with id " + id)
        return dataw

    def processData(self, data):
        self.__logger.info(int(datetime.now().strftime("%d")) - int(datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%d")))
        if datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d") != datetime.now().strftime("%Y-%m-%d"):
            if((int(datetime.now().strftime("%d")) - int(datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%d"))) > 1):
                raise ValueError("Dane są nieaktualne o więcej niż jeden dzień! oczekiwane: " + datetime.now().strftime("%Y-%m-%d") + ", otrzymane: " + datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d"))
            else:
                self.__logger.warning("Dane są nieaktualne o jeden dzień! oczekiwane: " + datetime.now().strftime("%Y-%m-%d") + ", otrzymane: " + datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d"))
        value = data["tip_value"]
        self.__logger.info(
            "Wartość z czujnika "
            + data["stacja"]
            + ", data: "
            + str(datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M"))
            + ": "
            + data["tip_value"]
        )
        v = round(float(data['tip_value'][0:5]), 2)
        return v
    def get_data(self):
        data = self.request(self.__service_url, self.__sensor_id)
        value = self.processData(data)
        self.__logger.info("Wartość przetwożona: " + str(value))
        va=int(value*100)
        self.__logger.info(va)
        curentValue = " ".join(["wartos_c__aktualna",self.__language.read_decimal( va )+" ","mikrosjiwerta","na_godzine_"])
        message = " ".join([" _ poziom_promieniowania _ ", curentValue, " _ "])
        return {
            "message": message,
            "source": "",
        }
