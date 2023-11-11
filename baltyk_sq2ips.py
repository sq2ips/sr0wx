# -*- coding: UTF-8 -*-

import requests
from datetime import datetime

import logging
from sr0wx_module import SR0WXModule

class BaltykSq2ips(SR0WXModule):
    def __init__(self,service_url,region_id):
        self.__service_url = service_url
        self.__region_id = region_id
        self.__logger = logging.getLogger(__name__)
    def say_region(self):
        if self.__region_id=="WESTERN BALTIC":
           regionText="baltyku_w "
        if self.__region_id=="SOUTHERN BALTIC":
           regionText="baltyku_s "
        if self.__region_id=="SOUTHEASTERN BALTIC":
           regionText="baltyku_se "
        if self.__region_id=="CENTRAL BALTIC":
           regionText="baltyku_c "
        if self.__region_id=="NORTHERN BALTIC":
           regionText="baltyku_n "
        if self.__region_id=="POLISH COASTAL WATERS":
           regionText="baltyku_psb "
        return(regionText)

    def request(self, url):
        self.__logger.info("::: Pobieranie progozy dla bałtyku")
        r = requests.get(url=url)
        r.encoding = r.apparent_encoding #kodowanie polskich znaków
        data = r.json()
        return(data)
    def process(self, data):

        alert_level = data['regions'][self.__region_id]['alert_level']
        forecast_now = data['regions'][self.__region_id]['forecast_now']
        forecast_next = data['regions'][self.__region_id]['forecast_next']
        return [alert_level, forecast_now, forecast_next]
    def process_time(self, data):
        data_time = data['validity']
        months = {
            "1": " stycznia ", "2": " lutego ","3": " marca ",\
        "4":" kwietnia ","5":" maja ","6":" czerwca ","7":" lipca ",\
        "8":" sierpnia ","9":" września ","10":" października ",\
        "11":" listopada ","12":" grudnia "}
        od_text = data_time[11:13] + "_00 utc " + str(int(data_time[21:23])) + "-go" + months[str(int(data_time[24:26]))] + data_time[27:31]
        do_text = data_time[35:37] + "_00 utc " + str(int(data_time[45:47])) + "-go" + months[str(int(data_time[48:50]))] + data_time[51:55]
        print(od_text)
        print(do_text)
        return [od_text, do_text]
        
    def say_data(self, text):
        frazy = {
            "°C":" stopni_celsjusza",
        }
        frazy_regularne = ["w skali B","w porywach","w części","stan morza","temperatura około",
            "przelotny deszcz","wiatr z kierunków","deszcz ze śniegiem","krupa śnieżna",
            "zatoki gdańskiej","zatoki pomorskiej","możliwe burze","brak danych",
            "dobra do umiarkowanej","umiarkowana do słabej","ryzyko oblodzenia statków","przelotne opady",
            "temperatura powietrza",
        ]

        for i in frazy:
            try:
                text = text.replace(i, frazy[i])
            except KeyError:
                pass
        
        text=text.lower()
        
        for i in frazy_regularne:
            try:
                fraza=i.replace(" ","_").lower()
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
                .replace(":","")\
                .replace(",","")\
                .replace("."," _ ")
        return(text)
    def get_data(self):
        data = self.request(self.__service_url)
        datap = self.process(data)
        message = "prognoza_na_obszar " + self.say_region()
        time = self.process_time(data)
        message += "waz_na_od_godziny " + time[0] + " do " + time[1] + " "
        message += "baltyk_alert_"+datap[0]+" _ "
        message += self.say_data(datap[1])
        message += " _ prognoza_orientacyjna_12 "
        message += self.say_data(datap[2])
        return {
            "message": message,
            "source": "baltyk_pogodynka_pl",
        }
        


