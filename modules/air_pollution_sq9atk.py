import logging

# LISTA STACJI Z NUMERAMI
# http://api.gios.gov.pl/pjp-api/rest/station/findAll

from sr0wx_module import SR0WXModule


class AirPollutionSq9atk(SR0WXModule):
    """Moduł pobierający info o zanieczyszczeniach powietrza"""

    def __init__(self, language, service_url, city_id, station_id):
        self.__language = language
        self.__service_url = service_url
        self.__station_id = station_id
        self.__logger = logging.getLogger(__name__)

        self.__stations_url = "station/findAll/"
        self.__station_url = "station/sensors/"
        self.__sensor_url = "data/getData/"
        self.__index_url = "aqindex/getIndex/"

    def getJson(self, url):
        data = self.requestData(url, self.__logger)
        return data.json()

    def getStationName(self):
        url = self.__service_url + self.__stations_url
        stationName = ""
        for station in self.getJson(url):
            if station["id"] == self.__station_id:
                stationName = station["stationName"]
        return stationName

    def getSensorValue(self, sensorId):
        url = self.__service_url + self.__sensor_url + str(sensorId)
        self.__logger.info("::: Pobieram dane o zanieczyszczeniach...")
        data = self.getJson(url)
        if data["values"][0]["value"] is not None:  # czasem tu schodzi null
            value = data["values"][0]["value"]
        else:
            value = data["values"][1]["value"]
        return [data["key"], int(value)]

    def getLevelIndexData(self):
        url = self.__service_url + self.__index_url + str(self.__station_id)
        return self.getJson(url)

    def getSensorsData(self):
        url = self.__service_url + self.__station_url + str(self.__station_id)
        levelIndexArray = self.getLevelIndexData()
        sensors = []
        for row in self.getJson(url):
            value = self.getSensorValue(row["id"])
            if value[1] > 1:  # czasem tu schodzi none
                qualityIndexName = self.__language.trim_pl(value[0]) + "IndexLevel"
                if qualityIndexName in levelIndexArray:
                    index = levelIndexArray[qualityIndexName]["indexLevelName"]
                else:
                    index = "empty"
                sensors.append(
                    [
                        row["id"],
                        qualityIndexName,
                        self.__language.trim_pl(row["param"]["paramName"]),
                        value[1],
                        self.__language.trim_pl(index),
                    ]
                )
        if len(sensors) > 0:
            return sensors
        else:
            raise Exception("Brak danych pomiarowych")

    def prepareMessage(self, data):
        levels = {
            "bardzo_dobry": "poziom_bardzo_dobry _ ",
            "dobry": "poziom_dobry _ ",
            "dostateczny": "poziom_dostateczny _ ",
            "umiarkowany": "poziom_umiarkowany _ ",
            "zly": "poziom_zl_y _ ",  # ten jest chyba nieuzywany
            "zl_y": "poziom_zl_y _ ",
            "bardzo_zly": "poziom_bardzo_zl_y _ ",  # ten też jest chyba nieuzywany
            "bardzo_zl_y": "poziom_bardzo_zl_y _ ",
            "empty": "",
        }
        message = " "
        for row in data:
            message += " " + row[2]
            message += " " + self.__language.read_micrograms(int(row[3]))
            message += " " + levels[row[4]]
        return message

    def get_data(self):
        self.__logger.info("::: Pobieram informacje o skażeniu powietrza...")
        sensorsData = self.getSensorsData()
        self.__logger.info("::: Przetwarzam dane...")
        valuesMessage = self.prepareMessage(sensorsData)
        
        message = " ".join(["informacja_o_skaz_eniu_powietrza", "stacja_pomiarowa", self.__language.trim_pl(self.getStationName()), "_", valuesMessage])
        return(
            {
                "message": message,
                "source": "gios",
            }
        )