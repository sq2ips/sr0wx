# by SQ2IPS
from sr0wx_module import SR0WXModule
import logging

from datetime import datetime, timedelta


class TimeInfo(SR0WXModule):
    def __init__(self, language, start_message, round_minutes, maxwaittime, round_part):
        self.__language = language
        self.__maxwaittime = maxwaittime
        self.__start_message = start_message
        self.__round_minutes = round_minutes
        self.__round_part = round_part
        self.__logger = logging.getLogger(__name__)

    def get_data(self):
        time = datetime.now()
        if self.__round_minutes:
            time_rounded = time + (datetime.min - time) % timedelta(minutes=self.__round_part)
            if (time_rounded - time).seconds/60 > self.__maxwaittime:
                self.__logger.warning(f"Różnica czasu zaokrąglonego od aktualnego ({time_rounded - time}) jest większa od {self.__maxwaittime} minut, pomijanie...")
            else:
                time = time_rounded
        time_words = self.__language.read_datetime(time, "%H %M")
        message = " ".join(self.__start_message + [time_words])
        return(
            {
                "message": message,
                "source": "",
            }
        )
