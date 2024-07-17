#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import logging

from colorcodes import *

from sr0wx_module import SR0WXModule

from datetime import datetime, timedelta

class MeteoYrSq2ips(SR0WXModule):
    """Klasa pobierająca informacje o pogodzie z yr.no"""

    def __init__(self, language, service_url, id, current, intervals):
        self.__service_url = service_url
        self.__language = language
        self.__id = id
        self.__current = current
        self.__intervals = intervals
        self.codes = {"lightrain":"lekkie_opady_deszczu", "partlycloudy":"czesciowe_zachmurzenie", "clearsky":"bezchmurnie", "fog":"mgla", "cloudy":"pochmurno", "rain":"opady_deszczu", "fair":"lekkie_zachmurzenie", "rainshowers":"ulewa", "lightrainshowers":"lekka_ulewa", "heavyrain":"intensywne_opady_deszczu", "heavyrainshowers":"silna_ulewa", "rainshowersandthunder":"burza", "heavyrainshowersandthunder":"burza_z_silna__ulewa_", "heavyrainandthunder":"burza_z_intensywnymi_opadami_deszczu"}
        self.__logger = logging.getLogger(__name__)

    def downloadData(self, service_url, id):
        links_url = "/".join([service_url,"api/v0/locations",id])
        links = self.requestData(links_url, self.__logger, 10, 3)
        links_data = links.json()["_links"]
        
        url_current = "".join([service_url,links_data["currenthour"]["href"]])
        url_forecast = "".join([service_url,links_data["forecast"]["href"]])
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

    def processValidity(self, date_end):
        #ds = datetime.strptime(date_start[:-6], "%Y-%m-%dT%H:%M:%S")
        de = datetime.strptime(date_end[:-6], "%Y-%m-%dT%H:%M:%S")
        return de-datetime.now()

    def processForecast(self, data):
        #date_start = data["start"]
        date_end = data["end"]
        
        validity = self.processValidity(date_end).seconds//3600

        # prognoza na następne x godzin
        if validity == 1:
            msg = " _ prognoza_na_nastepna "
        else:
            msg = " _ prognoza_na_nastepne "
        msg += " ".join([self.__language.read_validity_hour(validity), "_ "])
        
        # stan pogody
        msg += " ".join([self.codes[data["symbolCode"]["next1Hour"].split("_")[0]], "_ "])
        
        # pokrywa chmur
        cloud = round(data["cloudCover"]["value"])
        if cloud != 0:
            msg += " ".join([" pokrywa_chmur", self.__language.read_percent(cloud)])

        # opady
        rain = round(data["precipitation"]["value"])
        if rain != 0:
            msg += " ".join([" _ opady", self.__language.read_precipitation(rain)])

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
        #pres = round(data["pressure"]["value"])
        #msg += " ".join([" _ cisnienie", self.__language.read_pressure(pres)])
        
        # wilgotność
        #hum = round(data["humidity"]["value"])
        #msg += " ".join([" wilgotnosc", self.__language.read_percent(hum)])

        return msg

    def getInterval(self, data, time):
        intervals = []
        for i in data["longIntervals"]:
            intervals.append(abs(self.processValidity(i["end"])-time))
        self.__logger.info(f"::: Wartość interwału na {time} godzin: {min(intervals)+time}, indeks {intervals.index(min(intervals))}")
        return intervals.index(min(intervals))

    def getForecast(self, data):
        msg = ""
        intervals = []
        for i in self.__intervals:
            intervals.append(self.getInterval(data, timedelta(hours=i)))
        for i in intervals:
            msg += self.processForecast(data["longIntervals"][i])
        return msg

    def get_data(self, connection):
        try:
            message = "aktualny_stan_pogody _ "
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