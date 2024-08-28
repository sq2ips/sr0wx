import logging
from datetime import datetime, timedelta

from sr0wx_module import SR0WXModule


class RadioactiveSq2ips(SR0WXModule):
    """Klasa pobierająca dane o promieniowaniu z PAA"""

    def __init__(self, language, service_url, sensor_id, service_url_sr):
        self.__service_url = service_url
        self.__sensor_id = sensor_id
        self.__service_url_sr = service_url_sr
        self.__language = language
        self.__logger = logging.getLogger(__name__)

    def request(self, url, id):
        self.__logger.info("::: Pobieranie danych...")

        data = self.requestData(url, self.__logger, 20, 3).json()

        dataw = ""
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
        url = f"{url}{self.__sensor_id}?dateFrom={str(start)}&dateTo={str(end)}"
        self.__logger.info("::: Pobieranie średnich danych...")
        data = self.requestData(url, self.__logger, 10, 3).json()
        prs = 0
        try:
            for d in data:
                prs += float(d["moc_dawki"])
        except KeyError:
            raise ValueError("Nieprawidłowa odpowiedź serwera")
        if prs == 0:
            self.__logger.warning("Nieprawidłowe dane!")
            return None
        else:
            return prs / len(data)

    def processData(self, data):
        datediff = datetime.now() - datetime.strptime(data["tip_date"], "%Y-%m-%d %H:%M")

        if datediff < timedelta(days=1):
            pass
        elif datediff >= timedelta(days=1) and datediff < timedelta(days=2):
            self.__logger.warning(f"Dane są nieaktualne o jeden dzień, różnica czasów wynosi {datediff}")
        else:
            raise ValueError(f"Dane są nieaktualne o więcej niż jeden dzień, różnica czasów wynosi {datediff}")

        self.__logger.info(f"Wartość z czujnika {data['stacja']}, data: {str(datetime.strptime(data['tip_date'], '%Y-%m-%d %H:%M'))}: {data['tip_value']}")
        return round(float(data["tip_value"][0:5]), 2)

    def get_data(self):
        data = self.request(self.__service_url, self.__sensor_id)
        value = self.processData(data)
        value_sr = self.request_sr(self.__service_url_sr)
        self.__logger.info("Wartość przetwożona: " + str(value))
        va = round(value * 100)
        curentValue = " ".join(
            [
                "wartos_c__aktualna",
                self.__language.read_decimal(va) + " ",
                "mikrosjiwerta",
                "na_godzine_",
            ]
        )
        if value_sr is not None:
            va_sr = round(value_sr*100)
            self.__logger.info("Średnia wartość przetwożona: " + str(va_sr / 100))
            averageValue = " ".join(
                [
                    "s_rednia_wartos_c__dobowa",
                    self.__language.read_decimal(va_sr) + " ",
                    "mikrosjiwerta",
                    "na_godzine_",
                ]
            )
        else:
            averageValue = ""
            self.__logger.warning("Nieprawidłowe średnie dane, pomijanie...")
        message = " ".join(
            [" _ poziom_promieniowania _ ", curentValue, " _ ", averageValue, " _ "]
        )
        return(
            {
                "message": message,
                "source": "paa",
            }
        )