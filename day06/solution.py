import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    orbits={}
    for line in lines:
        com,orb = line.split(")")
        orbs = orbits.get(com,[])
        orbs.append(orb)
        orbits[com]=orbs
    return orbits

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

COM="COM"
YOU="YOU"
SAN="SAN"
orbits = readFile()

print(elapsedTimeMs(),"starting part1")
def countEveryOrbit(orbits,COM):
    ends=set()
    ends.add(COM)
    depth=0
    count=0
    while len(ends) > 0:
        depth+=1
        new_ends=set()
        for end in ends:
            new_ends.update(orbits.get(end,[]))
        count+=len(new_ends)*depth
        ends = new_ends
    return count

count = countEveryOrbit(orbits,COM)
print(f"{elapsedTimeMs()} counted {count} orbits")

print(elapsedTimeMs(),"starting part2")

def numberOfHops(YOU,youPath,SAN,sanPath):
    for node in youPath[::-1]:
        if node in sanPath:
            print("common node:",node)
            backtrack = len(youPath) - youPath.index(node)
            fwdtrack = len(sanPath) - sanPath.index(node)
            return backtrack+fwdtrack-4
    return -1

def transferDistance(orbits,COM,YOU,SAN):
    youPath=None
    sanPath=None
    paths=[]
    paths.append([COM])
    depth=0
    count=0
    while len(paths) > 0:
        depth+=1
        new_paths=[]
        for path in paths:
            end = path[-1]
            for new_end in orbits.get(end,[]):
                new_path = path.copy()
                new_path.append(new_end)
                new_paths.append(new_path)
                if new_end == YOU:
                    youPath = new_path
                elif new_end == SAN:
                    sanPath = new_path
        count+=len(new_paths)*depth
        paths = new_paths
    distance = numberOfHops(YOU,youPath,SAN,sanPath)
    return count,distance

count,dist = transferDistance(orbits,COM,YOU,SAN)
print(f"{elapsedTimeMs()} counted {count} orbits and number of xfers to get to same orbit as SAN: {dist}")