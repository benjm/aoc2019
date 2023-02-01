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

    def copy(self):
        return Program(self.code.copy(), self.ip, self.base, self.memory.copy())

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

    def nextOp(self, input_source):
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
            nextInput = input_source.getNext()
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
        return outp

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


@dataclass(unsafe_hash=True)
class Point:
    x: int
    y: int
    def copy(self):
        return Point(self.x, self.y)
    def alterBy(self, delta):
        return Point(self.x+delta.x, self.y+delta.y)

@dataclass
class InputSource:
    inp: int
    def getNext(self):
        return self.inp

@dataclass
class Droid:
    point: Point
    program: Program
    def copy(self):
        return Droid(self.point.copy(), self.program.copy())

NORTH=1
SOUTH=2
EAST=4
WEST=3

DIRECTIONS=[NORTH, SOUTH, EAST, WEST]

RIGHT_OF={
    NORTH:EAST,
    SOUTH:WEST,
    EAST:SOUTH,
    WEST:NORTH
}

LEFT_OF={
    NORTH:WEST,
    SOUTH:EAST,
    EAST:NORTH,
    WEST:SOUTH
}

BEHIND_OF={
    NORTH:SOUTH,
    SOUTH:NORTH,
    EAST:WEST,
    WEST:EAST
}

DELTA={
    NORTH:Point( 0,-1),
    SOUTH:Point( 0, 1),
    EAST: Point( 1, 0),
    WEST: Point(-1, 0)
}

BLOCKED=0
MOVED=1
OXYGEN=2

ORIGIN=Point(0,0)

def printKnown(known, walls, oxygen, droids=[]):
    droid_points = set(d.point for d in droids)
    if len(known) == 0:
        return
    min_y = min(p.y for p in known)
    max_y = max(p.y for p in known)
    min_x = min(p.x for p in known)
    max_x = max(p.x for p in known)
    print("KNOWN SPACE")
    for y in range(min_y, max_y+1):
        row=[]
        for x in range(min_x, max_x+1):
            p = Point(x,y)
            if p in walls:
                row.append("#")
            elif p == oxygen:
                row.append("O")
            elif p in droid_points:
                row.append("d")
            elif p == ORIGIN:
                row.append("x")
            elif p in known:
                row.append(".")
            else:
                row.append(" ")
        print(" ".join(row))
    print()

program = readFile()

def floodSearch(program, start_point, known=set(), walls=set()):
    oxygen_program=None
    oxygen=None
    steps=0
    steps_to_oxygen=0
    active_droids=[Droid(start_point, program.copy())]
    while len(active_droids)>0:
        if steps%1000==0:
            print(f"after {steps} steps there are {len(active_droids)} active droids, {len(walls)} walls and {len(known)} known points in space")
            # after 265000 steps there are 61 active droids, 886381 walls and 35811749 known points in space
            # ...something is not right...
        steps+=1
        new_droids = []
        for droid in active_droids:
            # try each direction from the droid
            for direction in DIRECTIONS:
                next_point = droid.point.alterBy(DELTA[direction])
                if next_point not in known:
                    known.add(next_point)
                    new_droid = droid.copy()
                    outp = None
                    while (outp==None):
                        outp = new_droid.program.nextOp(InputSource(direction))
                    if outp == BLOCKED:
                        walls.add(next_point)
                    elif outp in [MOVED, OXYGEN]:
                        new_droid.point = next_point
                        new_droids.append(new_droid)
                        if outp == OXYGEN:
                            oxygen = next_point
                            if steps_to_oxygen < 1:
                                steps_to_oxygen = steps
                                oxygen_program = new_droid.program.copy()
                    else:
                        raise Exception(f"borked - got output = {outp}")
        active_droids = new_droids
    printKnown(known, walls, oxygen, [])
    return steps_to_oxygen, steps-1, oxygen, walls, oxygen_program

min_steps, max_steps, oxygen, walls, oxygen_program = floodSearch(program, ORIGIN)
print(f"{elapsedTimeMs()} minimum steps to reach oxygen: {min_steps}")
#finally realised need to keep the program that was at the oxygen in order to use the same logic to backtrack
min_steps, max_steps, oxygen, walls, oxygen_program = floodSearch(oxygen_program, oxygen, walls.copy(), walls.copy())
print(f"{elapsedTimeMs()} time to fill with oxygen: {max_steps}")

# def runProgram(program, droid):
#     min_point=droid.copy()
#     max_point=droid.copy()
#     been=set()
#     walls=set()
#     start_wall_following=None
#     oxygen=None
#     outp=-1
#     input_source=InputSource(NORTH)
#     wall_following=False
#     n=0
#     while program.isRunning():
#         n+=1
#         if n>1000:
#             print("too many turns...")
#             printKnown(min_point,max_point,walls,been,oxygen)
#             print(been)
#             exit()
#         been.add(droid.copy())
#         outp = program.nextOp(input_source)
#         direction = input_source.getNext()
#         if outp != BLOCKED:
#             droid = droid.alterBy(DELTA[direction])
#         max_point = Point(max(max_point.x, droid.x), max(max_point.y, droid.y))
#         min_point = Point(min(min_point.x, droid.x), min(min_point.y, droid.y))
#         left_of = droid.alterBy(DELTA[LEFT_OF[direction]])
#         right_of = droid.alterBy(DELTA[RIGHT_OF[direction]])
#         ahead_of = droid.alterBy(DELTA[direction])
#         behind_of = droid.alterBy(DELTA[BEHIND_OF[direction]])
#         if outp == MOVED:
#             if droid == start_wall_following:
#                 print("back to the point where we started following the walls")
#                 printKnown(min_point,max_point,walls,been,oxygen)
#                 exit()
#             if wall_following:
#                 if left_of not in walls:
#                     input_source=InputSource(LEFT_OF[direction])
#                 elif ahead_of not in walls:
#                     pass # continue in same direction
#                 elif right_of not in walls:
#                     input_source=InputSource(RIGHT_OF[direction])
#                 else:
#                     input_source=InputSource(BEHIND_OF[direction])
#             else:
#                 pass # continue in same direction until hit a wall    
#         elif outp == BLOCKED:
#             if not wall_following:
#                 start_wall_following=droid.copy()
#             wall_following = True
#             walls.add(ahead_of)
#             if right_of not in walls:
#                 input_source=InputSource(RIGHT_OF[direction])
#             elif behind_of not in walls:
#                 input_source=InputSource(BEHIND_OF[direction])
#             else:
#                 input_source=InputSource(LEFT_OF[direction])
#         elif outp == OXYGEN:
#             oxygen = droid.copy()
#             print("found the oxygen")
#             printKnown(min_point,max_point,walls,been,oxygen)
#             exit()
#     return outp

# runProgram(program, ORIGIN)


