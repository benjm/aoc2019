import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    #process, convert, etc etc
    return lines

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

data = readFile()

# @dataclass(unsafe_hash=True)
# class Point:
#     x: int
#     y: int

print(elapsedTimeMs(),"starting part1")


# print(elapsedTimeMs(),"starting part2")
