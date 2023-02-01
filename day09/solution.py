import sys
import math
import itertools
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

DEBUG_LEVEL = 0

@dataclass
class Program:
    code: list
    ip: int
    base: int
    memory: dict

    def reset(self):
        self.ip = 0
        self.base = 0
        self.mem = {}
        for i in range(len(self.code)):
            self.mem[i] = self.code[i]

    def read(self, addr):
        if addr < 0:
            raise Exception(f"error - attempted to read from {addr}")
        return self.memory.get(addr, 0)

    def write(self, op, param_num, value):
        addr = self.read(self.ip+param_num)
        if op[3-param_num] == "2":
            addr = self.base + addr
        if addr < 0:
            raise Exception(f"error - attempted to write to {addr}")
        self.memory[addr] = value

    def isRunning(self):
        return (not self.isHalted())

    def isHalted(self):
        return self.read(self.ip) == 99

    def getParam(self,op,param_num):
        p_val = self.read(self.ip+param_num)
        if op[3-param_num] == "1": #immediate mode
            return p_val
        elif op[3-param_num] == "2": #relative mode
            return self.read(self.base + p_val)
        else:
            return self.read(p_val)

    def nextOp(self, inputs=[], inp=0):
        op = str(self.memory[self.ip]).zfill(5)
        if DEBUG_LEVEL>1: print(f"\tOP: {op}")
        outp = None
        op_i = int(op[3:])
        if op_i == 1: # ADD
            value = self.getParam(op,1) + self.getParam(op,2)
            self.write(op, 3, value)
            self.ip+=4
        elif op_i == 2: # MUL
            value = self.getParam(op,1) * self.getParam(op,2)
            self.write(op, 3, value)
            self.ip+=4
        elif op_i == 3: # INP
            nextInput = inputs[inp]
            inp+=1
            if nextInput == None:
                raise Exception("Error: no input provided for input operation")
            self.write(op, 1, nextInput)
            self.ip+=2
        elif op_i == 4: # OUTP
            outp = self.getParam(op,1)
            self.ip+=2
        elif op_i == 5:
            if self.getParam(op,1) != 0:
                self.ip = self.getParam(op,2)
            else:
                self.ip+=3
        elif op_i == 6:
            if self.getParam(op,1) == 0:
                self.ip = self.getParam(op,2)
            else:
                self.ip+=3
        elif op_i == 7:
            value = int(self.getParam(op,1) < self.getParam(op,2))
            self.write(op, 3, value)
            self.ip+=4
        elif op_i == 8:
            value = int(self.getParam(op,1) == self.getParam(op,2))
            self.write(op, 3, value)
            self.ip+=4
        elif op_i == 9:
            self.base+=self.getParam(op,1)
            self.ip+=2
        else:
            raise Exception(f"unknown operation {op} at ip {self.ip}\n\t{self}")
        return outp, inp

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    code = list(map(int,lines[0].split(",")))
    memory = {}
    for addr in range(len(code)):
        memory[addr] = code[addr]
    return Program(code,0,0,memory)

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

program = readFile()
if DEBUG_LEVEL>1: print(f"\t{program.memory}")

def runProgram(inputs,msg=""):
    print(f"running with inputs {inputs}\n{msg}")
    inp=0
    while program.isRunning():
        outp,inp = program.nextOp(inputs,inp)
        if outp != None:
            print(f"OUTP: {outp}")
        if DEBUG_LEVEL>1: print(f"\t{program.memory}")

runProgram([1],"test mode")
program.reset()
runProgram([2],"BOOST mode")


