# -*- coding: UTF-8 -*-

import logging
from sr0wx_module import SR0WXModule

from datetime import datetime

from colorcodes import *

class BaltykSq2ips(SR0WXModule):
    """Moduł pobierający komunikat o stanie i prognizie na obszar bałtyku"""
    def __init__(self, service_url, language, region_id):
        self.__service_url = service_url
        self.__language = language
        self.__region_id = region_id
        self.__logger = logging.getLogger(__name__)
        self.regions = {"WESTERN BALTIC": "baltyku_w", "SOUTHERN BALTIC":"baltyku_s", "SOUTHEASTERN BALTIC": "baltyku_se", "CENTRAL BALTIC": "baltyku_c", "NORTHERN BALTIC": "baltyku_n", "POLISH COASTAL WATERS": "baltyku_psb"}

    def request(self, url):
        r = self.requestData(url, self.__logger, 15, 3)
        r.encoding = r.apparent_encoding  # kodowanie polskich znaków
        data = r.json()
        return (data)

    def process(self, data):
        alert_level = data['regions'][self.__region_id]['alert_level']
        forecast_now = data['regions'][self.__region_id]['forecast_now']
        forecast_next = data['regions'][self.__region_id]['forecast_next']
        return [alert_level, forecast_now, forecast_next]

    def process_time(self, data):
        validity = data['validity']
        months = {
            1: " stycznia ", 2: " lutego ", 3: " marca ",
            4: " kwietnia ", 5: " maja ", 6: " czerwca ", 7: " lipca ",
            8: " sierpnia ", 9: " września ", 10: " października ",
            11: " listopada ", 12: " grudnia "}
        
        val = validity.split()
        
        if val[2] == "24:00":
            val[2] = "00:00"
        if val[6] == "24:00":
            val[6] = "00:00"
        
        od_date = datetime.strptime("".join([val[2], val[4]]), "%H:%M%d.%m.%Y")
        do_date = datetime.strptime("".join([val[6], val[8]]), "%H:%M%d.%m.%Y")
        
        if od_date.date() == do_date.date():
            od_text = "".join([od_date.strftime("%H"), "_00 "])
        else:
            od_text = "".join([od_date.strftime("%H"), "_00 utc ", str(od_date.day), "-go", months[od_date.month], str(od_date.year)])
        do_text = "".join([do_date.strftime("%H"), "_00 utc ", str(do_date.day), "-go", months[do_date.month], str(do_date.year)])

        return [od_text, do_text]

    def say_data(self, text):
        frazy = {
            "°C": " stopni_celsjusza",
            ", ": " oraz ",
            " -": " minus ",
        }
        frazy_regularne = ["w skali B", "w porywach", "w części", "stan morza", "temperatura około",
                           "przelotny deszcz", "wiatr z kierunków", "deszcz ze śniegiem", "krupa śnieżna",
                           "zatoki gdańskiej", "zatoki pomorskiej", "możliwe burze", "brak danych",
                           "dobra do umiarkowanej", "umiarkowana do słabej", "ryzyko oblodzenia statków", "przelotne opady",
                           "temperatura powietrza", "w cyrkulacji", "z kierunków", "w deszcz", "deszczu ze śniegiem", "lokalne burze","lokalne mgły","śnieg z deszczem", "burzowe porywy wiatru", "z przewagą"
                           ]

        for i in frazy:
            try:
                text = text.replace(i, frazy[i])
            except KeyError:
                pass

        text = text.lower()

        for i in frazy_regularne:
            try:
                fraza = i.replace(" ", "_").lower()
                text = text.replace(i.lower(), fraza)
            except KeyError:
                pass

        text = text\
            .replace(("ą"), "a_")\
            .replace(("ć"), "c_")\
            .replace(("ę"), "e_")\
            .replace(("ł"), "l_")\
            .replace(("ń"), "n_")\
            .replace(("ó"), "o_")\
            .replace(("ś"), "s_")\
            .replace(("ź"), "z_")\
            .replace(("ż"), "z_")\
            .replace(":", "")\
            .replace(",", "")\
            .replace(".", " _ ")
        return (text)

    def get_data(self, connection):
        try:
            self.__logger.info("::: Pobieranie komunikatu dla bałtyku...")
            data = self.request(self.__service_url)
            
            self.__logger.info("::: Przetwarzanie danych...")
            datap = self.process(data)
            time = self.process_time(data)

            message = " ".join(["prognoza_na_obszar",self.regions[self.__region_id], ""])

            message += " ".join(["waz_na_od_godziny", time[0], "do", time[1], "_ "])
            message += "".join(["baltyk_alert_",datap[0]," _ "])
            message += self.say_data(datap[1])
            message += " _ prognoza_orientacyjna_12 _ "
            message += self.say_data(datap[2])
            connection.send({
                            "message": message,
                            "source": "baltyk_imgw",
                        })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
