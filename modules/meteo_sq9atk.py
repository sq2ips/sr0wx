#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import re
import logging

from datetime import datetime

from bs4 import BeautifulSoup

from colorcodes import *

from sr0wx_module import SR0WXModule


class MeteoSq9atk(SR0WXModule):
    """Klasa pobierająca informacje o pogodzie"""

    def __init__(self, language, service_url, saytime, current):
        self.__service_url = service_url
        self.__language = language
        self.__current = current
        self.__saytime = saytime
        self.__logger = logging.getLogger(__name__)

    def downloadFile(self, url):
        data = self.requestData(url, self.__logger, 10, 3)
        return data.text
    def getHour(self):
        time = ":".join([str(datetime.now().hour), str(datetime.now().minute)])
        datetime_object = datetime.strptime(time, '%H:%M')
        time_words = self.__language.read_datetime(datetime_object, '%H %M')
        return time_words

    def parseForecastDesc(self, html):
        match = html.find_all("div", {"class": "forecastDesc"})[0].text
        return self.__language.rmv_pl_chars(match.strip().replace(" ", "_").replace(",", "_"))

    def parseTemperature(self, html):
        match = html.find_all("li")[0].find_all("span")[1]
        tempText = re.sub("[^0-9]", "", match.text)
        temp = self.__language.read_temperature(int(tempText))
        return temp

    def parseClouds(self, html):
        match = html.find_all("li")[2].find_all("span")[1]
        tempText = re.sub("[^0-9]", "", match.text)
        temp = self.__language.read_percent(int(tempText))
        return temp

    def parseWind(self, html):
        match = html.find_all("li")[3].find_all("span")[1]
        tempText = re.sub("[^0-9]", "", match.text)
        temp = self.__language.read_speed(int(tempText), "kmph")
        return temp

    def parsePressure(self, html):
        match = html.find_all("li")[5].find_all("span")[1]
        tempText = re.sub("[^0-9]", "", match.text)
        temp = self.__language.read_pressure(int(tempText))
        return temp

    def parseHumidity(self, html):
        match = html.find_all("li")[6].find_all("span")[1]
        tempText = re.sub("[^0-9]", "", match.text)
        temp = self.__language.read_percent(int(tempText))
        return temp

    def get_data(self, connection):
        try:
            rawHtml = self.downloadFile(self.__service_url)
            soup = BeautifulSoup(rawHtml, "lxml")
            
            self.__logger.info("::: Przetwarzam dane...\n")

            now = soup.find_all("li", {"id": "wts_p0"})[0]
            after = soup.find_all("li", {"id": "wts_p3"})[0]
            forecast = soup.find_all("li", {"id": "wts_p13"})[0]

            message = ""

            if self.__saytime:
                message += " ".join([
                    "stan_pogody_z_godziny", self.getHour(), " _ "
                ])
            if self.__current:
                message += " ".join([
                    self.parseForecastDesc(now), " _ "
                    "pokrywa_chmur", self.parseClouds(now), " _ "
                    "temperatura", self.parseTemperature(now),
                    "predkosc_wiatru", self.parseWind(now), " _ "
                    "cisnienie", self.parsePressure(now),
                    "wilgotnosc", self.parseHumidity(now),
                ])
            message += " ".join([

                " _ ", "prognoza_na_nastepne", "cztery", "godziny",
                " _ ", self.parseForecastDesc(after), " _ "
                "pokrywa_chmur", self.parseClouds(after), " _ "
                "temperatura", self.parseTemperature(after),
                "predkosc_wiatru", self.parseWind(after), " _ "
                "cisnienie", self.parsePressure(after),
                "wilgotnosc", self.parseHumidity(after),

                " _ ", "prognoza_na_nastepne", "dwanascie", "godzin",
                " _ ", self.parseForecastDesc(forecast), " _ "
                "pokrywa_chmur", self.parseClouds(forecast),  " _ "
                "temperatura", self.parseTemperature(forecast),
                "predkosc_wiatru", self.parseWind(forecast), " _ "
                "cisnienie", self.parsePressure(forecast),
                "wilgotnosc", self.parseHumidity(forecast), " _ "
            ])

            connection.send({
                "message": message,
                "source": "",
            })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
