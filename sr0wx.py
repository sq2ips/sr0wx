#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import requests
import logging.handlers
import logging
from multiprocessing import Process, Pipe
import numpy
import sys
import pygame
import os
import getopt
from colorcodes import *

LICENSE = COLOR_OKBLUE + """

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

""" + COLOR_ENDC


#
#
# ********
# sr0wx.py
# ********
#
# This is main program file for automatic weather station project;
# codename SR0WX.
#
# (At the moment) SR0WX can read METAR [#]_ weather informations and
# is able to read them aloud in Polish. SR0WX is fully extensible, so
# it's easy to make it read any other data in any language (I hope).
#
# .. [#] http://en.wikipedia.org/wiki/METAR
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

# Logging configuration


def setup_logging(config):
    # create formatter and add it to the handlers
    formatter = logging.Formatter(config.log_line_format)

    # Creating logger with the lowest log level in config handlers
    min_log_level = min([h['log_level'] for h in config.log_handlers])
    logger = logging.getLogger()
    logger.setLevel('DEBUG')

    # create logging handlers according to its definitions
    for handler_definition in config.log_handlers:
        handler = handler_definition['class'](**handler_definition['config'])
        handler.setLevel(handler_definition['log_level'])
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

#
# All datas returned by SR0WX modules will be stored in ``data`` variable.


message = " "

# Information about which modules are to be executed is written in SR0WX
# config file. Program starts every single of them and appends it's return
# value in ``data`` variable. As you can see every module is started with
# language variable, which is also defined in configuration.
# Refer configuration and internationalization manuals for further
# informations.
#
# Modules may be also given in commandline, separated by a comma.

config = None

try:
    if len(sys.argv)>1 and sys.argv[1] == "-t":
        test_mode = True
        opts, args = getopt.getopt(sys.argv[2:], "c:", ["config="])
    else:
        test_mode = False
        opts, args = getopt.getopt(sys.argv[1:], "c:", ["config="])
except getopt.GetoptError:
    pass
for opt, arg in opts:
    if opt in ("-c", "--config"):
        if arg[-3:] == '.py':
            arg = arg[:-3]
        if arg == "config_baltyk":
            import config_baltyk as config
        else:
            config = __import__(arg)


if config is None:
    import config as config

logger = setup_logging(config)

logger.info(COLOR_WARNING + "sr0wx.py started" + COLOR_ENDC)
# logger.info(LICENSE)

if test_mode:
    logger.info(COLOR_WARNING + "Test mode active" + COLOR_ENDC)

if len(args) > 0:
    modules = args[0].split(",")
else:
    modules = config.modules

aux_modules = {**config.aux_modules, **{v: k for k, v in config.aux_modules.items()}}

try:
    logger.info("Checking internet connection...")
    requests.get('http://google.com', timeout=30)
except requests.ConnectionError:
    logger.error(COLOR_FAIL + "No internet connection, offline mode active" + COLOR_ENDC + "\n")
    modules = config.offline_modules
    message += " ".join(config.data_sources_error_msg)
else:
    logger.info("Connection OK")


lang = my_import('.'.join((config.lang, config.lang)))
sources = [lang.source, ]

