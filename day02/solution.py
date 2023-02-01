import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    return list(map(int,lines[0].split(",")))

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

program = readFile()

def runIntCode(program,noun=12,verb=2):
    program[1]=noun
    program[2]=verb
    i = 0
    while program[i] != 99:
        op = program[i]
        addr_a = program[i+1]
        addr_b = program[i+2]
        reg = program[i+3]
        if op == 1:
            program[reg] = program[addr_a] + program[addr_b]
        elif op == 2:
            program[reg] = program[addr_a] * program[addr_b]
        i+=4
    return program[0]

print(elapsedTimeMs(),"starting part1")
res = runIntCode(program)
print(f"{elapsedTimeMs()} result [0] for 1202 = {res}")

def huntForValues(desiredResult):
    for noun in range(100):
        for verb in range(100):
            res = runIntCode(readFile(),noun,verb)
            if res == desiredResult:
                return (noun,verb)

desiredResult=19690720
noun,verb = huntForValues(desiredResult)
print(f"{elapsedTimeMs()} to get result {desiredResult} use noun|verb {noun*100+verb}")
