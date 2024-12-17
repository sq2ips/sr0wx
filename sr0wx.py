#!/usr/bin/env python3

#
#    ____  ____   _____        ____  __
#   / ___||  _ \ / _ \ \      / /\ \/ /
#   \___ \| |_) | | | \ \ /\ / /  \  /
#    ___) |  _ <| |_| |\ V  V /   /  \
#   |____/|_| \_\\___/  \_/\_/   /_/\_\
#
# This is main program file for automatic weather station project;
# codename SR0WX.
#
# This project was originaly created by SQ6JNX in 2009, the project
# was then developed by SQ9ATK who added a lot of modules, around 2023 I (SQ2IPS) started developing it.
# I created also created some modules and also rewriten the code to python 3 and also started writing documentation.
# Almost all longer coments are made by SQ6JNX. You can read documentation/manual at https://github.com/sq2ips/sr0wx/wiki.
#
# =====
# About
# =====
#
# Every automatic station's callsign in Poland (SP) is prefixed by "SR".
# This software is intended to read aloud weather informations (mainly).
# That's why we (or I) called it SR0WX.
#
# Extensions (mentioned above) are called ``modules`` (or ``languages``).
# Main part of SR0WX is called ``core``.
#
# SR0WX consists quite a lot of independent files so I (SQ6JNX) suggest
# reading other manuals (mainly configuration- and internationalization
# manual) in the same time as reading this one. Really.
#
# ============
# Requirements
# ============
#
# SR0WX (core) requires the following packages:
#
# ``os``, ``sys`` and ``time`` doesn't need further explanation, these are
# syandard Python packages.
#
# ``pygame`` [#]_ is a library helpful for game development, this project
# uses it for reading (playing) sound samples. ``config`` is just a
# SR0WX configuration file and it is described separately.
#
# ..[#] www.pygame.org
#
# =========
# Let's go!
# =========
#
# For infrmational purposes script says hello and gives local time/date,
# so it will be possible to find out how long script was running.

# Imports

# time measuring
import time
time_start = time.time()

# system and path libs
import os
from pathlib import Path

# this i a trick that changes system dir to dir of this file for fixing problems with locating other files
os.chdir("/".join(str(os.path.realpath(__file__)).split("/")[:-1]))

# logging libraries
import logging.config
import logging
import coloredlogs

from datetime import datetime, timedelta
import pause

# requests for checking internet connection
import requests

# system, getopt and inspect libs for getting command line args and modules
import sys
import getopt
import inspect

# subprocess lib for executing git commands to check version
import subprocess

# multiprocessing for modules
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing.context import TimeoutError

# pygame for playing audio
import pygame

# glob for checking cache
import glob

# socket for checking for other program instances
import socket

# colorcodes
from colorcodes import *

LICENSE = (
    COLOR_OKBLUE
    + """

Copyright 2009-2014 Michal Sadowski (sq6jnx at hamradio dot pl)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-----------------------------------------------------------

You can find full list of contributors on github.com/sq6jnx/sr0wx.py

"""
    + COLOR_ENDC
)

def run_module(args):
    module, logger, aux, = args
    if not aux:
        logger.info(
            COLOR_OKBLUE
            + f"starting {str(module)}..."
            + COLOR_ENDC
        )
    e = None
    
    try:
        module_data = module.get_data()
    except Exception as e:
        logger.exception(f"Exception when running {module}: {e}")
        return {module: [e, None]}
    else:
        return {module: [None, module_data]}

#
# All datas returned by SR0WX modules will be stored in ``data`` variable.


# Information about which modules are to be executed is written in SR0WX
# config file. Program starts every single of them and appends it's return
# value in ``data`` variable. As you can see every module is started with
# language variable, which is also defined in configuration.
# Refer configuration and internationalization manuals for further
# informations.
#
# Modules may be also given in commandline, separated by a comma.

# Args

config = None

test_mode = False
modules_text = None
saveAudioOverwrite = False
all_modules = False
showSamplesOverwrite = False
startTime = None

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, "c:m:tsafw:")

