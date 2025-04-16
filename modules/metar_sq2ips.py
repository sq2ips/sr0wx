import logging

from datetime import datetime, timezone

from sr0wx_module import SR0WXModule

class MetarSq2ips(SR0WXModule):
    def __init__(self, language, service_url, airport):
        self.__language = language
        self.__service_url = service_url
        self.__airport = airport
        self.__logger = logging.getLogger(__name__)

        self.__flags = {"AUTO": "komunikat_automatyczny"}
    def getMetar(self, url, airport):
        metar_json = self.requestData(url, self.__logger).json()
        
        if self.__airport not in metar_json:
            raise Exception(f"No airport with ICAO {airport}")

        metar_data = metar_json[self.__airport]["metars"]["sa"]["pl"][0]

        return metar_data
    
    def getWind(self, angle):
        msg = ""
        if 0 <= angle <= 23:
            msg += "polnocny"
        elif 23 < angle <= 67:
            msg += "polnocno wschodni"
        elif 67 < angle <= 112:
            msg += "wschodni"
        elif 112 < angle <= 157:
            msg += "poludniowo wschodni"
        elif 157 < angle <= 202:
            msg += "poludniowy"
        elif 202 < angle <= 247:
            msg += "poludniowo zachodni"
        elif 247 < angle <= 292:
            msg += "zachodni"
        elif 292 < angle <= 337:
            msg += "polnocno zachodni"
        elif 337 < angle <= 360:
            msg += "polnocny"
        return msg
    def getWindMax(self, angle):
        msg = ""
        if 0 <= angle <= 23:
            msg += "polnocnego"
        elif 23 < angle <= 67:
            msg += "polnocno wschodniego"
        elif 67 < angle <= 112:
            msg += "wschodniego"
        elif 112 < angle <= 157:
            msg += "poludniowo wschodniego"
        elif 157 < angle <= 202:
            msg += "poludniowego"
        elif 202 < angle <= 247:
            msg += "poludniowo zachodniego"
        elif 247 < angle <= 292:
            msg += "zachodniego"
        elif 292 < angle <= 337:
            msg += "polnocno zachodniego"
        elif 337 < angle <= 360:
            msg += "polnocnego"
        return msg
    
    def getText(self, metar):
        text = "komunikat_metar_dla_lotniska "

        # airport
        text += self.__airport

        text += " z_godziny "

        # time
        date = datetime.strptime(metar["date"], "%Y-%m-%dT%H:%M:%S.000Z")
        text += self.__language.read_datetime(date, "%H %M")

        text += " _ "

        # flags
        for flag in metar["flags"]:
            if flag in self.__flags:
                text += self.__flags[flag]
                text += " "
            else:
                self.__logger.warning(f"Unparsed flag: {flag}")
        
        # temp
        text += "temperatura "
        text += self.__language.read_temperature(metar["temperature"])

        # dew point
        text += " punkt_rosy "
        text += self.__language.read_temperature(metar["dewPoint"])

        # pressure
        text += " cisnienie "
        text += self.__language.read_pressure(metar["altimeter"])

        # visibility

        text += " widzialnos_c_ "
        vis = metar["visibility"]["value"]
        if vis >= 10:
            text += "ponad dziesiec kilometrow"
        else:
            text += self.__read_distance(vis)
        
        # wind

        text += " _ wiatr "
        if "minVariation" in metar["wind"] and self.getWind(metar["wind"]["directionDegrees"]) != self.getWind(metar["wind"]["minVariation"]) and self.getWind(metar["wind"]["directionDegrees"]) != self.getWind(metar["wind"]["maxVariation"]):
            text += "przewarznie "
        text += self.getWind(metar["wind"]["directionDegrees"])
        if "minVariation" in metar["wind"]:
            if self.getWind(metar["wind"]["directionDegrees"]) != self.getWind(metar["wind"]["minVariation"]):
                text += " od "
                text += self.getWindMax(metar["wind"]["minVariation"])
            if self.getWind(metar["wind"]["directionDegrees"]) != self.getWind(metar["wind"]["maxVariation"]):
                text += " do "
                text += self.getWindMax(metar["wind"]["maxVariation"])

        text += " "

        text += self.__language.read_speed(round(metar["wind"]["speed"] * 1.852), "kmph") # kt to kmph

        return text

    def get_data(self):
        self.__logger.info(f"::: Pobieranie danych METAR dla lotniska {self.__airport}...")
        metar = self.getMetar(self.__service_url, self.__airport)
        print(metar)

        self.__logger.info(f"::: Przetwarzanie danych...")
        message = self.getText(metar)

        return{
            "message": message,
            "source": "awiacja_imgw"
        }