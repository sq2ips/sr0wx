from sr0wx_module import SR0WXModule
import logging

from datetime import datetime


class TimeSq2ips(SR0WXModule):
    def __init__(self, language, start_message):
        self.__language = language
        self.__start_message = start_message
        self.__logger = logging.getLogger(__name__)

    def get_data(self, connection):
        try:
            time = ":".join([str(datetime.now().hour), str(datetime.now().minute)])
            datetime_object = datetime.strptime(time, "%H:%M")
            time_words = self.__language.read_datetime(datetime_object, "%H %M")
            message = " ".join(self.__start_message + [time_words])
            connection.send(
                {
                    "message": message,
                    "source": "",
                }
            )
        except Exception as e:
            self.__logger.exception(f"Exception when running {self}: {e}")
            connection.send(dict())
