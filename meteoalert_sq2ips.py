import requests
import logging
from colorcodes import *
from datetime import datetime

from sr0wx_module import SR0WXModule


class MeteoAlertSq2ips(SR0WXModule):
    def __init__(self, language, city_id, start_message, hydronames, short_validity, service_url):
        self.__language = language
        self.__short_validity = short_validity
        self.__hydronames = hydronames
        self.__start_message = start_message
        self.__city_id = city_id
        self.__logger = logging.getLogger(__name__)
        self.codes = {"SW": "silnym_wiatrem", "ID": "intensywnymi_opadami_deszczu", "OS": "opadami_sniegu", "IS": "intensywnymi_opadami_sniegu", "OM": "opadami_marznacymi", "ZZ": "zawiejami_lub_zamieciam_snieznymi", "OB": "oblodzeniem", "PR": "przymrozkami", "RO": "roztopami", "UP": "upalem", "MR": "silnym_mrozem", "MG": "gesta_mgla",
                      "MS": "mgla_intensywnie_osadzajaca_szadz", "BU": "burzami", "BG": "burzami_z_gradem", "DB": "silnym_deszczem_z_burzami", "GWSW": "gwaltownym_wzrostem_stanow_wody", "W_PSA": "wezbraniem_z_przekroczeniem_stanow_alarmowych", "W_PSO": "wezbraniem_z_przekroczeniem_stanow_ostrzegawczych", "SH": "susza_hydrologiczna"}
        self.komcodes = {"SW": "silnym_wietrze", "ID": "intensywnych_opadach_deszczu", "OS": "opadach_sniegu", "IS": "intensywnych_opadach_sniegu", "OM": "opadach_marznacych", "ZZ": "zawiejach_lub_zamieciach_snieznych", "OB": "oblodzeniu", "PR": "przymrozkach", "RO": "roztopach", "UP": "upale", "MR": "silnym_mrozie", "MG": "gestej_mgle",
                      "MS": "mgle_intensywnie_osadzajacej_szadz", "BU": "burzach", "BG": "burzach_z_gradem", "DB": "silnym_deszczu_z_burzami", "GWSW": "gwaltownym_wzroscie_stanow_wody", "W_PSA": "wezbraniu_z_przekroczeniem_stanow_alarmowych", "W_PSO": "wezbraniu_z_przekroczeniem_stanow_ostrzegawczych", "SH": "suszy_hydrologicznej"}
        self.stopnie = {"1": "pierwszego", "2": "drugiego", "3": "trzeciego"}
        self.__service_url = service_url

    def processDate(self, text, komets=False):
        if text[0:4] == "9999":
            return "waz_ne_do_odwol_ania "
        months = {
            "1": " stycznia ", "2": " lutego ", "3": " marca ",
            "4": " kwietnia ", "5": " maja ", "6": " czerwca ", "7": " lipca ",
            "8": " sierpnia ", "9": " września ", "10": " października ",
            "11": " listopada ", "12": " grudnia "}
        date = datetime.strptime(text[0:13], "%Y-%m-%dT%H")

        if self.__short_validity == False:
            if komets:
                text = "waz_ny_do_godziny " #
            else:
                text = "waz_ne_do_godziny "
            tekst += date.strftime("%H")+"_00 " + str(date.day) + "-go " + months[str(date.month)] + str(date.year)
        elif self.__short_validity == True:
            if date.month == datetime.now().month and date.year == datetime.now().year and date.day <= datetime.now().day+1:
                if date.day == datetime.now().day:
                    if komets:
                        text = "waz_ny_do_kon_ca_dnia" #
                    else:
                        text = "waz_ne_do_kon_ca_dnia"
                elif date.day == datetime.now().day+1:
                    if komets:
                        text = "waz_ny_do_jutra" #
                    else:
                        text = "waz_ne_do_jutra"
            else:
                if komets:
                    text = "waz_ny_do " + str(date.day) + "-go " + months[str(date.month)] #
                else:
                    text = "waz_ne_do " + str(date.day) + "-go " + months[str(date.month)]
        return text


    def processId(self, alerts, komets):
        id_wa = []
        id_wk = []

        for id in self.__city_id:
            if id in alerts["teryt"]: # Ostrzeżenia
                for i in alerts["teryt"][id]:
                    id_wa.append(i)
            if id in komets["teryt"]: # Komunikaty
                for i in komets["teryt"][id]:
                    id_wk.append(i)
        return id_wa, id_wk

    def processKomets(self, id_wk, komets):
        message = ""
        warnings_used = []
        for i in id_wk:
            kod = komets["komets"][i]["Phenomenon"][0]['Code']
            if kod in warnings_used:
                self.__logger.warning("Powtórzenie ostrzeżenia: "+kod)
            else:
                warnings_used.append(kod)
                wazne_do = komets["komets"][i]["LxValidTo"]
                wazne_do_text = self.processDate(wazne_do, True)
                self.__logger.info("kod: "+kod+ " ważne do: "+wazne_do)
                message += " ".join(["komunikat_o", self.komcodes[kod], wazne_do_text, "_ "])
        return message
    
    def processAlerts(self, id_wa, alerts):
        message = ""
        warnings_used = []
        for i in id_wa:
            kod = alerts["warnings"][i]["PhenomenonCode"]
            if kod in warnings_used:
                self.__logger.warning("Powtórzenie ostrzeżenia: "+kod)
            else:
                warnings_used.append(kod)
                stopien = alerts["warnings"][i]["Level"]
                #prawd = alerts["warnings"][i]["Probability"]
                wazne_do = alerts["warnings"][i]["LxValidTo"]
                wazne_do_text = self.processDate(wazne_do)
                self.__logger.info("kod: "+kod+" stopień: " + stopien + " ważne do: "+wazne_do)
                message += " ".join(["ostrzezenie_przed", self.codes[kod], self.stopnie[stopien], "stopnia", wazne_do_text, "_ "])
        return message
    
    def processHydro(self, hydronames, alerts_hydro):
        hydro_used = []
        message = ""
        for i in range(len(alerts_hydro["warnings"])):
            for j in range(len(alerts_hydro["warnings"][i]["Zlewnie"])):
                if alerts_hydro["warnings"][i]["Zlewnie"][j]["Code"] in hydronames:
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

                        message += " ".join(["ostrzezenie_przed", self.codes[kod], ""])
                        if stopien in self.stopnie:
                            message += " ".join([self.stopnie[stopien], "stopnia "])
                        message += " ".join([wazne_do_text, "_ "])
        return message

    def get_data(self, connection):
        try:
            url_alerts = self.__service_url + "osmet/latest/osmet-teryt?lc="
            url_komets = self.__service_url + "osmet/latest/komet-teryt?lc="
            url_alerts_hydro = self.__service_url + "warnhydro/latest/warn"
            
            self.__logger.info("::: Pobieranie dane o ostrzeżeniach...")

            alerts = self.requestData(url_alerts, self.__logger, 10, 3).json()
            komets = self.requestData(url_komets, self.__logger, 10, 3).json()
            alerts_hydro = self.requestData(url_alerts_hydro, self.__logger, 10, 3).json()

            self.__logger.info("::: Przetważanie danych...")
            
            self.__logger.info(f"id meteo: {self.__city_id}, hydronames: {self.__hydronames}")

            id_wa, id_wk = self.processId(alerts, komets)

            if len(id_wa) > 0 or len(id_wk) > 0:
                os = True
            else:
                os = False
            
            message = " ".join([self.processKomets(id_wk, komets), self.processAlerts(id_wa, alerts), self.processHydro(self.__hydronames, alerts_hydro)])
            connection.send({
                "message": message,
                "source": "imgw_pib",
            })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
