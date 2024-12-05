#!/usr/bin/python3

import urllib.request, urllib.parse
import json
import shutil
import configparser
import argparse
import datetime
import re

# for the future me:
# todo: please implement --save-default 
# and push this shit on github!


# static data
mensas = [
    {"longName": "Mensa Morgenstelle", "shortName": "mmo", "id": 621},
    {"longName": "Mensa Wilhelmsstraße", "shortName": "mwi", "id": 611},
    {"longName": "Mensa Prinz Karl", "shortName": "mpk", "id": 623},
    {"longName": "Cafeteria Morgenstelle", "shortName": "cmo", "id": 724},
    {"longName": "Cafeteria Wilhelmsstraße", "shortName": "cwi", "id": 715},
]

menuComponents = {
    "vegan": "\033[92mvegan\033[00m",
    "v": "\033[32mvegetarisch\033[00m",
    "g": "\033[33mGeflügel\033[00m",
    "s": "\033[91mSchwein\033[00m",
    "r": "\033[31mRind\033[00m",
    "f": "\033[36mFisch\033[00m",
    "so": "\033[37mSoja\033[00m",
}


# command line options
parser = argparse.ArgumentParser()
parser.add_argument("--list-mensas", help="list all available mensas", action="store_true")
parser.add_argument("-m", "--mensa", default="-1", help="id or shortname of chosen mensa (see --list-mensas)")
parser.add_argument("-d", "--date", default="0", help="date offset in days from today to display, e.g. +1 is tomorrow", type=int)
parser.add_argument("--save-default", help="save current settings as default settings in .mensarc", action="store_true")
parser.add_argument("--raw", help="output json array instead of nice human readable text", action="store_true")
args = parser.parse_args()

# list available mensas and exit if --list-mensas was called
if args.list_mensas:
    print("id: shortName (longName)")
    for mensa in mensas:
        print("%3d: %3s (%s)" % (mensa["id"], mensa["shortName"], mensa["longName"]))
    exit(0)

# prepare format string with terminal width awareness
termCols, termRows = shutil.get_terminal_size((80, 20))
fmtMeal = "%% -%ds %% -5s\n \u21AA %%s" % (termCols - 6)
fmtTitle = "{:^%ds}" % (termCols)

# settings
baseUrl = 'https://www.my-stuwe.de/wp-json/mealplans/v1/canteens/%(mensaId)s?lang=de'
rcFile = "/Users/sebastian/.mensarc"
config = configparser.ConfigParser()
config.read(rcFile)

# find mensa
if args.mensa == "-1":
    # --mensa omitted, fallback to .mensarc
    args.mensa = config["DEFAULT"]["mensaId"]
# match mensa
if args.mensa.isnumeric():
    # id submitted
    mensaId = args.mensa
else:
    # shortName submitted
    for mensa in mensas:
        if mensa["shortName"] == args.mensa:
            mensaId = mensa["id"]

# find target date
dateFilter = (datetime.date.today() + datetime.timedelta(days=args.date)).strftime("%Y-%m-%d")

# get static values
mensaShortName = "???"
mensaLongName = "Not Found"
for mensa in mensas:
    if int(mensa["id"]) == int(mensaId):
        mensaShortName = mensa["shortName"]
        mensaLongName = mensa["longName"]


if args.save_default:
    config["DEFAULT"]["mensaId"] = str(mensaId)
    with open(rcFile, 'w') as configfile:
        config.write(configfile)
    print("new default config saved to .mensarc")

# BEGIN PROCESSING AND OUTPUT SECTION
# read json from server
reqUrl = baseUrl % {"mensaId": mensaId}
req = urllib.request.urlopen(reqUrl)
rawJson = req.read().decode('cp1252')
mensaInfo = json.loads(rawJson)

# filter by date
menus = mensaInfo[str(mensaId)]["menus"]
menus = list(filter(lambda menu: (menu["menuDate"] == dateFilter), menus))

if args.raw:
    # raw json output
    print(menus)
    quit()

# normal (nice) output
print(fmtTitle.format("=== M E N Ü P L A N ==="))
print(fmtTitle.format(mensaLongName))
print(fmtTitle.format(dateFilter))
print("")

# print meals
rx = re.compile(r" \[.+?\]", re.IGNORECASE)
for menu in menus:
    # meal components
    components = []
    for component in menu["icons"]:
        try:
            components.append(menuComponents[component.lower()])
        except KeyError:
            components.append(component.lower())
    # remove components from menu line
    menu["menu"] = list(map(lambda entry: rx.sub("", entry), menu["menu"]))
    # output menu line
    if len(menu["menu"]) == 0:
        menuLine = menu["menuLine"]
    else:
        menuLine = ", ".join(menu["menu"])
    print(fmtMeal % (
        menuLine,
        menu["studentPrice"],
        " ".join(components)
    ))

