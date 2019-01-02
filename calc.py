import diff_calc
import requests
import pp_calc
import sys
import b_info
import configparser
from beatmap import Beatmap


def mod_str(mod):
    string = ""
    if mod.nf:
        string += "NF"
    if mod.ez:
        string += "EZ"
    if mod.hd:
        string += "HD"
    if mod.hr:
        string += "HR"
    if mod.dt:
        string += "DT"
    if mod.ht:
        string += "HT"
    if mod.nc:
        string += "NC"
    if mod.fl:
        string += "FL"
    if mod.so:
        string += "SO"
    return string


class mods:
    def __init__(self):
        self.nomod = 0,
        self.nf = 0
        self.ez = 0
        self.hd = 0
        self.hr = 0
        self.dt = 0
        self.ht = 0
        self.nc = 0
        self.fl = 0
        self.so = 0
        self.speed_changing = self.dt | self.ht | self.nc
        self.map_changing = self.hr | self.ez | self.speed_changing

    def update(self):
        self.speed_changing = self.dt | self.ht | self.nc
        self.map_changing = self.hr | self.ez | self.speed_changing


mod = mods()


def set_mods(mod, m):
    if m == "NF":
        mod.nf = 1
    if m == "EZ":
        mod.ez = 1
    if m == "HD":
        mod.hd = 1
    if m == "HR":
        mod.hr = 1
    if m == "DT":
        mod.dt = 1
    if m == "HT":
        mod.ht = 1
    if m == "NC":
        mod.nc = 1
    if m == "FL":
        mod.fl = 1
    if m == "SO":
        mod.so = 1

def return_beatmap(mod_s, file_name):
    try:
        file = requests.get(b_info.main(file_name)).text.splitlines()
    except:
        print("ERROR: " + file_name + " not a valid beatmap")
        sys.exit(1)

    map = Beatmap(file)

    mod.dt = 0
    mod.ez = 0
    mod.fl = 0
    mod.hd = 0
    mod.hr = 0
    mod.ht = 0
    mod.nc = 0
    mod.nf = 0
    mod.so = 0

    if mod_s != "":
        mod_s = [mod_s[i:i + 2] for i in range(0, len(mod_s), 2)]
        for m in mod_s:
            set_mods(mod, m)
            mod.update()

    map.apply_mods(mod)

    return map

def return_values(c100_s, c50_s, misses_s, combo_s, file_name, mod_s):
    try:
        file = requests.get(b_info.main(file_name)).text.splitlines()
    except:
        print("ERROR: " + file_name + " not a valid beatmap")
        sys.exit(1)

    map = Beatmap(file)

    if combo_s == "":
        combo = map.max_combo
    else:
        combo = int(combo_s)

    mod_s = mod_s.upper()

    mod.dt = 0
    mod.ez = 0
    mod.fl = 0
    mod.hd = 0
    mod.hr = 0
    mod.ht = 0
    mod.nc = 0
    mod.nf = 0
    mod.so = 0

    if mod_s != "":
        mod_s = [mod_s[i:i + 2] for i in range(0, len(mod_s), 2)]
        for m in mod_s:
            set_mods(mod, m)
            mod.update()

    if c100_s == "":
        c100 = 0
    else:
        c100 = int(c100_s)

    if c50_s == "":
        c50 = 0
    else:
        c50 = int(c50_s)

    if misses_s == "":
        misses = 0
    else:
        misses = int(misses_s)

    mod_string = mod_str(mod)
    map.apply_mods(mod)
    diff = diff_calc.main(map)
    pp, aim_value, speed_value, acc_value = pp_calc.pp_calc(diff[0], diff[1], diff[3], misses, c100, c50, mod, combo)

    return pp
