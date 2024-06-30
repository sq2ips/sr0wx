#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import logging

from colorcodes import *

from sr0wx_module import SR0WXModule

class MeteoYrSq2ips(SR0WXModule):
    """Klasa pobierająca informacje o pogodzie"""

    def __init__(self, language, service_url, id):
        self.__service_url = service_url
        self.__language = language
        self.__id = id
        self.codes = {"lightrain":"lekka_ulewa", "partlycloudy":"czesciowe_zachmurzenie", "clearsky":"bezchmurnie", "fog":"mgla", "cloudy":"pochmurno", "rain":"opady_deszczu", "fair":"pochmurno", "rainshowers":"ulewa", "lightrainshowers":"lekka_ulewa", "heavyrain":"intensywne_opady_deszczu", "heavyrainshowers":"silna_ulewa", "rainshowersandthunder":"burza"}
        self.__logger = logging.getLogger(__name__)

    def downloadData(self, service_url, id):
        links_url = service_url + "/api/v0/locations/" + id
        links = self.requestData(links_url, self.__logger, 10, 3)
        links_data = links.json()["_links"]
        
        url_current = service_url + links_data["currenthour"]["href"]
        url_forecast = service_url + links_data["forecast"]["href"]
        current = self.requestData(url_current, self.__logger, 10, 3)
        forecast = self.requestData(url_forecast, self.__logger, 10, 3)
        return (current.json(), forecast.json())
    
    def getWind(self, angle):
        msg = ''
        if 0 <= angle <= 23:
            msg += 'polnocny'
        elif 23 <= angle <= 67:
            msg += 'polnocno wschodni'
        elif 67 <= angle <= 112:
            msg += 'wschodni'
        elif 112 <= angle <= 157:
            msg += 'poludniowo wschodni'
        elif 157 <= angle <= 202:
            msg += 'poludniowy'
        elif 202 <= angle <= 247:
            msg += 'poludniowo zachodni'
        elif 247 <= angle <= 292:
            msg += 'zachodni'
        elif 292 <= angle <= 337:
            msg += 'polnocno zachodni'
        elif 337 <= angle <= 360:
            msg += 'polnocny'
        return msg

    def getCurrent(self, data):
        msg = ""

        code = data["symbolCode"]["next1Hour"].split("_")
        code = code[0]
        msg += " ".join([self.codes[code], "_ "])

        temp = data["temperature"]
        msg += " ".join(["temperatura", self.__language.read_temperature(round(temp["value"])), ""])
        if temp["value"] != temp["feelsLike"]:
            msg += " ".join(["odczuwalna", self.__language.read_temperature(round(temp["feelsLike"])), ""])

        wind = data["wind"]
        if round(wind["speed"]*3.6) != round(wind["gust"]*3.6):
            msg += " ".join(["wiatr", self.getWind(wind["direction"]), self.__language.read_number(round(wind["speed"]*3.6)), ""])
            msg += " ".join(["w_porywach", "do", self.__language.read_gust(round(wind["gust"]*3.6))])
        else:
            msg += " ".join([self.getWind(wind["direction"]), self.__language.read_speed(round(wind["speed"]*3.6), "kmph")])

        rain = data["precipitation"]["value"]
        if rain != 0:
            msg += " ".join([" opady", self.__language.read_precipitation(round(rain))])
        
        return msg
    
    #def processForecast(self, data):
    #    

    #def getForecast(self, data):
    #    pass

    def get_data(self, connection):
        try:
            message = "_ "
            self.__logger.info("::: Pobieranie danych pogodowych...")
            current, forecast = self.downloadData(self.__service_url, self.__id)
            self.__logger.info("::: Przetwarzanie danych...")
            message += self.getCurrent(current)
            connection.send({
                "message": message,
                "source": "yr",
            })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())