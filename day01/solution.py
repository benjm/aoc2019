import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    return list(map(int,lines))

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

modules = readFile()

total_fuel = 0
total_fuel_fuel = 0
for module in modules:
    module_fuel = (module//3) - 2
    if module_fuel>0:
        total_fuel+=module_fuel
    fuel_fuel_needed = (module_fuel//3)-2
    while fuel_fuel_needed > 0 :
        total_fuel_fuel+=fuel_fuel_needed
        fuel_fuel_needed = (fuel_fuel_needed//3)-2

print(f"{elapsedTimeMs()}\n\ttotal fuel required for justthe modules is {total_fuel}\n\ttotal extra for the fuel itself is {total_fuel_fuel}\n\tfor overall fuel required {total_fuel_fuel + total_fuel}")