for opt, arg in opts:
    if opt in "-c":
        if arg[-3:] == ".py":
            arg = arg[:-3]
        config = __import__(arg)
    elif opt in "-m":
        modules_text = arg.split(",")
    elif opt == "-t":
        test_mode = True
    elif opt == "-s":
        saveAudioOverwrite = True
    elif opt == "-a":
        all_modules = True
    elif opt == "-f":
        showSamplesOverwrite = True
    elif opt == "-w":
        startTime = arg

if config is None:
    import config as config

# Logger

logging.config.dictConfig(config.dict_log_config)
logger = logging.getLogger(__name__)

logger.info(COLOR_WARNING + "sr0wx.py started" + COLOR_ENDC)
# logger.info(LICENSE)
logger.info(COLOR_OKBLUE + f"For documentation see {config.upstream_url}/wiki")

# Checking for another instacnces
try:
    s = socket.socket()
    s.bind((socket.gethostname(), 56432))
except OSError:
    logger.error("Another sr0wx instance is running, exiting...")
    exit(1)

if test_mode:
    logger.info(COLOR_WARNING + "Test mode active" + COLOR_ENDC)

# command line modules
if all_modules:
    modules = config.modules_all
elif modules_text is not None:
    modules = [None for _ in modules_text]
    for m in config.modules_all:
        if inspect.getfile(m.__class__).split("/")[-1][:-3] in modules_text:
            modules[modules_text.index(inspect.getfile(m.__class__).split("/")[-1][:-3])] = m
    modules = [m for m in modules if m is not None]
    if modules == []:
        logger.error("No valid modules given in commandline, exiting...")
        exit(1)
else:
    modules = config.modules

# aux modules
if config.aux_modules_inversion:
    aux_modules = {**config.aux_modules, **{v: k for k, v in config.aux_modules.items()}}
else:
    aux_modules = config.aux_modules

# internet connection
offline_mode = False
try:
    logger.info("Checking internet connection...")
    requests.get("http://google.com", timeout=15)
except (requests.ConnectionError, requests.ReadTimeout) as e:
    logger.error(
        COLOR_FAIL + f"No internet connection, got error {e}, offline mode active" + COLOR_ENDC + "\n"
    )
    offline_mode = True
    modules = config.offline_modules
else:
    logger.info(COLOR_OKGREEN + "Connection OK" + COLOR_ENDC)

# updates
if config.check_for_updates and not offline_mode:
    try:
        logger.info("Checking for newer version availability...")
        branch = subprocess.check_output("git --no-pager branch".split()).decode().split("\n")

        for b in branch:
            if "*" in b:
                branch = "".join(b.replace("*", "").split())
                break

        local_hash = subprocess.check_output('git --no-pager log --format="%H" -n 1'.split()).decode().replace("\"", "")
        local_hash.replace("\n", "")
        local_hash = "".join(local_hash.split())

        global_hash = subprocess.check_output(f"git ls-remote {config.upstream_url}".split() + [branch]).decode().split()[0]

        if local_hash == global_hash:
            logger.info("Version is up to date.")
        else:
            logger.warning("Newer version is available, use 'git pull' to update.")

    except Exception as e:
        logger.error(f"Unable to check newer version availability, got error: {e}")

# cache
logger.info("Checking cache...")
if os.path.exists("cache/"):
    cache_dir = glob.glob("cache/*")
    if len(cache_dir) > 0:
        logger.info("Clearing cache...")
        for f in cache_dir:
            os.remove(f)
else:
    logger.info("Cache dir does not exists, creating...")
    os.mkdir("cache/")

# lang
lang = config.lang
config.pl_google = lang

# sources
sources = [
    lang.source,
]

