import requests
import logging

from sr0wx_module import SR0WXModule

class MeteoAlarmSq2ips(SR0WXModule):
    def __init__(self, city, start_message):
        self.__start_message=start_message
        self.__city = city
        self.__logger = logging.getLogger(__name__)
        self.codes = {"SW": "silnym_wiatrem","ID": "intensywnymi_opadami_deszczu","OS": "opadami_sniegu","IS": "intensywnymi_opadami_sniegu","OM": "opadami_marznacymi","ZZ": "zawiejami_lub_zamieciam_snieznymi","OB": "oblodzeniem","PR": "przymrozkami","RO": "roztopami","UP": "upalem","MR": "silnym_mrozem","MG": "gesta_mgla","MS": "mgla_intensywnie_osadzajaca_szadz","BU": "burzami","BG": "burzami_z_gradem","DB": "silnym_deszczem_z_burzami","GWSW": "gwaltownymi_wzrostami_stanow_wody","W_PSA": "wezbraniem_z_przekroczeniem_stanow_alarmowych","W_PSO": "wezbraniem_z_przekroczeniem_stanow_ostrzegawczych","SH": "susza_hydrologiczna"}
        self.stopnie = {"1":"pierwszego","2":"drugiego","3":"trzeciego"}
        self.procent = {10:"dziesiec",20:"dwadziescia",30:"trzydziesci",40:"czterdziesci",50:"piedziesiat",60:"szezdziesiat",70:"siedemdziesiat",80:"osiemdziesiat",90:"dziewiedziesiat",100:"sto"}
    def downloadData(self):
        urlap = "https://meteo.imgw.pl/api/meteo/messages/v1/prog/latest/pronieb/ALL"
        urln = "https://meteo.imgw.pl/dyn/data/out1proc.json?v=1.2"
        urla = "https://meteo.imgw.pl/api/meteo/messages/v1/osmet/latest/osmet-teryt?lc="
        self.__logger.info("::: Pobieranie ostrzeżeń meteorologicznych...")
        alerts = requests.get(url = urla).json()
        names = requests.get(url = urln).json()
        return(alerts, names)
    def process(self):
        data = self.downloadData()
        alerts = data[0]
        names = data[1]
        self.__logger.info("::: Przetważanie danych...")
        #nazwy
        for i in range(len(names["features"])):
            if self.__city in names["features"][i]["properties"]['jpt_nazwa_']:
                id = names["features"][i]["properties"]['jpt_kod_je']
        #Ostrzeżenia
        message = self.__start_message + " _ "
        try:
            id_w = alerts["teryt"][id][0]
        except KeyError:
            message += " ostrzezen_nie_ma "
        else:
            #print(id_w)
            kod = alerts["warnings"][id_w]["PhenomenonCode"]
            stopien = alerts["warnings"][id_w]["Level"]
            prawd = alerts["warnings"][id_w]["Probability"]
            print(kod)
            print(stopien)
            print(prawd)
            message += " ostrzezenie_przed "+str(self.codes[kod])+" "+ str(self.stopnie[stopien]) + " stopnia" + " " + "prawdopodobienstwo " + str(self.procent[int(prawd)]) + " procent _ _ "
        return(message)
    def get_data(self):
        message = self.process()
        print(message)
        return {
            "message": message,
            "source": "meteo imgw",
        }
