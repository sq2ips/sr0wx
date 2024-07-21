#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import logging

from colorcodes import *

from sr0wx_module import SR0WXModule

class KseSq2ips(SR0WXModule):
    def __init__(self, language, service_url):
        self.__language = language
        self.__service_url = service_url
        self.__logger = logging.getLogger(__name__)

    def get_data(self, connection):
        try:
            data = self.requestData(self.__service_url, self.__logger, 15, 3).json()["data"]

            message = "stan_sieci_energetycznej"

            message += " ".join([" _ zapotrzebowanie", self.__language.read_power(round(data["podsumowanie"]["zapotrzebowanie"], -2), "mega")])
            message += " ".join([" _ generacja", self.__language.read_power(round(data["podsumowanie"]["generacja"], -2), "mega")])

            saldo = data["podsumowanie"]["generacja"] - data["podsumowanie"]["zapotrzebowanie"]
            if saldo >= 0:
                message += " ".join([" _ saldo_wymiany eksport", self.__language.read_power(round(saldo, -2), "mega")])
            else:
                message += " ".join([" _ saldo_wymiany import", self.__language.read_power(round(saldo, -2), "mega")])

            connection.send({
                "message": message,
                "source": "pse",
            })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())