time_init = time.time()
# modules launching
messages = []
if config.multi_processing:
    logger.info("multiprocessing is ON\n")

    logger.info("starting modules...")

    args = []

    # list of args: logger and modules
    for module in modules:
        args.append((module, logger, False))

    # Pool and processes map
    with Pool(config.pool_workers) as pool:
        modules_results_map = pool.map_async(run_module, args)
        try:
            modules_results_raw = modules_results_map.get(timeout=config.general_timeout)
        except TimeoutError:
            logger.critical("General timeout exceeded, terminating pool and exiting...")
            pool.terminate()
            exit(1)
    
    # appending returned data to one dict
    modules_results = {}
    for module_result in modules_results_raw:
        modules_results.update(module_result)

    # loop thru all modules
    func_modules = ""
    any_func_modules = False
    for module in modules:
        module_data = None
        
        # if there was not any error
        if modules_results[module][0] is None:
            module_data = modules_results[module][1]
            func_modules += (
                    COLOR_OKGREEN + str(module) + COLOR_ENDC + "\n"
                )
        else:
            func_modules += COLOR_FAIL + str(module) + COLOR_ENDC
            # if there was try running aux module
            if module in aux_modules:
                if aux_modules[module] not in modules:
                    logger.info(
                        COLOR_OKBLUE
                        + f"Starting auxilary module {aux_modules[module]} for module {module}..."
                        + COLOR_ENDC
                    )
                    module_result = run_module((aux_modules[module], logger, True))
                    if module_result[aux_modules[module]][0] is None:
                        module_data = module_result[aux_modules[module]][1]
                
                    func_modules += " auxilary: "
                    if module_result[aux_modules[module]][0] is not None:
                        func_modules += (
                            COLOR_FAIL
                            + str(aux_modules[module])
                            + COLOR_ENDC
                            + "\n"
                        )
                    else:
                        func_modules += (
                            COLOR_OKGREEN
                            + str(aux_modules[module])
                            + COLOR_ENDC
                            + "\n"
                        )
                else:
                    func_modules += COLOR_WARNING + " auxilary module: " + str(aux_modules[module]) + " already running..." + COLOR_ENDC + "\n"
            else:
                func_modules += "\n"

        # check returned data and append to `messages` varible
        if module_data is not None:
            module_message = module_data.get("message", "")
            module_source = module_data.get("source", "")
            if module_message is not None:
                any_func_modules = True
                messages.append(module_message)
                if module_message != "" and module_source != "":
                    sources.append(module_source)

else:
    logger.info("multiprocessing is OFF\n")
    func_modules = ""
    any_func_modules = False
    for module in modules:
        module_data = run_module((module, logger, False))
        if module_data[module][0] is None:
            module_message = module_data[module][1].get("message", "")
            module_source = module_data[module][1].get("source", "")
        if module_message is None:
            func_modules += COLOR_FAIL + str(module) + COLOR_ENDC + "\n"
        else:
            any_func_modules = True
            func_modules += COLOR_OKGREEN + str(module) + COLOR_ENDC + "\n"
            messages.append(module_message)
        if module_message != "" and module_source != "":
            sources.append(module_source)

time_modules = time.time()

# checking and removing `_` from start and end of module message
modules_messages = []
for msg in messages:
    msg = msg.split()

    start = 0
    for i, m in enumerate(msg):
        if m != "_":
            start = i
            break
    
    end = 0
    for i, m in enumerate(msg[::-1]):
        if m != "_":
            end = len(msg) - i
            break

    modules_messages.append(" ".join(msg[start:end]))

# appending all module messages to `message`
message = " _ ".join(modules_messages)

logger.info(
    COLOR_BOLD
    + "modules ("
    + COLOR_ENDC
    + COLOR_OKGREEN
    + "functioning"
    + COLOR_ENDC
    + COLOR_BOLD
    + " / "
    + COLOR_ENDC
    + COLOR_FAIL
    + "not functioning"
    + COLOR_ENDC
    + COLOR_BOLD
    + "):\n"
    + COLOR_ENDC
    + func_modules
)

if not any_func_modules:
    logger.critical("ERROR: No functioning modules, exiting...")
    exit(1)

# When all the modules finished its' work it's time to ``.split()`` returned
# data. Every element of returned list is actually a filename of a sample.

if offline_mode:
    message = config.data_sources_error_msg + ["_"] + message.split()
else:
    message = config.hello_msg + ["_"] + message.split()

if config.read_sources_msg:
    message += ["_"] + sources
message += ["_"] + config.goodbye_msg

# It's time to init ``pygame``'s mixer (and ``pygame``). Possibly defined
# sound quality is far-too-good (44kHz 16bit, stereo), so you can change it.

pygame.mixer.init(config.samplerate, -16, 2, 1024)

