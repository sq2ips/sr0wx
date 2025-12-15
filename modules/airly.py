# by SQ9ATK
import logging
from datetime import datetime

from sr0wx_module import SR0WXModule
from config import LATITUDE, LONGITUDE

class Airly(SR0WXModule):
    """Moduł pobierający dane o zanieszczyszczeniach powietrza"""

    def __init__(
        self,
        language,
        api_key,
        service_url,
        mode,
        maxDistanceKM,
        installationId,
    ):
        self.__language = language
        self.__api_key = api_key
        self.__service_url = service_url
        self.__mode = mode
        self.__maxDistanceKM = str(maxDistanceKM)
        self.__installationId = str(installationId)
        self.__logger = logging.getLogger(__name__)
        self.__levels = {
            "VERY_LOW": "bardzo_dobry",
            "LOW": "dobry",
            "MEDIUM": "umiarkowany",
            "HIGH": "zly",
            "VERY_HIGH": "bardzo_zly",
        }

    def get_data(self):
        self.__logger.info("::: Pobieram dane o zanieczyszczeniach...")
        api_service_url = self.prepareApiServiceUrl()
        jsonData = self.getAirlyData(api_service_url)
        self.__logger.info("::: Przetwarzam dane...")
        message = "".join(
            [
                " informacja_o_skaz_eniu_powietrza ",
                # " _ ",
                # " godzina ",
                # self.getHour(),
                " _ stan_ogolny ",
                self.__levels[jsonData["current"]["indexes"][0]["level"]],
                self.getPollutionLevel(jsonData["current"]["values"]),
            ]
        )
        return(
            {
                "message": message,
                "source": "airly",
            }
        )

    def getPollutionLevel(self, json):
        message = ""
        for item in json:
            if item["name"] == "PM1":
                message += " _ pyl__zawieszony_pm1 "
                message += self.__language.read_micrograms(int(item["value"])) + " "

            if item["name"] == "PM25":
                message += " _ pyl__zawieszony_pm25 "
                message += self.__language.read_micrograms(int(item["value"])) + " "

            if item["name"] == "PM10":
                message += " _ pyl__zawieszony_pm10 "
                message += self.__language.read_micrograms(int(item["value"])) + " "
        return message

    def prepareApiServiceUrl(self):
        api_url = "https://airapi.airly.eu/v2/measurements/"
        urls = {
            "installationId": api_url
            + "installation?installationId="
            + self.__installationId,
            "point": api_url + "point?lat=" + str(LATITUDE) + "&lng=" + str(LONGITUDE),
            "nearest": api_url
            + "nearest?lat="
            + str(LATITUDE)
            + "&lng="
            + str(LONGITUDE)
            + "&maxDistanceKM="
            + self.__maxDistanceKM,
        }
        return urls[self.__mode]

    def getAirlyData(self, url):
        headers = {"Accept": "application/json", "apikey": self.__api_key}
        data = self.requestData(url, self.__logger, headers=headers)
        return data.json()

    def getHour(self):
        time = ":".join([str(datetime.now().hour), str(datetime.now().minute)])
        datetime_object = datetime.strptime(time, "%H:%M")
        msg = self.__language.read_datetime(datetime_object, "%H %M")
        return msg

    def getVisibility(self, value):
        msg = " _ "
        msg += " widocznosc " + self.__language.read_distance(int(value / 1000))
        return msg