if config.multi_processing:
    logger.info("multiprocessing is ON\n")
    processes = []
    connections = []
    for module in modules:
        conn1, conn2 = Pipe()
        connections.append(conn1)
        processes.append(Process(target=module.get_data, args=(conn2,)))

    for p in processes:
        logger.info(COLOR_OKBLUE + "starting %s..." + COLOR_ENDC, str(modules[processes.index(p)]))

        p.start()

    for p in processes:
        p.join()

    func_modules = ""
    any_func_modules = False
    for c in connections:
        module_data = c.recv()
        module_message = module_data.get("message", "")
        module_source = module_data.get("source", "")
        if module_message == "":
            func_modules += COLOR_FAIL + str(modules[connections.index(c)]) + COLOR_ENDC
            if modules[connections.index(c)] in aux_modules:
                logger.info(COLOR_OKBLUE + f"Starting auxilary module {aux_modules[modules[connections.index(c)]]} for module {modules[connections.index(c)]}..." + COLOR_ENDC)
                conn1, conn2 = Pipe()
                aux_modules[modules[connections.index(c)]].get_data(conn2)
                module_data = conn1.recv()
                module_message = module_data.get("message", "")
                module_source = module_data.get("source", "")
                func_modules += " auxilary: "
                if module_message == "":
                    func_modules += COLOR_FAIL + str(aux_modules[modules[connections.index(c)]]) + COLOR_ENDC + "\n"
                else:
                    any_func_modules = True
                    func_modules += COLOR_OKGREEN + str(aux_modules[modules[connections.index(c)]]) + COLOR_ENDC + "\n"
                    message = " ".join((message, module_message))     
            else:
                func_modules += "\n"

        elif module_message is None:
            func_modules += COLOR_OKGREEN + str(modules[connections.index(c)]) + COLOR_ENDC + "\n"
        else:
            any_func_modules = True
            func_modules += COLOR_OKGREEN + str(modules[connections.index(c)]) + COLOR_ENDC + "\n"
            message = " ".join((message, module_message))
        if module_message != "" and module_source != "":
            sources.append(module_data['source'])
else:
    logger.info("multiprocessing is OFF\n")
    func_modules = ""
    any_func_modules = False
    for module in modules:
        logger.info(COLOR_OKBLUE + "starting %s..." + COLOR_ENDC, module)
        conn1, conn2 = Pipe()
        module.get_data(conn2)
        module_data = conn1.recv()
        module_message = module_data.get("message", "")
        module_source = module_data.get("source", "")
        if module_message == "":
            func_modules += COLOR_FAIL + str(module) + COLOR_ENDC + "\n"
        elif module_message == None:
            func_modules += COLOR_OKGREEN + str(module) + COLOR_ENDC + "\n"
        else:
            any_func_modules = True
            func_modules += COLOR_OKGREEN + str(module) + COLOR_ENDC + "\n"
            message = " ".join((message, module_message))
        if module_message != "" and module_source != "":
            sources.append(module_data['source'])


logger.info(COLOR_BOLD + "modules (" + COLOR_ENDC + COLOR_OKGREEN + "functioning" + COLOR_ENDC + COLOR_BOLD + " / " +
            COLOR_ENDC + COLOR_FAIL + "not functioning" + COLOR_ENDC + COLOR_BOLD + "):\n" + COLOR_ENDC + func_modules)

if not any_func_modules:
    logger.critical(
        COLOR_FAIL + "ERROR: No functioning modules, exiting..." + COLOR_ENDC)
    exit(1)
# When all the modules finished its' work it's time to ``.split()`` returned
# data. Every element of returned list is actually a filename of a sample.

message = config.hello_msg + message.split()
if hasattr(config, 'read_sources_msg'):
    if config.read_sources_msg:
        if len(sources) > 1:
            message += sources
else:
    message += sources
message += config.goodbye_msg

if test_mode:
    logger.info(COLOR_WARNING + "Test mode active, exiting..." + COLOR_ENDC)
    exit(0)

# It's time to init ``pygame``'s mixer (and ``pygame``). Possibly defined
# sound quality is far-too-good (44kHz 16bit, stereo), so you can change it.

pygame.mixer.init(44000, -16, 2, 1024)

# Next (as a tiny timesaver & memory eater ;) program loads all necessary
# samples into memory. I think that this is better approach than reading
# every single sample from disk in the same moment when it's time to play it.

# Just for debug: our playlist (whole message as a list of filenames)

playlist = []

for el in message:
    if "upper" in dir(el):
        playlist.append(el)
    else:
        playlist.append("[sndarray]")

if hasattr(config, 'ctcss_tone'):
    volume = 25000
    arr = numpy.array([volume * numpy.sin(2.0 * numpy.pi * round(config.ctcss_tone)
                      * x / 16000) for x in range(0, 16000)]).astype(numpy.int16)
    arr2 = numpy.c_[arr, arr]
    ctcss = pygame.sndarray.make_sound(arr2)
    logger.info(COLOR_WARNING + "CTCSS tone %sHz" +
                COLOR_ENDC + "\n", "%.1f" % config.ctcss_tone)
    ctcss.play(-1)
