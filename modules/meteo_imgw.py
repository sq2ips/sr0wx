# by SQ2IPS
import logging

from sr0wx_module import SR0WXModule

from math import sqrt

class MeteoImgw(SR0WXModule):
    """Klasa pobierająca informacje o aktualnej pogodzie z """
    def __init__(self, language, service_url, lat, lon, station_name):
        self.__service_url = service_url
        self.__language = language
        self.__lat = lat
        self.__lon = lon
        self.__station_name = station_name
        self.__logger = logging.getLogger(__name__)
    
    def getClosestStation(self, stations):
        dist = []
        for station in stations:
            dist.append(sqrt((self.__lat-float(station["lat"]))**2+(self.__lon-float(station["lon"]))**2))
        station = stations[dist.index(min(dist))]
        self.__logger.info(f'Wybrano stację {station["nazwa_stacji"]}')
        return station
    
    def extractData(self, station):
        #try:
        #    temp = round(float(station["temperatura_powietrza"]))
        #    wind = round(float(station["wiatr_srednia_predkosc"])*3.6)
        #    wind_gust = round(float(station["wiatr_poryw_10min"])*3.6)
        #    wind_dir = int(station["wiatr_kierunek"])
        #    hum = int(station["wilgotnosc_wzgledna"])
        pass


    def prepareText(self, station):
        message = ""

        message+= "temperatura "
        #message+= self.__language.read_temperature(round())
    
    def get_data(self):
        self.__logger.info("::: Pobieranie aktualnych danych pogodowych...")
        stations = self.requestData(self.__service_url, self.__logger, 15, 3).json()
        station = self.getClosestStation(stations)
        print(station)
