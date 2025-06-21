import ephem
import datetime
import logging

from sr0wx_module import SR0WXModule
from config import LATITUDE, LONGITUDE

class CalendarSq2ips(SR0WXModule):
    """Moduł wyliczajacy wschody i zachody słońca"""

    def __init__(self, language, ele, pre, temp, hori):
        self.__language = language
        self.__ele = ele
        self.__pre = pre
        self.__temp = temp
        self.__hori = hori
        self.__logger = logging.getLogger(__name__)

    def hoursToNumbers(self, time="00:00"):
        datetime_object = datetime.datetime.strptime(time, "%H:%M")
        time_words = self.__language.read_datetime(datetime_object, "%H %M")
        return time_words

    def get_data(self):
        self.__logger.info("::: Przeliczam dane...")
        Gdynia = ephem.Observer()
        Gdynia.lat = str(LATITUDE)
        Gdynia.lon = str(LONGITUDE)
        Gdynia.elevation = self.__ele
        Gdynia.pressure = self.__pre
        Gdynia.temp = self.__temp
        Gdynia.horizon = self.__hori
        Gdynia.date = datetime.datetime.now()
        sun = ephem.Sun()
        sunrise = " ".join(
            [
                "wscho_d_sl_on_ca",
                "godzina",
                self.hoursToNumbers(
                    str(ephem.localtime(Gdynia.next_rising(sun)).hour)
                    + ":"
                    + str(ephem.localtime(Gdynia.next_rising(sun)).minute)
                ),
                " ",
            ]
        )
        sunset = " ".join(
            [
                "zacho_d_sl_on_ca",
                "godzina",
                self.hoursToNumbers(
                    str(ephem.localtime(Gdynia.next_setting(sun)).hour)
                    + ":"
                    + str(ephem.localtime(Gdynia.next_setting(sun)).minute)
                ),
                " ",
            ]
        )
        message = " ".join(["kalendarium", "_", sunrise, "_", sunset])
        Gdynia.next_antitransit
        self.__logger.info(f"Wschód: {ephem.localtime(Gdynia.next_rising(sun))}")
        self.__logger.info(f"Zachód: {ephem.localtime(Gdynia.next_setting(sun))}")
        return(
            {
                "message": message,
                "source": "",
            }
        )
