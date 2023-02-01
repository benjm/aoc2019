import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    #process, convert, etc etc
    return list(map(int,lines[0]))

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

BASE = [0, 1, 0, -1]

# @dataclass(unsafe_hash=True)
# class Point:
#     x: int
#     y: int

print(elapsedTimeMs(),"starting part1")

def modBase(base,i,cut_at):
    signal = []
    for b in base:
        signal += [b]*i
    while len(signal)<cut_at+1:
        signal+=signal
    return signal[1:cut_at+1]

def fft(phases):
    length = len(phases)
    new_phases=[]
    for i in range(length):
        signal = modBase(BASE,i+1, length)
        mod_phases = [phases[j] * signal[j] for j in range(length)]
        x = int(str(sum(mod_phases))[-1])
        new_phases.append(x)
    return new_phases

def fftRepeat(phases,repeats,iterations):
    phases*=repeats
    for i in range(iterations):
        if i%10==0:
            print(f"\t{elapsedTimeMs()} up to phase update {i}")
        phases = fft(phases)
    return phases

def decode(phases):
    addr = int("".join(map(str,phases[:7])))
    print(f"first 7 digits: {phases[:7]} gives address {addr}")
    res = int("".join(map(str,phases[addr:addr+7])))


phases = readFile()
repeats = 1
if len(sys.argv)>2:
    repeats = int(sys.argv[2])
iterations = 100

print(f"{elapsedTimeMs()} running phase * {repeats} for {iterations} iterations")
phases = fftRepeat(phases,repeats,iterations)
print(elapsedTimeMs(),"result, first 8 digits:","".join(map(str,phases[:8])))
# 0:00:02.825193 result, first 8 digits: 37153056

# def buildBases(length):
#     bases={}
#     for i in range(length):
#         base = modBase(BASE, i+1, length)
#         bases[i] = base
#     return bases


# def fftSpecific(phases,repeats,iterations,start,finish):
#     phases*=repeats
#     length = len(phases)
#     bases = buildBases(length)
#     signal = None
#     for i in range(iterations):
#         if signal:
#             signal = [signal[j] * base[j] for j in range(length)]
#         else:
#             signal = bases[0].copy()
#     print(signal)

# fftSpecific(phases,repeats,iterations,0,8)

