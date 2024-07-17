#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import urllib.request
import logging

from PIL import Image

from colorcodes import *

from sr0wx_module import SR0WXModule


class PropagationSq9atk(SR0WXModule):
    """Klasa pobierająca informacje o propagacji"""

    def __init__(self, language, service_url):
        self.__service_url = service_url
        self.__language = language
        self.__logger = logging.getLogger(__name__)
        self.__pixels = {
            # niepotrzebne pasma można zaremowac znakiem '#'
            # 160 : {'day' :{'x':50, 'y':60},  'night':{'x':100, 'y':60}},
            80: {'day': {'x': 50, 'y': 95},  'night': {'x': 100, 'y': 95}},
            40: {'day': {'x': 50, 'y': 140}, 'night': {'x': 100, 'y': 140}},
            20: {'day': {'x': 50, 'y': 185}, 'night': {'x': 100, 'y': 185}},
            10: {'day': {'x': 50, 'y': 230}, 'night': {'x': 100, 'y': 230}},
            6: {'day': {'x': 50, 'y': 270}, 'night': {'x': 100, 'y': 270}},
        }

        self.__levels = {
            '#17e624': 'warunki_podwyzszone',  # zielony
            '#e6bc17': 'warunki_normalne',  # żółty
            '#e61717': 'warunki_obnizone',  # czerwony
            '#5717e6': 'pasmo_zamkniete',  # fioletowy
        }

    def rgb2hex(self, rgb):
        return '#%02x%02x%02x' % rgb

    def downloadImage(self, url):
        self.__logger.info("::: Odpytuję adres: " + url)
        webFile = urllib.request.URLopener()
        webFile.retrieve(url, "cache/propagacja.png")
        return Image.open("cache/propagacja.png", 'r')

    def collectBandConditionsFromImage(self, image, dayTime):
        try:
            imageData = image.load()
            data = []
            equal = True
            for band in sorted(self.__pixels)[::-1]:
                x = self.__pixels[band][dayTime]['x']
                y = self.__pixels[band][dayTime]['y']
                rgba = imageData[x, y]
                color = self.rgb2hex((rgba[0], rgba[1], rgba[2]))

                # można zaremowac wybraną grupę aby nie podawać info o konkretnych warunkach
                if self.__levels[color] == 'warunki_podwyzszone':
                    string = str(band) + '_metrow' + ' ' + self.__levels[color]

                elif self.__levels[color] == 'warunki_normalne':
                    string = str(band) + '_metrow' + ' ' + self.__levels[color]

                elif self.__levels[color] == 'warunki_obnizone':
                    string = str(band) + '_metrow' + ' ' + self.__levels[color]

                elif self.__levels[color] == 'pasmo_zamkniete':
                    string = str(band) + '_metrow' + ' ' + self.__levels[color]

                if len(data) > 0 and data[-1:][0].split()[1] != string.split()[1]:
                    equal = False
                data.append(string)
            data.insert(0, " _ pasma _ ")
            if equal:
                data = ["na_wszystkich_pasmach " + self.__levels[color]]
            return data
        except:
            return list()

    def get_data(self, connection):
        try:
            image = self.downloadImage(self.__service_url)

            self.__logger.info("::: Przetwarzam dane...\n")

            message = " ".join([
                " _ informacje_o_propagacji ",
                " _ dzien _ ",
                #" _ pasma _ ",
                " _ " .join(self.collectBandConditionsFromImage(image, 'day')),
                " _ noc _ ",
                #" _ pasma _ ",
                " _ " .join(
                    self.collectBandConditionsFromImage(image, 'night')),
                " _ "
            ])

            connection.send({
                "message": message,
                "source": "noaa",
            })
        except Exception as e:
            self.__logger.exception(
                COLOR_FAIL + "Exception when running %s: %s" + COLOR_ENDC, str(self), e)
            connection.send(dict())
