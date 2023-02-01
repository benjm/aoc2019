import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines

lines = readFile()

def testInt(i,printStuff=False):
    s = str(i)
    if len(s) != 6:
        if printStuff: print("\nnot 6 digits")
        return False
    n = -1
    k = 0
    dbl = False
    for c in s:
        ic = int(c)
        if ic < n:
            if printStuff: print("\ndecreasing digit")
            return False
        if ic == n:
            k+=1
        else:
            if k==1:
                dbl = True
            k = 0
        n = ic
    if k==1:
        dbl = True
    if (not dbl) and printStuff: print("\nno double")
    return dbl


if len(lines)>1:
    for line in lines:
        print(f"testing {line} --> {testInt(int(line),True)}")

print(elapsedTimeMs(),"starting part1")
if len(lines) == 1:
    s,e = map(int,lines[0].split("-"))
    tot=0
    for i in range(s,e+1):
        if testInt(i):
            tot+=1
    print(f"There are {tot} valid passwords in range {lines[0]}")


# print(elapsedTimeMs(),"starting part2")
