# -*- coding: utf-8 -*-
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

import datetime
import sys

sys.path.append("./pyliczba/")

import pyliczba

def _(text): return text.replace(" ", "_")


def ra(value): return value.lower()\
    .replace("ą", "a")\
    .replace("ć", "c")\
    .replace("ę", "e")\
    .replace("ł", "l")\
    .replace("ń", "n")\
    .replace("ó", "o")\
    .replace("ś", "s")\
    .replace("Ś", "s")\
    .replace("ź", "z")\
    .replace("ż", "z")


class SR0WXLanguage(object):
    def __init__(self):
        """Nothing here for now."""
        pass


class PLGoogle(SR0WXLanguage):
    def __init__(self):
        pass

    def trim_pl(self, text): return "".join(
        text.lower()
        .replace("ą", "a_")
        .replace("ć", "c_")
        .replace("ę", "e_")
        .replace("ł", "l_")
        .replace("ń", "n_")
        .replace("ó", "o_")
        .replace("ś", "s_")
        .replace("ź", "x_")
        .replace("ż", "z_")
        .replace(":", "")
        .replace(",", "")
        .replace(".", "")
        .replace(" - ", "_")
        .replace("/", " ")
        .replace("\\", " ")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "_")
        .split()
    )

    def read_number(self, value, units=None):
        """Converts numbers to text."""
        if units is None:
            retval = pyliczba.lslownie(abs(value))
        else:
            retval = pyliczba.cosslownie(abs(value), units)

        if retval.startswith("jeden tysiąc"):
            retval = retval.replace("jeden tysiąc", "tysiąc")
        if value < 0:
            retval = " ".join(("minus", retval))

        return ra(retval)

    def read_number_higher_degree(self, f):
        d = {
            "0": "zera",
            "1": "jeden",
            "2": "dwoch",
            "3": "trzech",
            "4": "czterech",
            "5": "pieciu",
            "6": "szesciu",
            "7": "siedmiu",
            "8": "osmiu",
            "9": "dziewieciu",
            "10": "dziesieciu",
            "11": "jedenastu",
            "12": "dwunastu",
            "13": "trzynastu",
            "14": "czternastu",
            "15": "pietnastu",
            "16": "szesnastu",
            "17": "siedemnastu",
            "18": "osiemnastu",
            "19": "dziewietnastu",
            "20": "dwudziestu",
            "30": "trzydziestu",
            "40": "czterdziestu",
            "50": "piecdziesieciu",
            "60": "szejscdziesieciu",
            "70": "siedemdziesieciu",
            "80": "osiemdziesieciu",
            "90": "dziewiecdziesieciu",
            "100": "stu",
            "200": "dwustu",
            "300": "trzystu",
            "400": "czterystu",
            "500": "pieciuset",
            "600": "szesciuset",
            "700": "siedmiuset",
            "800": "osmiuset",
            "900": "dziewieciuset",
        }
        text = ""
        if int(f) < 0:
            f = abs(f)
            text += "minus "
        f = str(f)
        if len(f) == 1:
            if f == "1":
                text += "jednego"
            else:
                text += d[f]
        elif len(f) == 2:
            if f[1] == "0" or f[0] == "1":
                text += d[f]
            else:
                text += d[f[0] + "0"] + " " + d[f[1]]
        elif len(f) == 3:
            if f[1] == "0" and f[2] == "0":
                text += d[f]
            else:
                if f[2] != "0":
                    if f[1] == "0":
                        text += d[f[0] + "00"] + " " + d[f[2]]
                    else:
                        text += (
                            d[f[0] + "00"]
                            + " "
                            + d[f[1] + "0"]
                            + " "
                            + d[f[2]]
                        )
                else:
                    if f[1] == "0":
                        text += d[f[0] + "00"]
                    else:
                        text += (
                            d[f[0] + "00"]
                            + " "
                            + d[f[1] + "0"]
                        )
        return text

    def read_higher_degree(self, f, units):
        text = self.read_number_higher_degree(f)
        unit = None
        if abs(f) == 1:
            unit = units[0]
        else:
            unit = units[1]
        return " ".join(text.split() + [ra(unit)])

    def read_gust(self, n): return read_higher_degree(
        n, [_("kilometra na godzinę"), _("kilometrów na godzinę")])

    def read_pressure(self, value): return self.read_number(
        value, ["hektopaskal", "hektopaskale", "hektopaskali"])

    def read_distance(self, value): return self.read_number(
        value, ["kilometr", "kilometry", "kilometrow"])

    def read_percent(self, value): return self.read_number(
        value, ["procent", "procent", "procent"])

    def read_temperature(self, value): return self.read_number(
        value, [_("stopień Celsjusza"), _("stopnie Celsjusza"), _("stopni Celsjusza")])

    read_speed = lambda self, no, unit="mps": self.read_number(no, {
        "mps": [
            _("metr na sekundę"),
            _("metry na sekundę"),
            _("metrów na sekundę"),
        ],
        "kmph": [
            _("kilometr na godzinę"),
            _("kilometry na godzinę"),
            _("kilometrów na godzinę"),
        ],
    }[unit])

    def read_precipitation(self, value): return self.read_number(
        value, [_("milimetr"), _("milimetry"), _("milimetrów")])

    def read_power(self, value, prefix):
        units = [_("wat"), _("waty"), _("watow")]
        for i, unit in enumerate(units):
            units[i] = "_".join([prefix, unit])
        return self.read_number(value, units)

    def read_degrees(self, value): return self.read_number(
        value, ["stopień", "stopnie", "stopni"])

    def read_micrograms(self, value): return self.read_number(value, [
        "mikrogram na_metr_szes_cienny",
        "mikrogramy na_metr_szes_cienny",
        "mikrogramo_w na_metr_szes_cienny",
    ])

    def read_decimal(self, value):
        deg100 = [
            "setna",
            "setne",
            "setnych",
        ]

        deg10 = [
            "dziesia_ta",
            "dziesia_te",
            "dziesia_tych",
        ]
        if value >= 10:
            return self.read_number(value, deg100)
        else:
            return self.read_number(value, deg10)

    def read_direction(self, value, short=False):
        directions = {
            "N": ("północno", "północny"),
            "E": ("wschodnio", "wschodni"),
            "W": ("zachodnio", "zachodni"),
            "S": ("południowo", "południowy"),
        }
        if short:
            value = value[-2:]
        print("-".join(
            [
                directions[d][0 if i < 0 else 1]
                for i, d in enumerate(value, -len(value) + 1)
            ]
        ))
        return "-".join(
            [
                directions[d][0 if i < 0 else 1]
                for i, d in enumerate(value, -len(value) + 1)
            ]
        )

    def read_validity_hour(self, hour):
        hours = [
            "godzine",
            "godziny",
            "godzin",
        ]
        if hour == 1:
            return hours[0]
        elif hour == 2:
            return " ".join(["dwie", hours[1]])
        else:
            return self.read_number(hour, hours)

    def read_datetime(self, value, out_fmt, in_fmt=None):
        if type(value) != datetime.datetime and in_fmt is not None:
            value = datetime.datetime.strptime(value, in_fmt)
        elif type(value) == datetime.datetime:
            pass
        else:
            raise TypeError(
                "Either datetime must be supplied or both " "value and in_fmt"
            )

        MONTHS = [
            "",
            "stycznia",
            "lutego",
            "marca",
            "kwietnia",
            "maja",
            "czerwca",
            "lipca",
            "sierpnia",
            "września",
            "października",
            "listopada",
            "grudnia",
        ]

        DAYS_N0 = [
            "",
            "",
            "dwudziestego",
            "trzydziestego",
        ]
        DAYS_N = [
            "",
            "pierwszego",
            "drugiego",
            "trzeciego",
            "czwartego",
            "piątego",
            "szóstego",
            "siódmego",
            "ósmego",
            "dziewiątego",
            "dziesiątego",
            "jedenastego",
            "dwunastego",
            "trzynastego",
            "czternastego",
            "piętnastego",
            "szesnastego",
            "siedemnastego",
            "osiemnastego",
            "dziewiętnastego",
        ]
        HOURS = [
            "zero",
            "pierwsza",
            "druga",
            "trzecia",
            "czwarta",
            "piąta",
            "szósta",
            "siódma",
            "ósma",
            "dziewiąta",
            "dziesiąta",
            "jedenasta",
            "dwunasta",
            "trzynasta",
            "czternasta",
            "piętnasta",
            "szesnasta",
            "siedemnasta",
            "osiemnasta",
            "dziewiętnasta",
            "dwudziesta",
        ]

        _, tm_mon, tm_mday, tm_hour, tm_min, _, _, _, _ = value.timetuple()
        retval = []
        for word in out_fmt.split(" "):
            if word == "%d":  # Day of the month
                if tm_mday <= 20:
                    retval.append(DAYS_N[tm_mday])
                else:
                    retval.append(DAYS_N0[tm_mday // 10])
                    retval.append(DAYS_N[tm_mday % 10])
            elif word == "%B":  # Month as locale’s full name
                retval.append(MONTHS[tm_mon])
            elif word == "%H":  # Hour (24-hour clock) as a decimal number
                if tm_hour <= 20:
                    retval.append(HOURS[tm_hour])
                elif tm_hour > 20:
                    retval.append(HOURS[20])
                    retval.append(HOURS[tm_hour - 20])
            elif word == "%M":  # Minute as a decimal number
                if tm_min == 0:
                    retval.append("zero-zero")
                else:
                    retval.append(self.read_number(tm_min))
            elif word.startswith("%"):
                raise ValueError("Token %s' is not supported!", word)
            else:
                retval.append(word)
        return ra(" ".join((w for w in retval if w != "")))

    def read_callsign(self, value):
        # literowanie polskie wg. "Krótkofalarstwo i radiokomunikacja - poradnik",
        # Łukasz Komsta SQ8QED, Wydawnictwa Komunikacji i Łączności Warszawa, 2001,
        # str. 130
        LETTERS = {
            "a": "adam",
            "b": "barbara",
            "c": "celina",
            "d": "dorota",
            "e": "edward",
            "f": "franciszek",
            "g": "gustaw",
            "h": "henryk",
            "i": "irena",
            "j": "józef",
            "k": "karol",
            "l": "ludwik",
            "m": "marek",
            "n": "natalia",
            "o": "olga",
            "p": "paweł",
            "q": "quebec",
            "r": "roman",
            "s": "stefan",
            "t": "tadeusz",
            "u": "urszula",
            "v": "violetta",
            "w": "wacław",
            "x": "xawery",
            "y": "ypsilon",
            "z": "zygmunt",
            "/": "łamane",
        }
        retval = []
        for char in value.lower():
            try:
                retval.append(LETTERS[char])
            except KeyError:
                try:
                    retval.append(self.read_number(int(char)))
                except ValueError:
                    raise ValueError('"%s" is not a element of callsign', char)
        return " ".join(retval)


# to be removed from code
source = "zrodlo"

pl = PLGoogle()

trim_pl = pl.trim_pl
read_number = pl.read_number
read_pressure = pl.read_pressure
read_distance = pl.read_distance
read_percent = pl.read_percent
read_temperature = pl.read_temperature
read_speed = pl.read_speed
read_gust = pl.read_gust
read_precipitation = pl.read_precipitation
read_degrees = pl.read_degrees
read_micrograms = pl.read_micrograms
read_decimal = pl.read_decimal
read_direction = pl.read_direction
read_validity_hour = pl.read_validity_hour
read_datetime = pl.read_datetime
read_callsign = pl.read_callsign
read_power = pl.read_power
read_higher_degree = pl.read_higher_degree
