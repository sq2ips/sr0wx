# -*- coding: UTF-8 -*-
import logging
from datetime import datetime

from colorcodes import *

from sr0wx_module import SR0WXModule


class RadioactiveSq2ips(SR0WXModule):
    """Klasa pobierająca dane o promieniowaniu"""

    def __init__(self, language, service_url, sensor_id, service_url_sr):
        self.__service_url = service_url
        self.__sensor_id = sensor_id
        self.__service_url_sr = service_url_sr
        self.__language = language
        self.__logger = logging.getLogger(__name__)

    def request(self, url, id):
        self.__logger.info("::: Pobieranie danych...")

        data = self.requestData(url, self.__logger, 20, 3).json()
        
        dataw = ''
        try:
            for i in range(0, len(data["features"])):
                n = data["features"][i]["properties"]["id"]
                if n.find(id) == False:
                    dataw = data["features"][i]["properties"]
                    break
        except KeyError as e:
            if str(e) == "'features'":
                raise ValueError("Źródło zwraca puste dane.")
            else:
                raise KeyError(e)
        if dataw == "":
            raise KeyError("No sensor with id " + id)
        return dataw

    def request_sr(self, url):
        start = datetime.now().strftime("%Y-%m-%dT00:00:01.000Z")
        end = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        url = url + self.__sensor_id + f"?dateFrom={str(start)}&dateTo={str(end)}"
        self.__logger.info("::: Pobieranie średnich danych...")
        data = self.requestData(url, self.__logger, 10, 3).json()
        prs = 0
        try:
            for i in range(len(data)):
                prs += float(data[i]["moc_dawki"])
        except KeyError:
            raise ValueError("Nieprawidłowa odpowiedź serwera")
        if (prs == 0):
            self.__logger.warning("Nieprawidłowe dane!")
            return None
        else:
            return prs/len(data)

    def processData(self, data):
        # self.__logger.info(int(datetime.now().strftime("%d")) - int(datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%d")))
        if datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d") != datetime.now().strftime("%Y-%m-%d"):
            if ((int(datetime.now().strftime("%d")) - int(datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%d"))) > 1):
                raise ValueError("Dane są nieaktualne o więcej niż jeden dzień! oczekiwane: " + datetime.now().strftime(
                    "%Y-%m-%d") + ", otrzymane: " + datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d"))
            else:
                self.__logger.warning("Dane są nieaktualne o jeden dzień! oczekiwane: " + datetime.now().strftime(
                    "%Y-%m-%d") + ", otrzymane: " + datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d"))
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

    def get_data(self, connection):
        try:
            data = self.request(self.__service_url, self.__sensor_id)
            value = self.processData(data)
            value_sr = self.request_sr(self.__service_url_sr)
            self.__logger.info("Wartość przetwożona: " + str(value))
            va = int(value*100)
            # self.__logger.info(va)
            curentValue = " ".join(["wartos_c__aktualna", self.__language.read_decimal(
                va)+" ", "mikrosjiwerta", "na_godzine_"])
            if (value_sr != None):
                va_sr = int(round(value_sr, 2)*100)
                self.__logger.info(
                    "Średnia wartość przetwożona: " + str(va_sr/100))
                averageValue = " ".join(["s_rednia_wartos_c__dobowa", self.__language.read_decimal(
                    va_sr)+" ", "mikrosjiwerta", "na_godzine_"])
            else:
                averageValue = ""
                self.__logger.warning(
                    "Nieprawidłowe średnie dane, pomijanie...")
            message = " ".join(
                [" _ poziom_promieniowania _ ", curentValue, " _ ", averageValue, " _ "])
            connection.send({
                "message": message,
                "source": "paa",
            })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
