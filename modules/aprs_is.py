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
    def decimal_to_deg_min(self, dd, deg_digits):
        # format APRS: DDMM.mm dla szerokości (deg_digits=2), DDDMM.mm dla długości (deg_digits=3)
        degrees = int(abs(dd))
        minutes = round((abs(dd) - degrees) * 60, 2)
        if minutes >= 60.0:
            degrees += 1
            minutes -= 60.0
        return f"{degrees:0{deg_digits}d}{minutes:05.2f}"
    def get_data(self):
        self.__logger.info("::: Wysyłanie ramki do APRS-IS...")
        AIS = None
        try:
            AIS = aprslib.IS(self.__call, passwd=self.__passwd)
            AIS.connect()
            lat = self.decimal_to_deg_min(self.__lat, 2)
            lon = self.decimal_to_deg_min(self.__lon, 3)
            lat_hemi = "N" if self.__lat >= 0 else "S"
            lon_hemi = "E" if self.__lon >= 0 else "W"
            AIS.sendall(f"{self.__call}>APZWX,TCPIP*:!{lat}{lat_hemi}/{lon}{lon_hemi}W{self.__comment}")
            self.__logger.info("::: Ramka APRS-IS wysłana")
        except Exception as e:
            self.__logger.error(f"::: Błąd wysyłania ramki APRS-IS: {e}")
        finally:
            if AIS is not None:
                try:
                    AIS.close()
                except Exception:
                    pass
        return {"message": None, "source": ""}