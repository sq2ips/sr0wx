import requests
import logging
from colorcodes import *

from sr0wx_module import SR0WXModule

class MeteoAlertSq2ips(SR0WXModule):
    def __init__(self, city, start_message, hydronames):
        self.__hydronames = hydronames
        self.__start_message=start_message
        self.__city = city
        self.__logger = logging.getLogger(__name__)
        self.codes = {"SW": "silnym_wiatrem","ID": "intensywnymi_opadami_deszczu","OS": "opadami_sniegu","IS": "intensywnymi_opadami_sniegu","OM": "opadami_marznacymi","ZZ": "zawiejami_lub_zamieciam_snieznymi","OB": "oblodzeniem","PR": "przymrozkami","RO": "roztopami","UP": "upalem","MR": "silnym_mrozem","MG": "gesta_mgla","MS": "mgla_intensywnie_osadzajaca_szadz","BU": "burzami","BG": "burzami_z_gradem","DB": "silnym_deszczem_z_burzami","GWSW": "gwaltownymi_wzrostami_stanow_wody","W_PSA": "wezbraniem_z_przekroczeniem_stanow_alarmowych","W_PSO": "wezbraniem_z_przekroczeniem_stanow_ostrzegawczych","SH": "susza_hydrologiczna"}
        self.stopnie = {"1":"pierwszego","2":"drugiego","3":"trzeciego"}
        self.procent = {10:"dziesiec",20:"dwadziescia",30:"trzydziesci",40:"czterdziesci",50:"piecdziesiat",60:"szescdziesiat",70:"siedemdziesiat",80:"osiemdziesiat",90:"dziewiecdziesiat",100:"sto"}
    def downloadData(self):
        #urlap = "https://meteo.imgw.pl/api/meteo/messages/v1/prog/latest/pronieb/ALL"
        urln = "https://meteo.imgw.pl/dyn/data/out1proc.json?v=1.2"
        urla = "https://meteo.imgw.pl/api/meteo/messages/v1/osmet/latest/osmet-teryt?lc="
        urlah = "https://meteo.imgw.pl/api/meteo/messages/v1/warnhydro/latest/warn"
        self.__logger.info("::: Pobieranie ostrzeżeń meteorologicznych...")
        alerts = requests.get(url = urla).json()
        names = requests.get(url = urln).json()
        alerts_hydro = requests.get(url = urlah).json()  
        return(alerts, names, alerts_hydro)
    def process(self):
        data = self.downloadData()
        alerts = data[0]
        names = data[1]
        alerts_hydro = data[2]
        self.__logger.info("::: Przetważanie danych...")
        #nazwy
        for i in range(len(names["features"])):
            if self.__city in names["features"][i]["properties"]['jpt_nazwa_']:
                id = names["features"][i]["properties"]['jpt_kod_je']
        #id = '2263'
        self.__logger.info("id: "+id)
        #Ostrzeżenia
        message = self.__start_message + " _ "
        os = True
        id_w = []
        try:
            for i in range(len(alerts["teryt"][id])):
                id_w.append(alerts["teryt"][id][i])
        except KeyError:
            os = False
        else:
            os = True
            #print(id_w)
            warnings_used = []
            for i in range(len(id_w)):
                kod = alerts["warnings"][id_w[i]]["PhenomenonCode"]
                if kod in warnings_used:
                        self.__logger.warning("Powtórzenie ostrzeżenia: "+kod)
                else:
                    stopien = alerts["warnings"][id_w[i]]["Level"]
                    prawd = alerts["warnings"][id_w[i]]["Probability"]
                    self.__logger.info("kod: "+kod+" stopień:" + stopien + " prawdopodobieństwo:"+prawd)
                    #message += " ostrzezenie_przed "+str(self.codes[kod])+" "+ str(self.stopnie[stopien]) + " stopnia " + "prawdopodobienstwo " + str(self.procent[int(prawd)]) + " procent" + " _ "
                    message += " ostrzezenie_przed "+str(self.codes[kod])+" "+ str(self.stopnie[stopien]) + " stopnia " + " _ "
        hydro_used = []
        for i in range(len(alerts_hydro["warnings"])):
            for j in range(len(alerts_hydro["warnings"][i]["Zlewnie"])):
                if alerts_hydro["warnings"][i]["Zlewnie"][j]["Code"] in self.__hydronames:
                    os = True
                    #print(alerts_hydro["warnings"][i]["WarnHydro"])
                    kod = alerts_hydro["warnings"][i]["WarnHydro"]["Phenomena"]
                    if kod in hydro_used:
                        self.__logger.warning("Powtórzenie ostrzeżenia: "+kod)
                    else:
                        hydro_used.append(kod)
                        prawd = alerts_hydro["warnings"][i]["WarnHydro"]["Probability"]
                        stopien = alerts_hydro["warnings"][i]["WarnHydro"]["Level"]
                        self.__logger.info("kod: "+kod+" stopień:" + stopien + " prawdopodobieństwo:"+prawd)
                        if stopien not in list(self.stopnie):
                            #message += " ostrzezenie_przed "+str(self.codes[kod])+" "+ str(self.stopnie[stopien]) + " stopnia " + "prawdopodobienstwo " + str(self.procent[int(prawd)]) + " procent" + " _ "
                            message += " ostrzezenie_przed "+str(self.codes[kod])+ " _ "
                        else:
                            message += " ostrzezenie_przed "+str(self.codes[kod])+" "+ str(self.stopnie[stopien]) + " stopnia " + " _ "

  
        
        if(os==False):
            message += " ostrzezen_nie_ma "
        message += " _ "
        return(message)
    def get_data(self, connection):
        try:
            message = self.process()
            connection.send({
                "message": message,
                "source": "meteo imgw",
            })
            return {
                "message": message,
                "source": "meteo imgw",
            }
        except Exception as e:
            self.__logger.exception(COLOR_FAIL + "Exception when running %s: %s"+ COLOR_ENDC, str(self), e)
            connection.send(dict())
