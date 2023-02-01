import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

@dataclass
class Point:
    x: int
    y: int
    def dist(self,other):
        return abs(self.x-other.x)+abs(self.y-other.y)

@dataclass
class Line:
    a: Point
    b: Point
    stepsBefore: int

@dataclass
class Wire:
    horizontals: list
    verticals: list

DELTAS = {
    "R":(1,0),
    "L":(-1,0),
    "U":(0,1),
    "D":(0,-1)
}

def buildWire(twists):
    horizontals = []
    verticals = []
    current=Point(0,0)
    stepsBefore = 0
    for twist in twists:
        dirn = twist[0]
        delta = DELTAS[dirn]
        dist = int(twist[1:])
        x = current.x + delta[0] * dist
        y = current.y + delta[1] * dist
        destination = Point(x,y)
        line = Line(current,destination,stepsBefore)
        stepsBefore+=dist
        if dirn in ["U","D"]:
            verticals.append(line)
        else:
            horizontals.append(line)
        current=destination
    return Wire(horizontals, verticals)

def processLines(lines):
    wires=[]
    wires.append(buildWire(list(lines[0].split(","))))
    wires.append(buildWire(list(lines[1].split(","))))
    return wires

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

wires = readFile()

print(elapsedTimeMs(),"starting part1")
PORT = Point(0,0)

def getIntersect(hor,ver):
    if hor.a.y <= max(ver.a.y, ver.b.y) and hor.a.y >= min(ver.a.y, ver.b.y) and ver.a.x <= max(hor.a.x, hor.b.x) and ver.a.x >= min(hor.a.x, hor.b.x):
        return Point(ver.a.x, hor.a.y)
    # print(hor.a.y,"<=",max(ver.a.y, ver.b.y),"\n",hor.a.y," >= ",min(ver.a.y, ver.b.y) ,"\n", ver.a.x ,"<=", max(hor.a.x, hor.b.x) ,"\n", ver.a.x ,">=", min(hor.a.x, hor.b.x))
    return None
# intersect = getIntersect(Line(Point(0,0),Point(10,0)), Line(Point(5,-5),Point(5,5)))
# print(intersect)
# exit()
def closestIntersect(wires):
    wire_a, wire_b = wires
    closest_intersect = None
    least_steps_intersect = None
    least_steps = None
    for hor in wire_a.horizontals:
        for ver in wire_b.verticals:
            intersect = getIntersect(hor,ver)
            if intersect and intersect != PORT:
                if closest_intersect:
                    if closest_intersect.dist(PORT) > intersect.dist(PORT):
                        closest_intersect = intersect
                else:
                    closest_intersect = intersect

                steps = hor.stepsBefore + intersect.dist(hor.a) + ver.stepsBefore + intersect.dist(ver.a)
                if least_steps:
                    if least_steps > steps:
                        least_steps = steps
                        least_steps_intersect = intersect
                else:
                    least_steps = steps
                    least_steps_intersect = intersect
    for ver in wire_a.verticals:
        for hor in wire_b.horizontals:
            intersect = getIntersect(hor,ver)
            if intersect and intersect != PORT:
                if closest_intersect:
                    if closest_intersect.dist(PORT) > intersect.dist(PORT):
                        closest_intersect = intersect
                else:
                    closest_intersect = intersect

                steps = hor.stepsBefore + intersect.dist(hor.a) + ver.stepsBefore + intersect.dist(ver.a)
                if least_steps:
                    if least_steps > steps:
                        least_steps = steps
                        least_steps_intersect = intersect
                else:
                    least_steps = steps
                    least_steps_intersect = intersect
    return closest_intersect,least_steps_intersect,least_steps
closest_intersect,least_steps_intersect,least_steps = closestIntersect(wires)
print(f"{elapsedTimeMs()} closest intersect at {closest_intersect} with a distance of {closest_intersect.dist(PORT)}")
print(f"{elapsedTimeMs()} least lag intersect at {least_steps_intersect} with a step count of {least_steps}")

# print(elapsedTimeMs(),"starting part2")
