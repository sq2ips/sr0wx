import requests
import logging
from colorcodes import *
from datetime import datetime

from sr0wx_module import SR0WXModule


class MeteoAlertSq2ips(SR0WXModule):
    def __init__(self, city_id, start_message, hydronames, validity_type):
        self.__validity_type = validity_type
        self.__hydronames = hydronames
        self.__start_message = start_message
        self.__city_id = str(city_id)
        self.__logger = logging.getLogger(__name__)
        self.codes = {"SW": "silnym_wiatrem", "ID": "intensywnymi_opadami_deszczu", "OS": "opadami_sniegu", "IS": "intensywnymi_opadami_sniegu", "OM": "opadami_marznacymi", "ZZ": "zawiejami_lub_zamieciam_snieznymi", "OB": "oblodzeniem", "PR": "przymrozkami", "RO": "roztopami", "UP": "upalem", "MR": "silnym_mrozem", "MG": "gesta_mgla",
                      "MS": "mgla_intensywnie_osadzajaca_szadz", "BU": "burzami", "BG": "burzami_z_gradem", "DB": "silnym_deszczem_z_burzami", "GWSW": "gwaltownym_wzrostem_stanow_wody", "W_PSA": "wezbraniem_z_przekroczeniem_stanow_alarmowych", "W_PSO": "wezbraniem_z_przekroczeniem_stanow_ostrzegawczych", "SH": "susza_hydrologiczna"}
        self.stopnie = {"1": "pierwszego", "2": "drugiego", "3": "trzeciego"}
        self.procent = {10: "dziesiec", 20: "dwadziescia", 30: "trzydziesci", 40: "czterdziesci", 50: "piecdziesiat",
                        60: "szescdziesiat", 70: "siedemdziesiat", 80: "osiemdziesiat", 90: "dziewiecdziesiat", 100: "sto"}

    def processDate(self, text):
        if text[0:4] == "9999":
            return ("waz_ne_do_odwol_ania ")
        months = {
            "1": " stycznia ", "2": " lutego ", "3": " marca ",
            "4": " kwietnia ", "5": " maja ", "6": " czerwca ", "7": " lipca ",
            "8": " sierpnia ", "9": " września ", "10": " października ",
            "11": " listopada ", "12": " grudnia "}
        date = datetime.strptime(text[0:13], "%Y-%m-%dT%H")
        if self.__validity_type == 1:
            text = "waz_ne_do_godziny " + date.strftime("%H")+"_00 " + str(
                date.day) + "-go " + months[str(date.month)] + str(date.year)
        elif self.__validity_type == 2:
            if date.month == datetime.now().month and date.year == datetime.now().year:
                if date.day == datetime.now().day:
                    text = "waz_ne_do_kon_ca_dnia"
                elif date.day == datetime.now().day+1:
                    text = "waz_ne_do_jutra"
                else:
                    text = "waz_ne_do " + \
                        str(date.day) + "-go " + months[str(date.month)]
            else:
                text = "waz_ne_do " + str(date.day) + \
                    "-go " + months[str(date.month)]
        return text

    def downloadData(self):
        # urlap = "https://meteo.imgw.pl/api/meteo/messages/v1/prog/latest/pronieb/ALL"
        #urln = "https://meteo.imgw.pl/dyn/data/out1proc.json?v=1.2"
        urla = "https://meteo.imgw.pl/api/meteo/messages/v1/osmet/latest/osmet-teryt?lc="
        urlk = "https://meteo.imgw.pl/api/meteo/messages/v1/osmet/latest/komet-teryt?lc="
        urlah = "https://meteo.imgw.pl/api/meteo/messages/v1/warnhydro/latest/warn"
        self.__logger.info("::: Pobieranie ostrzeżeń...")
        alerts = self.requestData(urla, self.__logger, 10, 3).json()
        #names = requests.get(url=urln).json()
        komets = self.requestData(urlk, self.__logger, 10, 3).json()
        alerts_hydro = self.requestData(urlah, self.__logger, 10, 3).json()
        #return (alerts, names, alerts_hydro)
        return  (alerts, komets, alerts_hydro)

    def process(self):
        data = self.downloadData()
        alerts = data[0]
        #names = data[1]
        komets = data[1]
        alerts_hydro = data[2]
        self.__logger.info("::: Przetważanie danych...")
        # nazwy
        # for i in range(len(names["features"])):
        #    if self.__city in names["features"][i]["properties"]['jpt_nazwa_']:
        #        id = names["features"][i]["properties"]['jpt_kod_je']
        self.__logger.info(f"id: {self.__city_id}")
        # Ostrzeżenia
        message = self.__start_message + " _ "
        id_w = []
        id_wk = []
        if self.__city_id in alerts["teryt"]:
            for i in alerts["teryt"][self.__city_id]:
                id_w.append(i)

        if self.__city_id in komets["teryt"]:
            for i in komets["teryt"][self.__city_id]:
                id_wk.append(i)

        if len(id_w) > 0 or len(id_wk) > 0:
            os = True
        else:
            os = False

        warnings_used = []
        for i in id_wk:
            kod = komets["komets"][i]["Phenomenon"][0]['Code']
            if kod in warnings_used:
                self.__logger.warning("Powtórzenie ostrzeżenia: "+kod)
            else:
                warnings_used.append(kod)
                wazne_do = komets["komets"][i]["LxValidTo"]
                wazne_do_text = self.processDate(wazne_do)
                self.__logger.info(
                    "kod: "+kod+ " ważne do: "+wazne_do)
                # message += " ostrzezenie_przed "+str(self.codes[kod])+" "+ str(self.stopnie[stopien]) + " stopnia " + "prawdopodobienstwo " + str(self.procent[int(prawd)]) + " procent" + " _ "
                message += " ostrzezenie_przed "+str(self.codes[kod]) + " " + wazne_do_text + " _ "

        for i in id_w:
            kod = alerts["warnings"][i]["PhenomenonCode"]
            if kod in warnings_used:
                self.__logger.warning("Powtórzenie ostrzeżenia: "+kod)
            else:
                warnings_used.append(kod)
                stopien = alerts["warnings"][i]["Level"]
                prawd = alerts["warnings"][i]["Probability"]
                wazne_do = alerts["warnings"][i]["LxValidTo"]
                wazne_do_text = self.processDate(wazne_do)
                self.__logger.info(
                    "kod: "+kod+" stopień: " + stopien + " ważne do: "+wazne_do)
                # message += " ostrzezenie_przed "+str(self.codes[kod])+" "+ str(self.stopnie[stopien]) + " stopnia " + "prawdopodobienstwo " + str(self.procent[int(prawd)]) + " procent" + " _ "
                message += " ostrzezenie_przed "+str(self.codes[kod])+" " + str(
                    self.stopnie[stopien]) + " stopnia " + wazne_do_text + " _ "


        hydro_used = []
        for i in range(len(alerts_hydro["warnings"])):
            for j in range(len(alerts_hydro["warnings"][i]["Zlewnie"])):
                if alerts_hydro["warnings"][i]["Zlewnie"][j]["Code"] in self.__hydronames:
                    os = True
                    # print(alerts_hydro["warnings"][i]["WarnHydro"])
                    kod = alerts_hydro["warnings"][i]["WarnHydro"]["Phenomena"]
                    if kod in hydro_used:
                        self.__logger.warning("Powtórzenie ostrzeżenia: "+kod)
                    else:
                        hydro_used.append(kod)
                        prawd = alerts_hydro["warnings"][i]["WarnHydro"]["Probability"]
                        stopien = alerts_hydro["warnings"][i]["WarnHydro"]["Level"]
                        wazne_do = alerts_hydro["warnings"][i]["WarnHydro"]["LxValidTo"]
                        wazne_do_text = self.processDate(wazne_do)
                        self.__logger.info(
                            "kod: "+kod+" stopień: " + stopien + " ważne do: "+wazne_do)

                        message += " ostrzezenie_przed " + \
                            str(self.codes[kod])+" "
                        if stopien in list(self.stopnie):
                            # message += " ostrzezenie_przed "+str(self.codes[kod])+" "+ str(self.stopnie[stopien]) + " stopnia " + "prawdopodobienstwo " + str(self.procent[int(prawd)]) + " procent" + " _ "
                            message += " " + \
                                str(self.stopnie[stopien]) + " stopnia "
                        message += wazne_do_text
                        message += " _ "

        if (os == False):
            message += " ostrzezen_nie_ma "
        message += " _ "
        return (message)

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
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
