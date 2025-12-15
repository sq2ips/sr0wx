import logging

from sr0wx_module import SR0WXModule

class AirGios(SR0WXModule):
    """Moduł pobierający info o zanieczyszczeniach powietrza z GIOŚ"""
    def __init__(self, language, service_url, uri_index, uri_all, sensor_id, onlyAlerts):
        self.__language = language
        self.__service_url = service_url
        self.__uri_index = uri_index
        self.__uri_all = uri_all
        self.__sensor_id = sensor_id
        self.__only_alerts = onlyAlerts

        self.__logger = logging.getLogger(__name__)

        self.__index_text = "Wartość indeksu dla wskaźnika "
        self.__index_values = {0: "poziom_bardzo_dobry", 1: "poziom_dobry", 2: "poziom_dostateczny", 3: "poziom_umiarkowany", 4: "poziom_zl_y", 5: "poziom_bardzo_zl_y"}
        self.__main_index_values = {0: "bardzo_dobry", 1: "dobry", 2: "dostateczny", 3: "umiarkowany", 4: "zl_y", 5: "bardzo_zl_y"}
        self.__sensors = {"SO2": "dwutlenek_siarki", "NO2": "dwutlenek_azotu", "PM10": "pyl__pm10", "PM2.5": "pyl__pm25", "O3": "ozon"}
    def processName(self, data):
        for station in data:
            if station["Identyfikator stacji"] == self.__sensor_id:
                return station["Nazwa stacji"]
        raise ValueError(f"Stacjia o ID {self.__sensor_id} nie istnieje.")
    def processIndex(self, data):
        values = {}
        for key in data.keys():
            if self.__index_text in key:
                sens = key.replace(self.__index_text, "")
                if data[key] == None:
                    self.__logger.warning(f"Brak danych o poziomie {sens} z czujnika")
                else:
                    values[sens] = data[key]
        
        return (data["Wartość indeksu"], values)
    def getText(self, values):
        message = ""
        for value in values.keys():
            if value in self.__sensors:
                message+=" ".join([self.__sensors[value], self.__index_values[values[value]], "_ "])
            else:
                self.__logger.warning(f"Pomiar {value} nieznany, pomijanie...")
        return message

    def get_data(self):
        uri_all = f"{self.__service_url}{self.__uri_all}"
        self.__logger.info("::: Pobieranie indeksu zanieczyszczenia powietrza...")
        data = self.requestData(uri_all, self.__logger, 10, 3).json()
        name = self.processName(data["Lista stacji pomiarowych"])

        self.__logger.info("::: Pobieranie nazw stacji...")
        uri_index = f"{self.__service_url}{self.__uri_index}{self.__sensor_id}"
        data = self.requestData(uri_index, self.__logger, 10, 3).json()

        self.__logger.info("::: Przetwarzanie danych...")
        main_index, indexes = self.processIndex(data["AqIndex"])

        message = "informacja_o_skaz_eniu_powietrza _ "
        message += "stacja_pomiarowa "
        message += self.__language.trim_pl(name)

        message += " _ stan_ogolny "
        message += self.__main_index_values[main_index]
        message += " _ "
        
        if self.__only_alerts and set(indexes.values()) == {0}:
            message += "brak_skaz_enia"
        else:
            message += self.getText(indexes)
        
        return(
            {
                "message": message,
                "source": "gios_",
            }
        )