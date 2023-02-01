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
        self.memory = {}
        for i in range(len(self.code)):
            self.memory[i] = self.code[i]

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

    def nextOp(self, input_source, inp=0):
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
            nextInput = input_source.getNext(inp)
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

# 0 is an empty tile. No game object appears in this tile.
# 1 is a wall tile. Walls are indestructible barriers.
# 2 is a block tile. Blocks can be broken by the ball.
# 3 is a horizontal paddle tile. The paddle is indestructible.
# 4 is a ball tile. The ball moves diagonally and bounces off objects.

EMPTY=0
WALL=1 
BLOCK=2 #breakable
PADDLE=3 #horizontal
BALL=4 # moves diagonally, bounces

@dataclass(unsafe_hash=True)
class Point:
    x: int
    y: int

@dataclass
class InputSource:
    joystick: int
    def getNext(self, inp):
        return self.joystick

program = readFile()
if DEBUG_LEVEL>1: print(f"\t{program.memory}")

def runProgram(program,input_source,msg=""):
    print(f"running with inputs {input_source}\n{msg}")
    inp=0
    buffer=[]
    tiles={}
    score=0
    paddle=None
    ball=None
    while program.isRunning():
        if ball and paddle:
            if ball.x == paddle.x:
                input_source.joystick=NEUTRAL
            elif ball.x<paddle.x:
                input_source.joystick=LEFT
            else:
                input_source.joystick=RIGHT
        outp,inp = program.nextOp(input_source,inp)
        if outp != None:
            buffer.append(outp)
            ##TODO ball trajectory & move joystick (inputs)
            if len(buffer) == 3:
                if buffer[0]==-1 and buffer[1]==0:
                    score=buffer[2]
                    print(f"\tscore: {score}")
                else:
                    point = Point(buffer[0], buffer[1])
                    typ = buffer[2]
                    if typ == BALL:
                        ball = point
                        print(f"\t\tball: {point}")
                    elif typ == PADDLE:
                        paddle = point
                        print(f"\t\tpaddle: {point}")
                    tiles[point] = typ
                    #print(f"\t{typ} at {point}")
                buffer=[]
        if DEBUG_LEVEL>1: print(f"\t{program.memory}")
    return tiles,score

LEFT=-1
NEUTRAL=0
RIGHT=1

tiles,score = runProgram(program, InputSource(NEUTRAL))
num_blocks = sum(1 for tile in tiles if tiles[tile]==BLOCK)
print(f"{elapsedTimeMs()} looks like there are {num_blocks} blocks")

program = readFile()
program.code[0] = 2
program.reset()
tiles,score = runProgram(program, InputSource(NEUTRAL))
print(f"{elapsedTimeMs()} got a score of {score}")
