#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import logging
from operator import itemgetter

from colorcodes import *

from sr0wx_module import SR0WXModule

class ImgwPodestSq2ips(SR0WXModule):
    """Klasa pobierająca informacje stanie wody"""
    
    def __init__(self, language, service_url, wodowskazy, zlewnie, custom_names, custom_rivers, use_outdated, read_level, read_diff_level):
        self.__language = language
        self.__service_url = service_url
        self.__wodowskazy = wodowskazy
        self.__zlewnie = zlewnie
        self.__custom_names = custom_names
        self.__custom_rivers = custom_rivers
        self.__use_outdated = use_outdated
        self.__read_level = read_level
        self.__read_diff_level = read_diff_level
        self.__codes_all = ['below', 'low', 'medium', 'high', 'warning', 'alarm']
        self.__codes = {'alarm': "przekroczenia_stanow_alarmowych", 'warning': "przekroczenia_stanow_ostrzegawczych", 'below': "przekroczenia_absolutnych_stanow_minimalnych"}
        self.__codes_diff = {"alarm":"diffToAlarm", "warning":"diffToWarn", "below": "diffToAbsoluteMin"}
        self.__cm_units = ["centymetr", "centymetry", "centymetrow"]
        self.__logger = logging.getLogger(__name__)

    def toDict(self, data):
        stations = {}
        for station in data:
            stations[int(station["code"])] = station
        return(stations)
    
    def getStations(self, stations):
        stations_id = []
        # wodowskazy ze zlewni
        for id in stations:
            if stations[id]["catchment"] is not None:
                if int(stations[id]["catchment"]) in self.__zlewnie:
                    stations_id.append(id)
        if len(stations_id) == 0:
            self.__logger.warning(COLOR_WARNING + f"Brak wodowskazów w zlewni {self.__zlewnia}" + COLOR_ENDC)
        # wodowskazy z id
        for w in self.__wodowskazy:
            if w in stations:
                if w in stations_id:
                    self.__logger.warning(COLOR_WARNING + f"Wodowskaz o id {w} już na liście" + COLOR_ENDC)
                else:
                    stations_id.append(w)
            else:
                self.__logger.warning(COLOR_WARNING + f"wodowskaz o kodzie {w} nie istnieje" + COLOR_ENDC)
        return stations_id
    
    def checkStations(self, stations, stations_id):
        stations_checked = []
        for id in stations_id:
            station = stations[id]
            if "Outdated" in station["statusCode"]:
                if not self.__use_outdated:
                    self.__logger.warning(COLOR_WARNING + f"Zdezaktualizowany stan wody z wodowskazu {station['code']}, kod {station['statusCode']}, pomijanie..." + COLOR_ENDC)
                    continue
                else:
                    self.__logger.warning(COLOR_WARNING + f"Zdezaktualizowany stan wody z wodowskazu {station['code']}, kod {station['statusCode']}, używanie mimo to..." + COLOR_ENDC)
            elif station["statusCode"] in ['no-water-state-data', None]:
                self.__logger.warning(COLOR_WARNING + f"Nieznany stan wody z wodowskazu {station['code']}, kod {station['statusCode']}" + COLOR_ENDC)
            elif station["statusCode"] == "unknown":
                self.__logger.warning(COLOR_WARNING + f"Brak stanów charakterystycznych z wodowskazu {station['code']}" + COLOR_ENDC)
            else:
                if station["statusCode"] in self.__codes_all:
                    stations_checked.append(station)
                else:
                    self.__logger.warning(COLOR_WARNING + f"Nieprawidłowy kod, otrzymano {station['statusCode']}" + COLOR_ENDC)
        return stations_checked

    def groupStations(self, stations):
        stations_grouped = {}
        for station in stations:
            if station["statusCode"] not in stations_grouped:
                stations_grouped[station["statusCode"]] = []
            stations_grouped[station["statusCode"]] = stations_grouped[station["statusCode"]] + [station]
        
        stations_grouped_sorted = {}

        for code in self.__codes:
            if code in stations_grouped:
                stations_grouped_sorted[code] = sorted(stations_grouped[code], key = itemgetter("river"))
                self.__logger.info(f"Kod: {code}, liczba wodowskazów: {len(stations_grouped_sorted[code])}")

        return stations_grouped_sorted

    def getText(self, station):
        # odczytywanie danych jako tekstu z jedenego wodowskazu
        if station["isSeaStation"]:
            msg = " akwen "
        msg = " rzeka "

        river = " ".join(station["river"].split()[:-1])
        if river in self.__custom_rivers:
            msg += self.__custom_rivers[river]
        else:
            msg += self.__language.trim_pl(river)
        
        msg += " wodowskaz "
        if station["name"] in self.__custom_names:
            msg += self.__custom_names[station["name"]]
        else:
            msg += self.__language.trim_pl(station["name"])
        
        if station["currentState"] is not None and self.__read_level:
            msg += " poziom "
            msg += self.__language.read_number(int(station["currentState"]["value"]), units=self.__cm_units)

        if None not in [station[x] for x in self.__codes_diff.values()] and self.__read_diff_level:
            msg += " przekroczenie_o "
            msg += self.__language.read_number(abs(int(station[self.__codes_diff[station["statusCode"]]])), units=self.__cm_units)

        msg += " "
        
        if station["trend"] < 0:
            msg += "tendencja_spadkowa "
        elif station["trend"] == 0:
            pass
        elif station["trend"] > 0:
            msg += "tendencja_wzrostowa "
        
        msg += "_"
        return(msg)

    def get_data(self, connection):
        try:
            # pobieranie wszystkich danych
            data = self.requestData(self.__service_url, self.__logger, 15, 3).json()

            self.__logger.info("::: Przetwarzanie danych...")
            # konwersja na dict
            stations = self.toDict(data)
            if len(stations) == 0:
                raise Exception("Brak danych")
            
            self.__logger.info("::: Wyszukiwanie wybranych wodowskazów...")
            # wyszukiwanie wodowskazów na podstawie id i zlewni
            stations_id = self.getStations(stations)
            if len(stations_id) == 0:
                raise Exception("Brak wodowskazów na liście")

            self.__logger.info("::: Sprawdzanie danych z wodowskazów...")
            # sprawdzanie wodowskazów na podstawie kodów
            stations_checked = self.checkStations(stations, stations_id)
            if len(stations_checked) == 0:
                raise Exception("Brak funkcjonujących wodowskazów na liście")
            self.__logger.info(f"Liczba wszystkich wodowskazów: {len(stations)}")
            self.__logger.info(f"Liczba wybranych wodowskazów: {len(stations_id)}")
            self.__logger.info(f"Liczba poprawnych wybranych wodowskazów: {len(stations_checked)}")

            self.__logger.info("::: Grupowanie danych z wodowskazów...")
            # grupowanie wodowskazów na podstawie kodów
            stations_grouped = self.groupStations(stations_checked)

            message = "komunikat_hydrologiczny_imgw "
            for code in stations_grouped:
                if code in self.__codes:
                    message += " ".join([" _", self.__codes[code], "_"])
                    for station in stations_grouped[code]:
                        message += self.getText(station)

            if len(message.split()) > 1:
                connection.send({
                    "message": message,
                    "source": "hydro_imgw",
                })
            else:
                self.__logger.warning(COLOR_WARNING + "Brak przekroczeń wybranych stanów wody" + COLOR_ENDC)
                connection.send({
                    "message": None,
                    "source": "",
                })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
