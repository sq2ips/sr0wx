import logging
from datetime import datetime, timedelta

from sr0wx_module import SR0WXModule


class MeteoAlertSq2ips(SR0WXModule):
    """Moduł pobierający dane o zagrożeniach meteorolologicznych i hydrologicznych z meteo.imgw.pl"""

    def __init__(
        self, language, city_id, start_message, hydronames, short_validity, read_probability, service_url
    ):
        self.__language = language
        self.__short_validity = short_validity
        self.__read_pobability = read_probability
        self.__hydronames = hydronames
        self.__start_message = start_message
        self.__city_id = city_id
        self.__service_url = service_url
        self.__logger = logging.getLogger(__name__)
        self.codes = {
            "SW": "silnym_wiatrem",
            "ID": "intensywnymi_opadami_deszczu",
            "OS": "opadami_s_niegu",
            "IS": "intensywnymi_opadami_s_niegu",
            "OM": "opadami_marzna_cymi",
            "ZZ": "zawiejami_lub_zamieciami_s_niez_nymi",
            "OB": "oblodzeniem",
            "PR": "przymrozkami",
            "RO": "roztopami",
            "UP": "upal_em",
            "MR": "silnym_mrozem",
            "MG": "ge_sta__mgl_a_",
            "MS": "mgl_a__intensywnie_osadzaja_ca__szadx_",
            "BU": "burzami",
            "BG": "burzami_z_gradem",
            "DB": "silnym_deszczem_z_burzami",
            "GWSW": "gwal_townym_wzrostem_stano_w_wody",
            "W_PSA": "wezbraniem_z_przekroczeniem_stano_w_alarmowych",
            "W_PSO": "wezbraniem_z_przekroczeniem_stano_w_ostrzegawczych",
            "SH": "susza__hydrologiczna_",
        }
        self.komcodes = {
            "SW": "silnym_wietrze",
            "ID": "intensywnych_opadach_deszczu",
            "OS": "opadach_s_niegu",
            "IS": "intensywnych_opadach_s_niegu",
            "OM": "opadach_marzna_cych",
            "ZZ": "zawiejach_lub_zamieciach_s_niez_nych",
            "OB": "oblodzeniu",
            "PR": "przymrozkach",
            "RO": "roztopach",
            "UP": "upale",
            "MR": "silnym_mrozie",
            "MG": "ge_stej_mgle",
            "MS": "mgle_intensywnie_osadzaja_cej_szadx_",
            "BU": "burzach",
            "BG": "burzach_z_gradem",
            "DB": "silnym_deszczu_z_burzami",
            "GWSW": "gwal_townym_wzros_cie_stano_w_wody",
            "W_PSA": "wezbraniu_z_przekroczeniem_stano_w_alarmowych",
            "W_PSO": "wezbraniu_z_przekroczeniem_stano_w_ostrzegawczych",
            "SH": "suszy_hydrologicznej",
        }
        self.stopnie = {"1": "pierwszego", "2": "drugiego", "3": "trzeciego"}

    def processDate(self, validity, komets=False):
        if validity[0:4] == "9999":
            return "waz_ne_do_odwol_ania "
        months = {
            "1": " stycznia ",
            "2": " lutego ",
            "3": " marca ",
            "4": " kwietnia ",
            "5": " maja ",
            "6": " czerwca ",
            "7": " lipca ",
            "8": " sierpnia ",
            "9": " września ",
            "10": " października ",
            "11": " listopada ",
            "12": " grudnia ",
        }
        date = datetime.strptime(validity[0:13], "%Y-%m-%dT%H")
        text = ""
        if self.__short_validity:
            if date.day == datetime.now().day:
                if komets:
                    text = "waz_ny_do_kon_ca_dnia"
                else:
                    text = "waz_ne_do_kon_ca_dnia"
            elif date.day == (datetime.now() + timedelta(days=1)).day:
                if komets:
                    text = "waz_ny_do_jutra"
                else:
                    text = "waz_ne_do_jutra"
            else:
                if komets:
                    text = (
                        "waz_ny_do " + str(date.day) + "-go " + months[str(date.month)]
                    )
                else:
                    text = (
                        "waz_ne_do " + str(date.day) + "-go " + months[str(date.month)]
                    )
        else:
            if komets:
                text = "waz_ny_do_godziny "
            else:
                text = "waz_ne_do_godziny "
            text += (
                date.strftime("%H")
                + "_00 "
                + str(date.day)
                + "-go "
                + months[str(date.month)]
                + str(date.year)
            )

        return text

    def processId(self, alerts, komets):
        id_wa = []
        id_wk = []

        for id in self.__city_id:
            if id in alerts["teryt"]:  # Ostrzeżenia
                for i in alerts["teryt"][id]:
                    id_wa.append(i)
            if id in komets["teryt"]:  # Komunikaty
                for i in komets["teryt"][id]:
                    id_wk.append(i)
        return id_wa, id_wk

    def processKomets(self, id_wk, komets):
        message = ""
        warnings_used = []
        for i in id_wk:
            kod = komets["komets"][i]["Phenomenon"][0]["Code"]
            if kod in warnings_used:
                self.__logger.warning("Powtórzenie ostrzeżenia: " + kod)
            else:
                warnings_used.append(kod)
                wazne_do = komets["komets"][i]["LxValidTo"]
                wazne_do_text = self.processDate(wazne_do, True)
                self.__logger.info("kod: " + kod + " ważne do: " + wazne_do)
                message += " ".join(
                    ["komunikat_o", self.komcodes[kod], wazne_do_text, "_ "]
                )
        return message, warnings_used

    def processAlerts(self, id_wa, alerts, warnings_used):
        message = ""
        for i in id_wa:
            kod = alerts["warnings"][i]["PhenomenonCode"]
            if kod in warnings_used:
                self.__logger.warning("Powtórzenie ostrzeżenia: " + kod)
            else:
                warnings_used.append(kod)
                stopien = alerts["warnings"][i]["Level"]
                prawd = alerts["warnings"][i]["Probability"]
                wazne_do = alerts["warnings"][i]["LxValidTo"]
                self.__logger.info(f"kod: {kod}, stopień: {stopien}, prawdopodobieństwo: {prawd}, ważne do: {wazne_do}")
                message += " ".join(["ostrzezenie_przed", self.codes[kod], ""])
                message += " ".join([self.stopnie[stopien], "stopnia "])
                if self.__read_pobability:
                    message += " ".join(["prawdopodobienstwo", self.__language.read_percent(int(prawd)), ""])
                message += " ".join([self.processDate(wazne_do), "_ "])

        return message

    def processHydro(self, hydronames, alerts_hydro):
        hydro_used = []
        message = ""
        for i in range(len(alerts_hydro["warnings"])):
            for j in range(len(alerts_hydro["warnings"][i]["Zlewnie"])):
                if alerts_hydro["warnings"][i]["Zlewnie"][j]["Code"] in hydronames:
                    kod = alerts_hydro["warnings"][i]["WarnHydro"]["Phenomena"]
                    if kod in hydro_used:
                        self.__logger.warning("Powtórzenie ostrzeżenia: " + kod)
                    else:
                        hydro_used.append(kod)
                        prawd = alerts_hydro["warnings"][i]["WarnHydro"]["Probability"]
                        stopien = alerts_hydro["warnings"][i]["WarnHydro"]["Level"]
                        wazne_do = alerts_hydro["warnings"][i]["WarnHydro"]["LxValidTo"]
                        self.__logger.info(f"kod: {kod}, prawdopodobieństwo: {prawd}, ważne do: {wazne_do}")

                        message += " ".join(["ostrzezenie_przed", self.codes[kod], ""])
                        # if stopien in self.stopnie:
                        #    message += " ".join([self.stopnie[stopien], "stopnia "]) # ostrzerzenia hydro nie potrzebują stopni
                        if self.__read_pobability:
                            message += " ".join(["prawdopodobienstwo", self.__language.read_percent(int(prawd)), ""])
                        message += " ".join([self.processDate(wazne_do), "_ "])
        return message

    def get_data(self):
        url_komets = self.__service_url + "osmet/latest/komet-teryt?lc="
        url_alerts = self.__service_url + "osmet/latest/osmet-teryt?lc="
        url_alerts_hydro = self.__service_url + "warnhydro/latest/warn"
        self.__logger.info("::: Pobieranie dane o ostrzeżeniach...")

        komets = self.requestData(url_komets, self.__logger).json()
        alerts = self.requestData(url_alerts, self.__logger).json()
        alerts_hydro = self.requestData(url_alerts_hydro, self.__logger).json()
        
        self.__logger.info("::: Przetważanie danych...")
        self.__logger.info(
            f"id meteo: {self.__city_id}, hydronames: {self.__hydronames}"
        )
        id_wa, id_wk = self.processId(alerts, komets)
        if len(id_wa) > 0 or len(id_wk) > 0:
            os = True
        else:
            os = False
        msg_komets, warnings_used = self.processKomets(id_wk, komets)
        msg_alerts = self.processAlerts(id_wa, alerts, warnings_used)
        msg_hydro = self.processHydro(self.__hydronames, alerts_hydro)
        message = " ".join(["_", msg_komets, msg_alerts, msg_hydro])
        if len(message.split()) == 1:
            message = "ostrzezen_nie_ma"
        return(
            {
                "message": message,
                "source": "imgw_pib",
            }
        )