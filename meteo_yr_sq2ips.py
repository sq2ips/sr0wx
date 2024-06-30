#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import logging

from colorcodes import *

from sr0wx_module import SR0WXModule

from datetime import datetime

class MeteoYrSq2ips(SR0WXModule):
    """Klasa pobierająca informacje o pogodzie"""

    def __init__(self, language, service_url, id, current, nominal_validity):
        self.__service_url = service_url
        self.__language = language
        self.__id = id
        self.__current = current
        self.__nominal_validity = nominal_validity
        self.codes = {"lightrain":"lekka_ulewa", "partlycloudy":"czesciowe_zachmurzenie", "clearsky":"bezchmurnie", "fog":"mgla", "cloudy":"pochmurno", "rain":"opady_deszczu", "fair":"pochmurno", "rainshowers":"ulewa", "lightrainshowers":"lekka_ulewa", "heavyrain":"intensywne_opady_deszczu", "heavyrainshowers":"silna_ulewa", "rainshowersandthunder":"burza", "heavyrainshowersandthunder":"burza_z_silna__ulewa_", "heavyrainandthunder":"burza_z_intensywnymi_opadami_deszczu"}
        self.forecast_intervals = [0, 2]
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

        # stan pogody
        code = data["symbolCode"]["next1Hour"].split("_")
        code = code[0]
        msg += " ".join([self.codes[code], "_ "])

        # opady
        rain = round(data["precipitation"]["value"])
        if rain != 0:
            msg += " ".join([" opady", self.__language.read_precipitation(rain)])

        # temperatura
        temp = round(data["temperature"]["value"])
        temp_fl = round(data["temperature"]["feelsLike"])
        
        if temp != temp_fl:
            msg += " ".join([" temperatura", self.__language.read_number(temp)])
            msg += " ".join([" odczuwalna", self.__language.read_temperature(temp_fl)])
        else:
            msg += " ".join([" temperatura", self.__language.read_temperature(temp)])

        # wiatr
        wind_speed = round(data["wind"]["speed"]*3.6)
        wind_gust = round(data["wind"]["gust"]*3.6)
        wind_dir = data["wind"]["direction"]

        if wind_speed != wind_gust:
            msg += " ".join([" wiatr", self.getWind(wind_dir), self.__language.read_number(wind_speed)])
            msg += " ".join([" w_porywach", "do", self.__language.read_gust(wind_gust)])
        else:
            msg += " ".join([" wiatr", self.getWind(wind_dir), self.__language.read_speed(wind_speed), "kmph"])
        
        return msg

    def processValidity(self, date_start, date_end):
        ds = datetime.strptime(date_start, "%Y-%m-%dT%H:%M:%S%z")
        de = datetime.strptime(date_end, "%Y-%m-%dT%H:%M:%S%z")
        return (de-ds).seconds//3600

    def processForecast(self, data):
        if self.__nominal_validity:
            date_start = data["nominal_start"]
            date_end = data["nominal_end"]
        else:
            date_start = data["start"]
            date_end = data["end"]
        
        validity = self.processValidity(date_start, date_end)

        # prognoza na następne x godzin
        if validity == 1:
            msg = " _ prognoza_na_nastepna "
        else:
            msg = " _ prognoza_na_nastepne "
        msg += " ".join([self.__language.read_validity_hour(validity), "_ "])
        
        # stan pogody
        msg += " ".join([self.codes[data["symbolCode"]["next6Hours"].split("_")[0]], "_ "])
        
        # pokrywa chmur
        cloud = round(data["cloudCover"]["value"])
        msg += " ".join([" pokrywa_chmur", self.__language.read_percent(cloud)])

        # opady
        rain = round(data["precipitation"]["value"])
        if rain != 0:
            msg += " ".join([" opady", self.__language.read_precipitation(rain)])

        # temperatura
        temp = round(data["temperature"]["value"])
        temp_fl = round(data["feelsLike"]["value"])

        if temp != temp_fl:
            msg += " ".join([" _ temperatura", self.__language.read_number(temp)])
            msg += " ".join([" odczuwalna", self.__language.read_temperature(temp_fl)])
        else:
            msg += " ".join([" _ temperatura", self.__language.read_temperature(temp)])
        
        # wiatr
        wind_speed = round(data["wind"]["speed"]*3.6)
        wind_gust = round(data["wind"]["gust"]*3.6)
        wind_dir = data["wind"]["direction"]

        if wind_speed != wind_gust:
            msg += " ".join([" wiatr", self.getWind(wind_dir), self.__language.read_number(wind_speed)])
            msg += " ".join([" w_porywach", "do", self.__language.read_gust(wind_gust)])
        else:
            msg += " ".join([" wiatr", self.getWind(wind_dir), self.__language.read_speed(wind_speed), "kmph"])

        # ciśnienie
        pres = round(data["pressure"]["value"])
        msg += " ".join([" cisnienie", self.__language.read_pressure(pres)])
        
        # wilgotność
        hum = round(data["humidity"]["value"])
        msg += " ".join([" wilgotnosc", self.__language.read_percent(hum)])

        return msg

    def getForecast(self, data):
        msg = ""
        for i in self.forecast_intervals:
            msg += self.processForecast(data["longIntervals"][i])
        return msg

    def get_data(self, connection):
        try:
            message = "_ "
            self.__logger.info("::: Pobieranie danych pogodowych...")
            current, forecast = self.downloadData(self.__service_url, self.__id)
            self.__logger.info("::: Przetwarzanie danych...")
            if self.__current:
                message += " ".join([self.getCurrent(current), self.getForecast(forecast)])
            else:
                message += " ".join([self.getCurrent(current)])
            connection.send({
                "message": message,
                "source": "yr",
            })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())