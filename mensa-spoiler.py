#!/usr/bin/python3
import sys

class Spoiler:
    # fancy data model
    begin = 0
    length = 0
    def __str__(self):
        return f"{self.begin}:{self.length}:SPOILER"

# read stdin
input = sys.stdin.read()


# search for spoiler tags
offset = 0
while input.find("<spoiler>", offset) != -1:
    # spoiler repr
    spoiler = Spoiler()
    # start pos of spoiler tag
    pos = input.find("<spoiler>", offset)
    spoiler.begin = pos
    # remove spoiler begin tag
    input = input.replace("<spoiler>", "", 1)
    # find closing tag
    pos = input.find("</spoiler>", offset)
    spoiler.length = pos - spoiler.begin
    # remove spoiler end tag
    input = input.replace("</spoiler>", "", 1)
    # prepare next round
    offset = pos
    # debug output
    print(spoiler)
