import logging
import requests

from sr0wx_module import SR0WXModule


class AntistormSq2ips(SR0WXModule):
    """Moduł pobierający informacje o zagrożeniu burzowym"""

    def __init__(self, language, service_url, city_id):
        self.__service_url = service_url
        self.__language = language
        self.__city_id = str(city_id)
        self.__logger = logging.getLogger(__name__)

    def checkData(self, data):
        try:
            data = data.json()
            if {"m", "p_b", "t_b", "a_b", "s", "p_o", "t_o", "a_o"} <= data.keys():
                if set([type(d) is int for d in list(data.values())[1:]]) == {True}:
                    return data
                else:
                    raise Exception("Nieprawidłowy typ danych")
            else:
                raise Exception("Brak prawidłowych elementów w odpowiedzi serwera.")
        except requests.exceptions.JSONDecodeError:
            raise Exception("Odpowiedź nie jest w formacie JSON. Złe id?")

    def getProbability(self, value):
        return round((value / 255) * 100)

    def parseData(self, data):
        self.__logger.info(f"id: {self.__city_id}, miasto: {data['m']}")

        data_dict = {}
        if data["t_b"] < 255 and data["p_b"] > 0:
            data_dict["burza"] = [data["t_b"], self.getProbability(data["p_b"])]

        if data["t_o"] < 255 and data["p_o"] > 0:
            data_dict["deszcz"] = [data["t_o"], self.getProbability(data["p_o"])]

        return data_dict

    def get_data(self):
        self.__logger.info("::: Pobieranie danych radaru pogodowego...")
        url = "".join([self.__service_url, "?id=", self.__city_id])
        data = self.requestData(url, self.__logger)
        self.__logger.info("::: Przetwarzanie danych...")
        data = self.checkData(data)
        data_dict = self.parseData(data)
        if len(data_dict) > 0:
            message = "radar_pogodowy "
            for z in data_dict:
                message += " ".join(
                    [
                        "_",
                        "zjawisko",
                        z,
                        "czas_do_wysta_pienia",
                        self.__language.read_number(
                            data_dict[z][0],
                            units=(("minuta"), ("minuty"), ("minut")),
                        ),
                        "prawdopodobienstwo",
                        self.__language.read_percent(data_dict[z][1]),
                        "",
                    ]
                )
        else:
            message = "brak_ostrzez_en__radaru_pogodowego"
        return(
            {
                "message": message,
                "source": "antistorm_eu",
            }
        )
