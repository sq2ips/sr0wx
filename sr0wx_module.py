#
#   Copyright 2014 Michal Sadowski (sq6jnx at hamradio dot pl)
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

import warnings

#import requests
from curl_cffi import requests

from colorcodes import *


class SR0WXModule:
    """Base class for SR0WX modules."""

    def __init__(self):
        pass

    def getData(self):
        """Deprecated method. Runs `get_data()`."""
        msg = "Use if getData() is deprecated, use get_data() instead"
        warnings.warn(msg)
        return self.get_data(None)

    def get_data(self, connection):
        """Returns message to be played back by core of sr0wx.py. Not implemented here.

        Modules are expected to return a `dict` with the following keys:
            - `message` -- message text, filled template, etc (currently list of
            samples)
            - `need_ctcss` -- hint for core module whether or not to playback CTCSS tone
        """
        msg = "This method should be implemented in child class"
        raise NotImplementedError(msg)

    def requestData(self, url, logger, timeout=15, repeat=3, headers={}, impersonate="chrome"):
        headers.update({'User-Agent': 'SR0WX/1.0'})
        data = None
        for i in range(repeat):
            try:
                logger.info("::: Requesting data from address: " + url)
                data = requests.get(url, timeout=timeout, headers=headers)
                data.raise_for_status()
                break
            except Exception as e:
                if i < repeat - 1:
                    logger.exception(f"Exception getting data: {e}, trying again...")
                else:
                    raise e
        logger.info("::: Dane pobrano, status OK")
        return data

    def wind_direction_name(self, angle):
        """Return wind direction name in words based on angle in degrees"""
        angle = angle % 360

        if 0 <= angle <= 23:
            return "polnocny"
        elif 23 < angle <= 67:
            return "polnocno wschodni"
        elif 67 < angle <= 112:
            return "wschodni"
        elif 112 < angle <= 157:
            return "poludniowo wschodni"
        elif 157 < angle <= 202:
            return "poludniowy"
        elif 202 < angle <= 247:
            return "poludniowo zachodni"
        elif 247 < angle <= 292:
            return "zachodni"
        elif 292 < angle <= 337:
            return "polnocno zachodni"
        elif 337 < angle <= 360:
            return "polnocny"
