from datetime import datetime

from sr0wx_module import SR0WXModule
import logging
from datetime import datetime

class SpaceWeatherSq2ips(SR0WXModule):
    """Moduł pobierający informacje o alertach pogody kosmicznej"""
    def __init__(self, language, urlG, urlR, urlS, geomagneticShort, radioNoise):
        self.__language = language
        self.__urlG = urlG
        self.__urlR = urlR
        self.__urlS = urlS
        self.__geomagneticShort = geomagneticShort
        self.__radioNoise = radioNoise
        self.__logger = logging.getLogger(__name__)

    def DownloadData(self, url):
        data = self.requestData(url, self.__logger, 10, 3)
        return data.json()

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
        self.__logger.info(f"zakłucenia jonosfery {val}")

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
            if (datetime.now() - datetime.strptime(d["time_tag"], "%Y-%m-%dT%H:%M:%SZ")).seconds // 3600 <= 6:
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
            if self.__radioNoise:
                dataR = self.DownloadData(self.__urlR)
            dataG = self.DownloadData(self.__urlG)
            dataS = self.DownloadData(self.__urlS)

            self.__logger.info("::: Przetważanie danych")
            dG = self.ProcessG(dataG)
            if self.__radioNoise:
                dR = self.ProcessR(dataR)
            else:
                dR = None
            dS = self.ProcessS(dataS)

            if dG is None and dR is None and dS is None:
                message = "brak_alerto_w_pogody_kosmicznej"
            else:
                message = "alerty_pogody_kosmicznej _ "

                if dG is not None:
                    message += dG
                    message += " burze_geomagnetyczne _ "

                if dR is not None:
                    message += dR
                    message += " zakl_ucenia_jonosfery _ "

                if dS is not None:
                    message += dS
                    message += " burze_radiacyjne "

            connection.send({
                "message": message,
                "source": "swpc",
            })
        except Exception as e:
            self.__logger.exception(f"Exception when running {self}: {e}")
            connection.send(dict())