import logging
from datetime import datetime, timedelta

from sr0wx_module import SR0WXModule

# https://monitoring.paa.gov.pl/_api/maps/MapLayer/15d20873-f8a7-8899-5d69-960cc9ebbbb6/DetailsTable/f5af6ec4-d759-3163-344e-cbf147d28e28/Data/d2e87d20-28e2-47ea-860d-98a4e98d8726?dateFrom=2025-11-12T00:00:00.000Z&dateTo=2025-12-12T00:00:00.000Z
# https://monitoring.paa.gov.pl/_api/maps/MapLayer/15d20873-f8a7-8899-5d69-960cc9ebbbb6/DetailsTable/f5af6ec4-d759-3163-344e-cbf147d28e28/Data/d2e87d20-28e2-47ea-860d-98a4e98d8726?dateFrom=2025-12-12T00:00:00.000Z&dateTo=2025-12-12T00:00:00.000Z

class RadioactiveSq2ips(SR0WXModule):
    """Klasa pobierająca dane o promieniowaniu z PAA"""

    def __init__(self, language, service_url, sensor_id):
        self.__service_url = service_url
        self.__sensor_id = sensor_id
        self.__language = language
        self.__logger = logging.getLogger(__name__)

    def request(self):
        date = datetime.now().strftime("%Y-%m-%dT00:00:00.000Z")
        url = f"{self.__service_url}/{self.__sensor_id}?dateFrom={date}&dateTo={date}"
        self.__logger.info("::: Pobieranie danych...")
        data = self.requestData(url, self.__logger, 10, 3).json()

        return data

    def processData(self, data):
        datediff = datetime.now() - datetime.strptime(data["date_end_str"], "%Y-%m-%d %H:%M")

        if datediff < timedelta(days=1):
            pass
        elif datediff >= timedelta(days=1) and datediff < timedelta(days=2):
            self.__logger.warning(f"Dane są nieaktualne o jeden dzień, różnica czasów wynosi {datediff}")
        else:
            raise ValueError(f"Dane są nieaktualne o więcej niż jeden dzień, różnica czasów wynosi {datediff}")
        
        val = round(float(data["moc_dawki"]), 2)
        self.__logger.info(f"Wartość z czujnika, data: {str(datetime.strptime(data['date_end_str'], '%Y-%m-%d %H:%M'))}: {val}")
        return val
    
    def processDataSr(self, data):
        val_sr = 0
        for reading in data:
            val_sr+=round(float(reading["moc_dawki"]), 2)
        val_sr/=len(data)
        return(val_sr)


    def get_data(self):
        data = self.request()
        value = self.processData(data[0])
        value_sr = self.processDataSr(data)
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
            ["poziom_promieniowania _ ", curentValue, " _ ", averageValue, ""]
        )
        return(
            {
                "message": message,
                "source": "paa",
            }
        )