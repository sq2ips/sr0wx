import logging
from colorcodes import *
import requests

from sr0wx_module import SR0WXModule

class AntistormSq2ips(SR0WXModule):
    """Moduł pobierający informacje o zagrożeniu burzowym"""
    def __init__(self, language, service_url, id):
        self.__service_url = service_url
        self.__language = language
        self.__id = str(id)
        self.__logger = logging.getLogger(__name__)
    def checkData(self, data):
        try:
            if {"m", "p_b", "t_b", "a_b", "s", "p_o", "t_o", "a_o"} <= data.keys():
                if set([type(d) is int for d in list(data.values())[1:]]) is {True}:
                    return data.json()
                else:
                    raise Exception("Nieprawidłowy typ danych")
            else:
                raise Exception("Brak prawidłowych elementów w odpowiedzi serwera.")
        except requests.exceptions.JSONDecodeError:
            raise Exception("Odpowiedź nie jest w formacie JSON. Złe id?")
    def getProbability(self, value):
        return round((value/255)*100)
    def parseData(self, data):
        self.__logger.info(f"id: {self.__id}, miasto: {data['m']}")
        prob_storm = self.getProbability(data["p_b"])
        prob_rain = self.getProbability(data["p_o"])



    def get_data(self, connection):
        url = "".join([self.__service_url, "?id=", id])
        data = self.requestData(url, self.__logger, 15, 3)
        data = self.checkData(data)

        