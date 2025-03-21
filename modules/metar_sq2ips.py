import logging

import requests
import feedparser
from datetime import datetime, timezone

from sr0wx_module import SR0WXModule

class MetarSq2ips(SR0WXModule):
    def __init__(self, language, service_url, service_urns, airport):
        self.__language = language
        self.__service_url = service_url
        self.__service_urns = service_urns
        self.__airport = airport
        self.__logger = logging.getLogger(__name__)

        self.__cloud_intens = {'SKC': 0, 'FEW': 20, 'STC': 40, 'BKN': 75, 'OVC': 100}
        self.__phenom_codes = ['DZ', 'RA', 'SN', 'SG', 'PL', 'GR', 'GS', 'UP', 'BR', 'FG', 'FU', 'VA', 'DU', 'SA', 'HZ', 'PO', 'SQ', 'FC', 'SS', 'DS', 'MI', 'BC', 'PR', 'DR', 'BL', 'SH', 'TS', 'FZ', 'VC']

    def get_metar(self):
        metars = []
        for urn in self.__service_urns:
            try:
                metar_data = self.requestData(f"{self.__service_url}/{urn}?airport={self.__airport}", self.__logger, 15, 3)

                parsed_rss = feedparser.parse(metar_data.text)
                title = parsed_rss["entries"][0]['title']
                metar = parsed_rss["entries"][0]['summary']
                if metar == '':
                    raise Exception("Empty data. Wrong airport code?")
                metar = metar[:-1].split()
                if metar[0] != 'METAR':
                    raise Exception("ERROR invalid data")

                metars.append(metar[1:])
            except Exception as e:
                self.__logger.warning(f"Error while getting data from {urn}: {e}")

        return metars

    def parse_metar(self, metar):
        metar_data = {'COR': False, 'NIL': False, 'AUTO': False, 'phenoms': []}

        if metar[0] == 'COR':
            metar_data["COR"] = True
            metar = metar[1:]

        if metar[0] == 'NIL':
            metar_data['NIL'] = True
            exit(0)

        metar_data["ICAO"] = metar[0]

        metar_time = datetime.strptime(metar[1], "%d%H%MZ")
        metar_data["time"] = datetime.now(timezone.utc).replace(day=metar_time.day, hour=metar_time.hour, minute=metar_time.minute, second=0, microsecond=0) # UTC

        for m in metar[2:]:
            try:
                if m == 'AUTO': # auto observation flag
                    metar_data['AUTO'] = True
                # wind data
                elif len(m) >= 7 and m[-2:] == 'KT': 
                    metar_data["wind_dir"] = m[0:3] # in deg
                    if metar_data["wind_dir"] != 'VRB':
                        metar_data["wind_dir"] = int(metar_data["wind_dir"])
                    metar_data["wind"] = int(m[3:5]) # in knot
                    if 'G' in m:
                        metar_data["wind_gust"] = int(m[6:8])
                # wind edge directions
                elif len(m) == 7 and m[3] == 'V':
                    metar_data["wind_edge_min"] = int(m[0:3])
                    metar_data["wind_edge_max"] = int(m[4:])
                # visibility
                elif len(m) == 4 and m.isdecimal():
                    metar_data["vis"] = int(m)
                # directional visibility
                elif len(m) == 5 and m[4] in ['N', 'S', 'E', 'W'] and m[:4].isdigit():
                    metar_data["vis_dir_val"] = int(m[:-1])
                    metar_data['vis_dir'] = m[-1]
                # vertical visibility
                elif len(m)==5 and m[:2] == 'VV':
                    metar_data['v_vis'] = int(m[2:])
                # visibility flag
                elif m in ['CAVOK', 'NSC', 'NCD']:
                    metar_data["vis"] = m
                # phenoms
                elif True in [p in m for p in self.__phenom_codes]:
                    if m[0] in ['+', '-']:
                        sign = m[0]
                        m = m[1:]
                    else:
                        sign = None

                    phenoms = []

                    phenoms.append(sign)

                    if len(m) == 2:
                        if m in self.__phenom_codes:
                            phenoms.append(m)
                        else:
                            raise ValueError("Invalid phenom: {m}")
                    elif len(m) == 4:
                        if m[0:2] in self.__phenom_codes and m[2:4] in self.__phenom_codes:
                            phenoms.append(m[0:2])
                            phenoms.append(m[2:4])
                        else:
                            raise ValueError("Invalid phenom: {m}")
                    else:
                        raise ValueError("Invalid length of phenom: {m}")

                    metar_data['phenoms'].append(phenoms)
                # clouds
                elif len(m)>=6 and m[0:3] in self.__cloud_intens:
                    metar_data["clouds"] = self.__cloud_intens[m[0:3]]
                    metar_data["clouds_ground"] = int(m[3:6])
                    if len(m) >= 8 and m[6:] in ['CB', 'TCU']:
                        metar_data["clouds_type"] = m[6:]
                # temperature data
                elif m.count('/') == 1 and len(m) <= 7 and 'R' not in m:
                    temp = []
                    for t in m.replace('M', '-').split('/'):
                        temp.append(int(t))

                    metar_data['temp'] = temp[0]
                    metar_data['temp_dwp'] = temp[1]
                # pressure
                elif len(m) >= 4 and m[0] == 'Q':
                    metar_data['press'] = int(m[1:])

                else:
                    print(f"WARNING: unparsed element: {m}")
            except Exception as e:
                print(f"ERROR while parsing {m}: {e}")

        return metar_data
    
    def get_text(metar_obj):
        # time
        metar_obj["time"]

        # airport
        metar_obj["airport"]

        # preweather info
        if metar_obj['COR']:
            ...
        if metar_obj['NIL']:
            ...
        if metar_obj['AUTO']:
            ...
        
        # temp
        if "temp" in metar_obj:
            ...
        
        # wind
        if "wind" in metar_obj:
            ...
        
        # pressure
        if "press" in metar_obj:
            ...
        
        # wind edge
        if "wind_edge_min" in metar_obj:
            ...
        
        # visibility
        if "vis" in metar_obj:
            ...
        
        # directional visibility
        if "vis_dir" in metar_obj:
            ...
        
        # vertical visibility
        if "v_vis" in metar_obj:
            ...
        
        # phenoms
        if metar_obj["phenoms"] != []:
            ...

        # clouds
        if "clouds" in metar_obj:
            ...
        


    def get_data(self):
        self.__logger.info("::: Downloading metar data...")
        metars = self.get_metar()

        if metars == []:
            raise Exception("No valid data got.")
        else:
            self.__logger.info(f"Number of correct frames got: {len(metars)}")

        self.__logger.info("::: Parsing metar data...")
        parsed_metars = []
        for m in metars:
            parsed_metars.append(self.parse_metar(m))

        td = [(datetime.now(timezone.utc) - p["time"]) for p in parsed_metars]

        n_metar = parsed_metars[td.index(min(td))]

        self.__logger.info(f"Latest metar data from: {datetime.strftime(n_metar["time"], "%d.%m.%Y %H:%M UTC")}")

        print(n_metar)
        exit(0)