else:
    logger.info(COLOR_WARNING + "CTCSS tone disabled" + COLOR_ENDC)

logger.info("playlist elements: %s", " ".join(playlist)+"\n")
logger.info("loading sound samples...")
logger.info("playing sound samples\n")

sound_samples = {}
for el in message:
    if "upper" in dir(el):
        if el[0:7] == 'file://':
            sound_samples[el] = pygame.mixer.Sound(el[7:])

        if el != "_" and el not in sound_samples:
            if not os.path.isfile(config.lang + "/" + el + ".ogg"):
                logger.warning(COLOR_FAIL + "Couldn't find %s" %
                               (config.lang + "/" + el + ".ogg" + COLOR_ENDC))
                sound_samples[el] = pygame.mixer.Sound(
                    config.lang + "/beep.ogg")
            else:
                sound_samples[el] = pygame.mixer.Sound(
                    config.lang + "/" + el + ".ogg")

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
        logger.warning(COLOR_WARNING + "No Raspberry Pi GPIO module found, skipping..." + COLOR_ENDC)
    except Exception as e:
        logger.error(COLOR_FAIL + f"Unable to turn GPIO ptt on, got error: {e}, skipping...")


# Program should be able to "press PTT" via RSS232. See ``config`` for
# details.

if config.serial_port is not None:

    import serial
    try:
        ser = serial.Serial(config.serial_port, config.serial_baud_rate)
        if config.serial_signal == 'DTR':
            logger.info(COLOR_OKGREEN + "DTR/PTT set to ON\n" + COLOR_ENDC)
            ser.setDTR(1)
            ser.setRTS(0)
        else:
            logger.info(COLOR_OKGREEN + "RTS/PTT set to ON\n" + COLOR_ENDC)
            ser.setDTR(0)
            ser.setRTS(1)
    except Exception as e:
        logger.error(COLOR_FAIL + f"Failed to open serial port {config.serial_port}@{config.serial_baud_rate}: {e}" + COLOR_ENDC)


pygame.time.delay(500)

# OK, data prepared, samples loaded, let the party begin!
#
# Take a look at ``while`` condition -- program doesn't check if the
# sound had finished played all the time, but only 25 times/sec (default).
# It is because I don't want 100% CPU usage. If you don't have as fast CPU
# as mine (I think you have, though) you can always lower this value.
# Unfortunately, there may be some pauses between samples so "reading
# aloud" will be less natural.

for el in message:
    #print(el) # wyświetlanie nazw sampli
    if el == "_":
        pygame.time.wait(500)
    else:
        if "upper" in dir(el):
            try:
                voice_channel = sound_samples[el].play()
            except:
                a = 1

        elif "upper" not in dir(el):
            sound = pygame.sndarray.make_sound(el)
            if config.pygame_bug == 1:
                sound = pygame.sndarray.make_sound(pygame.sndarray.array(
                    sound)[:len(pygame.sndarray.array(sound))/2])
            voice_channel = sound.play()
        while voice_channel.get_busy():
            pygame.time.Clock().tick(25)

# Possibly the argument of ``pygame.time.Clock().tick()`` should be in
# config file...
#
# The following four lines give us a one second break (for CTCSS, PTT and
# other stuff) before closing the ``pygame`` mixer and display some debug
# informations.

logger.info(COLOR_WARNING + "finishing...\n" + COLOR_ENDC)

pygame.time.delay(500)

# If we've opened serial it's now time to close it.
try:
    if config.serial_port is not None:
        ser.close()
        logger.info(COLOR_OKGREEN + "RTS/PTT set to OFF\n" + COLOR_ENDC)
except NameError:
    # sudo gpasswd --add ${USER} dialout
    logger.exception(COLOR_FAIL + "Couldn't close serial port" + COLOR_ENDC)

if not nopi:
    GPIO.output(config.rpi_pin, GPIO.LOW)
    logger.info(COLOR_OKGREEN + f"GPIO PTT: OFF, PIN: {config.rpi_pin}" + COLOR_ENDC)
    GPIO.cleanup()


logger.info(COLOR_WARNING + "goodbye" + COLOR_ENDC)

# Documentation is a good thing when you need to double or triple your
# Lines-Of-Code index ;)
