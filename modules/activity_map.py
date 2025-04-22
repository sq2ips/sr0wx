#
#   Copyright 2009-2014 Michal Sadowski (sq6jnx at hamradio dot pl)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import base64
import logging
import json

import requests

from sr0wx_module import SR0WXModule
from config import LATITUDE, LONGITUDE


class ActivityMap(SR0WXModule):
    """This module does not give any data, it just contacts application to mark
    station on the map.

    Parameters:
        - `callsign`: your station callsign
        - `latitude`, `longitude`: geographic position of station
        - `hour_quarter`: quarter in which station is transmitting (to be
        deprecated)
        - `above_sea_level`: antenna's height a.s.l.
        - `above_ground_level`: antenna's height a.g.l.
        - `station_range`: station's range in normal conditions, in kilometers
        - `additional_info`: additional information to show on website
        - `service_url`: mapping service url, defaults to SQ9ATK service
    """

    def __init__(
        self,
        callsign,
        hour_quarter,
        above_sea_level,
        above_ground_level,
        station_range,
        additional_info="",
        service_url="",
    ):
        self.__callsign = callsign
        self.__hour_quarter = hour_quarter
        self.__above_sea_level = above_sea_level
        self.__above_ground_level = above_ground_level
        self.__station_range = station_range
        self.__additional_info = additional_info
        self.__service_url = service_url

        self.__logger = logging.getLogger(__name__)

    def get_data(self):
        """This module does NOT return any data! It is here just to say "hello" to
        map utility!"""
        self.__logger.info("::: Przetwarzam dane...")
        station_info = {
            "callsign": self.__callsign,
            "lat": LATITUDE,
            "lon": LONGITUDE,
            "q": self.__hour_quarter,
            "asl": self.__above_sea_level,
            "agl": self.__above_ground_level,
            "range": self.__station_range,
            "info": self.__additional_info,
        }
        dump = json.dumps(station_info, separators=(",", ":"))
        b64data = base64.urlsafe_b64encode(dump.encode())
        url = self.__service_url.encode() + b64data
        url = url.decode()
        self.__logger.info("::: Odpytuję adres: " + url)
        # ----------------------
        for i in range(4):
            try:
                response = requests.get(url, timeout=15).text
                if response != "OK":
                    raise Exception("Non-OK response")
                break
            except Exception as e:
                if i < 3:
                    self.__logger.warning(
                        f"Exception sending data:\n{e}\ntrying again..."
                    )
                else:
                    raise e
        self.__logger.info("::: Dane wysłano, status OK")
        return {"message": None, "source": ""}
