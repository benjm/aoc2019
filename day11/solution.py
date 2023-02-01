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

BLACK=0
WHITE=1
LEFT=0
RIGHT=1
UP="^"
DN="v"
LF="<"
RT=">"
FACINGS=[UP,RT,DN,LF]
DELTAS={UP:(0,-1),DN:(0,1),RT:(1,0),LF:(-1,0)}

@dataclass(unsafe_hash=True)
class Point:
    x: int
    y: int

@dataclass
class Hull:
    robot: Point
    facing: str
    white_points: set
    painted_points: set

@dataclass
class InputSource:
    hull: Hull
    def getNext(self, inp):
        if self.hull.robot in self.hull.white_points:
            return WHITE
        else:
            return BLACK

program = readFile()
if DEBUG_LEVEL>1: print(f"\t{program.memory}")

def runProgram(input_source,msg=""):
    print(f"running with inputs {input_source}\n{msg}")
    inp=0
    last=None
    while program.isRunning():
        outp,inp = program.nextOp(input_source,inp)
        if outp != None:
            if last != None:
                print(f"OUTP PAIR: {last},{outp}")
                robot = input_source.hull.robot
                # paint
                if last == BLACK:
                    input_source.hull.white_points.discard(robot)
                else:
                    input_source.hull.white_points.add(robot)
                input_source.hull.painted_points.add(robot)
                # turn
                f_i = FACINGS.index(input_source.hull.facing)
                if outp == LEFT:
                    f_i = [f_i-1, len(FACINGS)-1][f_i==0]
                else:
                    f_i = [f_i+1, 0][f_i==len(FACINGS)-1]
                input_source.hull.facing = FACINGS[f_i]
                # move
                dx,dy = DELTAS[input_source.hull.facing]
                input_source.hull.robot = Point(robot.x+dx, robot.y+dy)
                #reset last
                last = None
            else:
                last = outp
        if DEBUG_LEVEL>1: print(f"\t{program.memory}")
    return input_source.hull

hull = runProgram(InputSource(Hull(Point(0,0),UP,set(),set())),"test mode")
print(f"{elapsedTimeMs()} number of panels painted at least once is {len(hull.painted_points)}")

program.reset()
white_points=set()
ORIGIN = Point(0,0)
white_points.add(ORIGIN)
hull = runProgram(InputSource(Hull(ORIGIN,UP,white_points,set())),"test mode")
y_values = [p.y for p in hull.white_points]
x_values = [p.x for p in hull.white_points]
for y in range(min(y_values), max(y_values)+1):
    row=[]
    for x in range(min(x_values), max(x_values)+1):
        c = [".","#"][Point(x,y) in hull.white_points]
        row.append(c)
    print(" ".join(row))

