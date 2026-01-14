import requests
import logging

from sr0wx_module import SR0WXModule

class HealthChecksIo(SR0WXModule):
    def __init__(self, service_url, uuid):
        self.__service_url = service_url
        self.__uuid = uuid
        self.__logger = logging.getLogger(__name__)
    def get_data(self):
        self.__logger.info("::: Wysyłanie ping do healthchecks.io...")

        res = requests.get(self.__service_url+self.__uuid)
        res.raise_for_status()
        if res.text != "OK":
            raise Exception("Nieprawidłowa odpowiedź serwera")
        else:
            self.__logger.info("::: Ping wysłany, status OK")
        return {"message": None, "source": ""}