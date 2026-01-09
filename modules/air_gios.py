import logging

from sr0wx_module import SR0WXModule

import base64
import json
import requests
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1
from Crypto.Util.Padding import unpad
from binascii import unhexlify


class AesUtil:
    def __init__(self, key_size, iteration_count):
        self.key_size = key_size // 8  # bits → bytes
        self.iteration_count = iteration_count

    def generate_key(self, salt, passphrase):
        return PBKDF2(
            password=passphrase.encode(),
            salt=unhexlify(salt),
            dkLen=self.key_size,
            count=self.iteration_count,
            hmac_hash_module=SHA1
        )

    def decrypt(self, salt, iv, passphrase, cipher_text):
        key = self.generate_key(salt, passphrase)
        cipher = AES.new(key, AES.MODE_CBC, unhexlify(iv))
        decrypted = cipher.decrypt(base64.b64decode(cipher_text))
        return unpad(decrypted, AES.block_size).decode("utf-8")

class AirGios(SR0WXModule):
    """Moduł pobierający info o zanieczyszczeniach powietrza z GIOŚ"""
    def __init__(self, language, service_url, uri_index, uri_all, sensor_id, onlyAlerts):
        self.__language = language
        self.__service_url = service_url
        self.__uri_index = uri_index
        self.__uri_all = uri_all
        self.__sensor_id = sensor_id
        self.__only_alerts = onlyAlerts

        self.__logger = logging.getLogger(__name__)

        self.__index_text = "Wartość indeksu dla wskaźnika "
        self.__index_values = {0: "poziom_bardzo_dobry", 1: "poziom_dobry", 2: "poziom_dostateczny", 3: "poziom_umiarkowany", 4: "poziom_zl_y", 5: "poziom_bardzo_zl_y"}
        self.__main_index_values = {0: "bardzo_dobry", 1: "dobry", 2: "dostateczny", 3: "umiarkowany", 4: "zl_y", 5: "bardzo_zl_y"}
        self.__sensors = {"SO2": "dwutlenek_siarki", "NO2": "dwutlenek_azotu", "PM10": "pyl__pm10", "PM2.5": "pyl__pm25", "O3": "ozon", "CO": "tlenek_we_gla", "C6H6": "benzen"}
    def processName(self, data):
        for station in data:
            if station["Identyfikator stacji"] == self.__sensor_id:
                return station["Nazwa stacji"]
        raise ValueError(f"Stacjia o ID {self.__sensor_id} nie istnieje.")
    def processIndex(self, data):
        values = {}
        for key in data.keys():
            if self.__index_text in key:
                sens = key.replace(self.__index_text, "")
                if data[key] == None:
                    self.__logger.warning(f"Brak danych o poziomie {sens} z czujnika")
                else:
                    values[sens] = data[key]
        
        return (data["Wartość indeksu"], values)
    def processValues(self, data):
        values = {}
        for param in data["currentValuesByParamCode"].keys():
            values[param.replace(",", ".").replace("<sub>", "").replace("</sub>", "")] = data["currentValuesByParamCode"][param]
        
        for value in values:
            if value not in self.__sensors:
                self.__logger.warning(f"Nieznana wartość: {value}")

        return values

    def getText(self, indexes, values):
        message = ""
        indexes = dict(sorted(indexes.items(), key=lambda item: item[1]))
        for value in list(indexes.keys())[::-1]:
            if value in self.__sensors:
                ind =  indexes[value]
                if value in values:
                    if ind > 0:
                        message+=" ".join([self.__sensors[value], self.__language.read_micrograms(round(values[value])), self.__index_values[ind], "_ "])
                    else:
                        message+=" ".join([self.__sensors[value], self.__index_values[ind], "_ "])
                else:
                    self.__logger.warning(f"Brak wartości odczytu {value}")

            else:
                self.__logger.warning(f"Pomiar {value} nieznany, pomijanie...")
        return message
    
    def decryptData(self, data, token):
        iteration_count = 1000
        key_size = 128
        iv = "dc0da04af8fee58593442bf834b30739"
        salt = "dc0da04af8fee58593442bf834b30739"

        aes_util = AesUtil(key_size, iteration_count)
        plaintext = aes_util.decrypt(salt, iv, token, data)

        return json.loads(plaintext)

    def getToken(self, session):
        code = session.get("https://powietrze.gios.gov.pl/pjp/current").text
        for line in code.splitlines(True):
            if "var encryptionKey = " in line:
                return line.split()[-1].replace("\"", "").replace(";", "") 
    
    def get_aqi_index_levels(self, id):
        session = requests.Session()

        token = self.getToken(session)

        url = "https://powietrze.gios.gov.pl/pjp/aqi-details/getAQIDetails"

        headers = {
            '_csrf_token': token,
        }

        data = {
            'id': str(id),
        }

        response = session.post(
            url,
            headers=headers,
            data=data,
        )
        response.raise_for_status()

        encrypted_data = response.text

        data = self.decryptData(encrypted_data, token)

        return data

    def get_data(self):
        uri_all = f"{self.__service_url}{self.__uri_all}"
        self.__logger.info("::: Pobieranie indeksu zanieczyszczenia powietrza...")
        data = self.requestData(uri_all, self.__logger, 10, 3).json()
        name = self.processName(data["Lista stacji pomiarowych"])

        self.__logger.info("::: Pobieranie nazw stacji...")
        uri_index = f"{self.__service_url}{self.__uri_index}{self.__sensor_id}"
        data = self.requestData(uri_index, self.__logger, 10, 3).json()

        self.__logger.info("::: Pobieranie wartości zanieczyszczeń...")
        values_data = self.get_aqi_index_levels(self.__sensor_id)

        self.__logger.info("::: Przetwarzanie danych...")
        values = self.processValues(values_data)

        main_index, indexes = self.processIndex(data["AqIndex"])

        if indexes == {}:
            raise Exception("Brak danych o poziomie zanieczyszczeń")
        if values == {}:
            raise Exception("Brak danych o wartości zanieczyszczeń")
        
        for k in indexes.keys():
            if k not in values:
                self.__logger.warning(f"Brak odczytu wartości {sens}")

        message = "informacja_o_skaz_eniu_powietrza _ "
        message += "stacja_pomiarowa "
        message += self.__language.trim_pl(name)

        if main_index == -1:
            self.__logger.warning("Brak wartości indeksu jakości powietrza")
        else:
            message += " _ stan_ogolny "
            message += self.__main_index_values[main_index]
        
        message += " _ "
        
        if self.__only_alerts and set(indexes.values()) == {0}:
            message += "brak_skaz_enia"
        else:
            message += self.getText(indexes, values)
        
        return(
            {
                "message": message,
                "source": "gios_",
            }
        )