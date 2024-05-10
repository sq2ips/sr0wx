import requests
from datetime import datetime

from sr0wx_module import SR0WXModule
import logging
from colorcodes import *


class SpaceWeatherSq2ips(SR0WXModule):
    def __init__(self, urlG, urlR, urlS, geomagneticShort):
        self.__urlG = urlG
        self.__urlR = urlR
        self.__urlS = urlS
        self.__geomagneticShort = geomagneticShort
        self.__logger = logging.getLogger(__name__)

    def DownloadData(self, url):
        data = requests.get(url=url).json()
        return (data)

    def ProcessG(self, data):
        Kp = data[0].index("Kp")
        date = data[0].index("time_tag")
        del data[0]
        if self.__geomagneticShort:
            val = float(data[-1][Kp])
            self.__logger.info(f"Burze geomagnetyczne geomagnetyczne (chwilowe): Kp={val}, data: {data[-1][date]}")
        else:
            val_list = []
            for d in data:
                if (datetime.now() - datetime.strptime(d[date], "%Y-%m-%d %H:%M:%S.000")).days < 1:
                    val_list.append(float(d[Kp]))
            val = max(val_list)
            self.__logger.info(f"Burze geomagnetyczne geomagnetyczne: Kp={val}")

        if val < 5:
            message = None
        elif val >= 5 and val < 6:
            message = "mal_e"
        elif val >= 6 and val < 7:
            message = "duz_e"
        elif val >= 7 and val < 8:
            message = "bardzo_duz_e"
        elif val >= 8 and val < 9:
            message = "silne"
        elif val >= 9:
            message = "ekstremalne"

        return (message)

    def ProcessR(self, data):
        val_list = []
        for d in data:
            val_list.append(float(d["flux"]))
        val = max(val_list)
        self.__logger.info(f"zakłucenia radiowe {val}")
        if val < 10**-5:
            message = None
        elif val >= 10**-5 and val < 5*10**-5:
            message = "mal_e"
        elif val >= 5*10**-5 and val < 10**-4:
            message = "duz_e"
        elif val >= 10**-4 and val < 10**-3:
            message = "bardzo_duz_e"
        elif val >= 10**-3 and val < 2*10**-3:
            message = "silne"
        elif val >= 2*10**-3:
            message = "ekstremalne"

        return message

    def ProcessS(self, data):
        val_list = []
        for d in data:
            val_list.append(float(d["flux"]))
        val = max(val_list)
        self.__logger.info(f"Burze radiacyjne: {val}")

        if val < 10:
            message = None
        elif val >= 10 and val < 10**2:
            message = "mal_e"
        elif val >= 10**2 and val < 10**3:
            message = "duz_e"
        elif val >= 10**3 and val < 10**4:
            message = "bardzo_duz_e"
        elif val >= 10**4 and val < 10**5:
            message = "silne"
        elif val >= 10**5:
            message = "ekstremalne"
        return message
    def get_data(self, connection):
        try:
            self.__logger.info("::: Pobieranie danych")
            dataR = self.DownloadData(self.__urlR)
            dataG = self.DownloadData(self.__urlG)
            dataS = self.DownloadData(self.__urlS)

            self.__logger.info("::: Przetważanie danych")
            dG = self.ProcessG(dataG)
            dR = self.ProcessR(dataR)
            dS = self.ProcessS(dataS)

            if dG == None and dR == None and dS == None:
                message = "brak_alerto_w_pogody_kosmicznej"
            else:
                message = "alerty_pogody_kosmicznej _ "

                if dG != None:
                    message += dG
                    message += " burze_geomagnetyczne _ "

                if dR != None:
                    message += dR
                    message += " zakl_ucenia_radiowe _ "

                if dS != None:
                    message += dS
                    message += " burze_radiacyjne "

            connection.send({
                "message": message,
                "source": "nasa noaa",
            })
            return {
                "message": message,
                "source": "nasa noaa",
            }
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
        return (message)
