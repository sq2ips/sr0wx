import logging

from sr0wx_module import SR0WXModule


class RadioactiveSq9atk(SR0WXModule):
    """Klasa pobierająca dane o promieniowaniu"""

    def __init__(self, language, service_url, sensor_id):
        self.__service_url = service_url
        self.__sensor_id = sensor_id
        self.__language = language
        self.__logger = logging.getLogger(__name__)

    def downloadFile(self, url):
        data = self.requestData(url, self.__logger)
        return data.text

    def isSensorMatchedById(self, sensorId, string):
        pos = string.find(("Details sensor " + str(sensorId)))
        return pos >= 0

    def isSensorRow(self, string):
        # na początku trzeba dodac spację bo inaczej find nie znajduje pierwszego znaku
        string = " " + string
        pos = string.find("Last sample")
        return pos >= 0

    def cleanUpString(self, string):
        string = string.replace("<br />", "<br/>")
        string = string.replace("<br>", "<br/>")
        string = string.replace("'", "")

        return string

    def extractSensorData(self, string):
        string = self.cleanUpString(string)
        tmpArr = string.split("<br/>")

        arrPart = tmpArr[0].split(".bindPopup(")
        tmpArr[0] = arrPart[1]

        tmpCurrent = tmpArr[0].split("Last sample: ")
        tmpAverage = tmpArr[2].split("24 hours average: ")

        current = tmpCurrent[1].split(" ")[0]
        average = tmpAverage[1].split(" ")[0]

        return {"current": current, "average": average}

    def getSensorData(self, html):
        dataArr = html.split("L.marker([")
        ret = {}
        for row in dataArr:
            if self.isSensorRow(row):
                if self.isSensorMatchedById(self.__sensor_id, row):
                    ret = self.extractSensorData(row)
        if ret == {}:
            raise ValueError(f"Sensor o id: {self.__sensor_id} nie istnieje")
        return ret

    def get_data(self):
        self.__logger.info("::: Pobieram dane...")
        html = self.downloadFile(self.__service_url)
        self.__logger.info("::: Przetwarzam dane...")
        data = self.getSensorData(html)
        msvCurrent = int(float(data["current"]) * 100)
        msvAverage = int(float(data["average"]) * 100)
        averageValue = " ".join(
            [
                "wartos_c__aktualna",
                self.__language.read_decimal(msvCurrent) + " ",
                "mikrosjiwerta",
                "na_godzine_",
            ]
        )
        currentValue = " ".join(
            [
                "s_rednia_wartos_c__dobowa",
                self.__language.read_decimal(msvAverage) + " ",
                "mikrosjiwerta",
                "na_godzine_",
            ]
        )
        message = " ".join(
            [
                "poziom_promieniowania _ ",
                averageValue,
                " _ ",
                currentValue,
            ]
        )
        return(
            {
                "message": message,
                "source": "radioactiveathome_org",
            }
        )