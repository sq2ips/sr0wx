import logging
import aprslib

from sr0wx_module import SR0WXModule

class AprsIs(SR0WXModule):
    def __init__(self, passwd, call, lat, lon, comment):
        self.__passwd = passwd
        self.__call = call
        self.__lat = lat
        self.__lon = lon
        self.__comment = comment
        self.__logger = logging.getLogger(__name__)
    def decimal_to_deg_min(self, dd):
        degrees = int(dd)
        minutes = abs(dd - degrees) * 60
        return f"{degrees}{round(minutes, 2)}"
    def get_data(self):
        self.__logger.info("::: Wysyłanie ramki do APRS-IS...")
        AIS = aprslib.IS(self.__call, passwd=self.__passwd)
        AIS.connect()
        lat = self.decimal_to_deg_min(self.__lat)
        lon = self.decimal_to_deg_min(self.__lon)
        
        AIS.sendall(f"{self.__call}>APZWX,TCPIP*:!{lat}N/0{lon}EW{self.__comment}")
        return {"message": None, "source": ""}