# Next (as a tiny timesaver & memory eater ;) program loads all necessary
# samples into memory. I think that this is better approach than reading
# every single sample from disk in the same moment when it's time to play it.

# Just for debug: our playlist (whole message as a list of filenames)

playlist = []

logger.info("loading sound samples...")

for el in message:
    if "upper" in dir(el):
        playlist.append(el)
    else:
        playlist.append("[sndarray]")

if config.ctcss_tone is not None:
    import numpy

    arr = numpy.array(
        [
            config.ctcss_volume
            * numpy.sin(2.0 * numpy.pi * round(config.ctcss_tone) * x / 16000)
            for x in range(0, 16000)
        ]
    ).astype(numpy.int16)
    arr2 = numpy.c_[arr, arr]
    ctcss = pygame.sndarray.make_sound(arr2)
    logger.info(COLOR_WARNING + f"CTCSS tone {config.ctcss_tone}Hz" + COLOR_ENDC)
    ctcss.play(-1)
else:
    logger.info(COLOR_WARNING + "CTCSS tone disabled" + COLOR_ENDC)

logger.info(f"playlist elements: {playlist}")

logger.info("Checking samples...")

sound_samples = {}
for el in message:
    if "upper" in dir(el):
        if el[0:7] == "file://":
            sound_samples[el] = pygame.mixer.Sound(el[7:])
        sample = "".join([config.lang_name, "/samples/", el, ".ogg"])
        if el != "_" and el not in sound_samples:
            if not os.path.isfile(sample):
                logger.warning(COLOR_FAIL + f"Couldn't find {sample}" + COLOR_ENDC)
                sound_samples[el] = pygame.mixer.Sound(
                    config.lang_name + "/samples/beep.ogg"
                )
            else:
                sound_samples[el] = pygame.mixer.Sound(sample)

if test_mode:
    logger.warning("Test mode active, exiting...")
    exit(0)

time_wait_2 = 0
time_wait_1 = 0
if startTime is not None:
    time_wait_1 = time.time()
    try:
        startTime = int(startTime)
        if not (0 <= startTime <= 60):
            raise Exception("Invalid value, should be betwen 0 and 60 (60 for next hour).")
        now = datetime.now()
        if startTime == 60:
            dt_start = now.replace(minute=0, second=0, microsecond=0)
            dt_start += timedelta(hours=1)
        else:
            dt_start = now.replace(minute=startTime, second=0, microsecond=0)
        if dt_start < now:
            raise Exception("Given time is in the past")
        if (dt_start-now) > timedelta(minutes=config.maxWaitTime):
            raise Exception(f"Given time is bigger than {config.maxWaitTime} minutes")
        logger.info(f"Waiting {dt_start-now} secconds for given time {dt_start}.")
        pause.until(dt_start)
        logger.info("Done.")
    except Exception as e:
        logger.warning(f"Unable to wait for given time, got error: {e}, skipping...")
    time_wait_2 = time.time()

nopi = True
if config.rpi_pin is not None:
    try:
        import RPi.GPIO as GPIO

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(config.rpi_pin, GPIO.OUT)
        GPIO.output(config.rpi_pin, GPIO.HIGH)
        logger.info(COLOR_OKGREEN + f"GPIO PTT: ON, PIN: {config.rpi_pin}" + COLOR_ENDC)
        nopi = False
    except ImportError:
        logger.warning("No Raspberry Pi GPIO module found, skipping...")
    except Exception as e:
        logger.error(f"Unable to turn GPIO ptt on, got error: {e}, skipping...")

# Program should be able to "press PTT" via RS232. See ``config`` for
# details.

if config.serial_port is not None:
    import serial

    try:
        ser = serial.Serial(config.serial_port, config.serial_baud_rate)
        if config.serial_signal == "DTR":
            logger.info(COLOR_OKGREEN + "Serial PTT: DTR: ON" + COLOR_ENDC)
            ser.setDTR(1)
            ser.setRTS(0)
        else:
            logger.info(COLOR_OKGREEN + "Serial PTT: RTS: ON" + COLOR_ENDC)
            ser.setDTR(0)
            ser.setRTS(1)
    except Exception as e:
        logger.error(
            f"Failed to open serial port {config.serial_port}@{config.serial_baud_rate}: {e}"
        )


