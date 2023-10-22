import ephem
import datetime
import logging

from colorcodes import *

from sr0wx_module import SR0WXModule

class CalendarSq2ips(SR0WXModule):
    """Klasa wyliczajaca wschody i zachody slonca"""
    def __init__(self,language,lat,lon,ele,pre,temp,hori):
        self.__language = language
        self.__lat = lat
        self.__lon = lon
        self.__ele = ele
        self.__pre = pre
        self.__temp = temp
        self.__hori = hori
        self.__logger = logging.getLogger(__name__)

    def hoursToNumbers(self, time="00:00"):
        datetime_object = datetime.datetime.strptime(time, '%H:%M')
        time_words = self.__language.read_datetime(datetime_object, '%H %M')
        return time_words
    def get_data(self, connection):
        try:
            self.__logger.info("::: Przeliczam dane...\n")
            Gdynia=ephem.Observer()
            Gdynia.lat= self.__lat
            Gdynia.lon= self.__lon
            Gdynia.elevation = self.__ele
            Gdynia.pressure = self.__pre
            Gdynia.temp = self.__temp
            Gdynia.horizon = self.__hori
            Gdynia.date = datetime.datetime.now()
            sun = ephem.Sun()
            sunrise = " ".join(["wscho_d_sl_on_ca","godzina",self.hoursToNumbers(str(ephem.localtime(Gdynia.next_rising(sun)).hour) + ":" + str(ephem.localtime(Gdynia.next_rising(sun)).minute)), " "])
            sunset = " ".join(["zacho_d_sl_on_ca","godzina",self.hoursToNumbers(str(ephem.localtime(Gdynia.next_setting(sun)).hour) + ":" + str(ephem.localtime(Gdynia.next_setting(sun)).minute)), " "])
            message = " ".join([" _ kalendarium _ ",sunrise ," _ ", sunset ," _ "])
            self.__logger.info(str(ephem.localtime(Gdynia.next_rising(sun)).hour) + ":" + str(ephem.localtime(Gdynia.next_rising(sun)).minute))
            self.__logger.info(str(ephem.localtime(Gdynia.next_setting(sun)).hour) + ":" + str(ephem.localtime(Gdynia.next_setting(sun)).minute))
            connection.send({
                "message":message,
                "source":"ephem",
            })
            return {
                "message":message,
                "source":"ephem",
            }
        except Exception as e:
            self.__logger.exception(COLOR_FAIL + "Exception when running %s: %s"+ COLOR_ENDC, str(self), e)
            connection.send(dict())

