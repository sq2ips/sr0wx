import glob
import shutil
import json
import os
from datetime import datetime, timedelta

import logging
from sr0wx_module import SR0WXModule

class MeteoAprsSq2ips(SR0WXModule):
    def __init__(self, language, path, move_after):
        self.__language = language
        self.__logger = logging.getLogger(__name__)
        self.__path = path
        self.__move_after = move_after

    def parseAprsWeather(self, frame):
        if type(frame) is not str:
            raise TypeError(f"Invalid frame type, expected string got {frame}")
        if len(frame) == 0:
            raise ValueError("Frame is empty")
        
        try:
            (head, body) = frame.split(':', 1)
        except:
            raise ValueError("frame has no body", frame)
        
        if len(body) == 0:
            raise ValueError("frame body is empty", frame)
        
        try:
            (fromcall, path) = head.split('>', 1)
        except:
            raise ValueError("invalid packet header")

        if (not 1 <= len(fromcall) <= 9 or not re.findall(r"^[a-z0-9]{0,9}(\-[a-z0-9]{1,8})?$", fromcall, re.I)):
            raise ParseError("fromcallsign is invalid")
        
        frame_type = body[0]
        body = body[1:]

        if len(body) == 0:
            raise ValueError("frame body is empty after packet type character", frame)
        


        if (frame_type in '!=/@;' or 0 <= body.find('!') < 40) and "_" in body:
            data = body[body.find("_")+1:]
        elif frame_type == "_":
            data = body
        else:
            # ramka nie pogodowa
            return None
        
        data = re.match(r"^([cSgtrpPlLs#][0-9\-\. ]{3}|h[0-9\. ]{2}|b[0-9\. ]{5})+", body)

    def updateFiles(self):
        files = glob.glob("".join([self.__path, "/data/*"]))

        files_frames = {}
        for file in files:
            date_text = file.split()[-1]
            date = datetime.strptime("".join([date_text, "000"]), "%Y%m%d-%H%M%S-%f")
            if (datetime.now() - date) > timedelta(hours=1):
                shutil.move(file, "".join([self.__path, "/data_old/*"]))
            else:
                files_frames[date] = file
        return files_frames

    def getUsedStations(self):
        if os.path.exists("".join([self.__path, "/stations.json"])):
            with open("".join([self.__path, "/stations.json"]), "r") as f:
                stations = json.load(f)
        else:
            self.__logger.warning("file stations.json does not exists, skipping station check...")
        return stations
    
    def saveUsedStations(self, station, stations):
        if not os.path.exists("".join([self.__path, "/stations.json"])):
            self.__logger.info("Creating stations.json...")
        
        stations[datetime.now()] = station

        with open("".join([self.__path, "/stations.json"]), "w") as f:
            json.dump(stations)

    def loadFrames(self, files_frames):
        frames_text = {}
        for date, file in zip(files_frames.keys(), files_frames.values()):
            with open(file, "r") as f:
                frame = f.read().split()[1]
                if frame is "":
                    self.__logger.warning(f"Empty data in frame: {file}, date: {date}")
                else:
                    frames_text[date] = frame
        return frames_text
    
    def parseFrames(self, frames_text):
        frames = {}
        for date, frame in zip(frames_text.keys(), frames_text.values()):
            try:
                parsed = self.parseAprsWeather(frame)
                if parsed is not None:
                    frame_parsed[date] = parsed
            except Exception as e:
                self.__logger.warning(f"Unable to parse frame {frame}, got error {e}")
        
        if len(frames) == 0:
            raise Exception("No weather frames")
        
        return frames
    

    def choseFrame(self, weather_frames):
        frame = weather_frames[min(weather_frames)]
        return frame

    def getWind(self, angle):
        if 0 <= angle <= 23:
            return "polnocny"
        elif 23 <= angle <= 67:
            return "polnocno wschodni"
        elif 67 <= angle <= 112:
            return "wschodni"
        elif 112 <= angle <= 157:
            return "poludniowo wschodni"
        elif 157 <= angle <= 202:
            return "poludniowy"
        elif 202 <= angle <= 247:
            return "poludniowo zachodni"
        elif 247 <= angle <= 292:
            return "zachodni"
        elif 292 <= angle <= 337:
            return "polnocno zachodni"
        elif 337 <= angle <= 360:
            return "polnocny"

    def getWeatherData(self, frame):
        call = frame["from"]

        weather = frame["weather"]

        message = ""

        if "temperatue" in weather:
            message += " ".join(["temperatura", self.__language.read_temperature(round(weather["temperature"])), ""])
        
        if "humidity" in weather:
            message += " ".join(["wilgotnosc", self.__language.read_percent(round(weather["humidity"])), ""])
        
        if "wind_gust" in weather:
            if "wind_direction" in weather:
                message += " ".join(["wiatr", self.getWind(weather["wind_direction"]), self.__language.read_speed(weather["wind_gust"])])
            else:
                message += " ".join(["predkosc_wiatru", self.__language.read_speed()])