pygame.time.delay(config.marginDelay)

time_audio = time.time()

# OK, data prepared, samples loaded, let the party begin!
#
# Take a look at ``while`` condition -- program doesn't check if the
# sound had finished played all the time, but only 25 times/sec (default).
# It is because I don't want 100% CPU usage. If you don't have as fast CPU
# as mine (I think you have, though) you can always lower this value.
# Unfortunately, there may be some pauses between samples so "reading
# aloud" will be less natural.

logger.info("playing sound samples...\n")

for el in message:
    if config.showSamples or showSamplesOverwrite:
        print(el, end=" ", flush=True)
    if el == "_":
        pygame.time.wait(config.delayValue)
    else:
        if "upper" in dir(el):
            try:
                voice_channel = sound_samples[el].play()
            except:
                a = 1

        elif "upper" not in dir(el):
            sound = pygame.sndarray.make_sound(el)
            if config.pygame_bug == 1:
                sound = pygame.sndarray.make_sound(
                    pygame.sndarray.array(sound)[
                        : len(pygame.sndarray.array(sound)) / 2
                    ]
                )
            voice_channel = sound.play()
        while voice_channel.get_busy():
            pygame.time.Clock().tick(config.clockTick)
        pygame.time.delay(config.timeDelay)

# The following four lines give us a one second break (for CTCSS, PTT and
# other stuff) before closing the ``pygame`` mixer and display some debug
# informations.

time_playing = time.time()

pygame.time.delay(config.marginDelay)

logger.info(COLOR_WARNING + "finishing...\n" + COLOR_ENDC)

# If we've opened serial it's now time to close it.
try:
    if config.serial_port is not None:
        ser.close()
        logger.info(COLOR_OKGREEN + "Serial PTT: OFF" + COLOR_ENDC)
except NameError:
    # sudo gpasswd --add ${USER} dialout
    logger.exception("Couldn't close serial port")

if not nopi:
    GPIO.output(config.rpi_pin, GPIO.LOW)
    logger.info(COLOR_OKGREEN + f"GPIO PTT: OFF, PIN: {config.rpi_pin}" + COLOR_ENDC)
    GPIO.cleanup()

# Save the message to an audio file

if config.saveAudio or saveAudioOverwrite:
    try:
        logger.info("Importing pydub...")
        from pydub import AudioSegment

        logger.info("Creating samples list...")
        samples = []
        for el in message:
            if el == "_":
                samples.append(AudioSegment.silent(duration=config.delayValue))
            elif "upper" in dir(el):
                if el[0:7] == "file://":
                    sample_full = el[7:]
                sample = "".join([config.lang_name, "/samples/", el, ".ogg"])
                if not os.path.isfile(sample):
                    sample_full = config.lang_name + "/samples/beep.ogg"
                else:
                    sample_full = sample
                samples.append(AudioSegment.from_file(sample_full))
                samples.append(AudioSegment.silent(duration=config.timeDelay))

        logger.info("Combining...")
        samples_combined = sum(samples)

        logger.info(f"Saving message to audio file {config.audioPath}")
        file_handle = samples_combined.export(config.audioPath, format="wav")
        if os.path.exists(config.audioPath):
            logger.info(COLOR_OKGREEN + "Succesfully saved." + COLOR_ENDC)
        else:
            logger.error("Saving ended but file is not present.")
    except Exception as e:
        logger.error(f"Couldn't save message, got error {e}")

logger.info(f"Script was running for {round(time.time()-time_start, 2)} seconds total, in it:\ninitialization - {round(time_init-time_start, 2)}s\nModules - {round(time_modules-time_init, 2)}s\nLoading audio - {round(time_audio-time_modules-(time_wait_2-time_wait_1), 2)}s\nPlaying audio - {round(time_playing-time_audio, 2)}s\nFinishing - {round(time.time()-time_playing, 2)}s")
logger.info(COLOR_WARNING + "goodbye" + COLOR_ENDC)

# Documentation is a good thing when you need to double or triple your
# Lines-Of-Code index ;)
