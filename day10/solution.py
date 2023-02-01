import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

@dataclass(unsafe_hash=True)
class Point:
    x: int
    y: int

@dataclass
class Space:
    asteroids: list
    height: int
    width: int

def processLines(lines):
    asteroids=[]
    height=len(lines)
    width=len(lines[0])
    for y in range(height):
        line = lines[y]
        for x in range(width):
            if line[x] == "#":
                asteroids.append(Point(x,y))
    return Space(asteroids,height,width)

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

space = readFile()

def hasLineOfSight(asteroid, other, space):
    checks=[]
    if other.x == asteroid.x:
        x = other.x
        for y in range(min(other.y, asteroid.y)+1, max(other.y, asteroid.y)):
            point = Point(x,y)
            if point in space.asteroids:
                #print(f"hit {point} between {asteroid} and {other}")
                return False
    elif other.y == asteroid.y:
        y = other.y
        for x in range(min(other.x, asteroid.x)+1, max(other.x, asteroid.x)):
            point = Point(x,y)
            if point in space.asteroids:
                #print(f"hit {point} between {asteroid} and {other}")
                return False
    else:
        dx = other.x - asteroid.x
        dy = other.y - asteroid.y
        for d in range(2,min(abs(dx), abs(dy))+1):
            if abs(dx)%d == 0 and abs(dy)%d == 0:
                for m in range(1,d):
                    x = asteroid.x + (m*dx//d)
                    y = asteroid.y + (m*dy//d)
                    point = Point(x,y)
                    if point in space.asteroids:
                        #print(f"hit {point} between {asteroid} and {other}")
                        return False

    return True

def findVisibleOthers(asteroid, others, space):
    visible=[]
    for other in others:
        if hasLineOfSight(asteroid, other, space):
            visible.append(other)
    return visible

def printVisibleSpace(space, visibleCount):
    pad = len(str(max(visibleCount.values())))
    for y in range(space.height):
        row=[]
        for x in range(space.width):
            count = visibleCount.get(Point(x,y),0)
            if count>0:
                row.append(str(count))
            else:
                row.append("."*pad)
        print(" ".join(row))

def canSeeMostOthers(space):
    visibleCount = {}
    for asteroid in space.asteroids:
        visibleCount[asteroid] = 0
    for a_i in range(len(space.asteroids)-1):
        asteroid = space.asteroids[a_i]
        others = space.asteroids[a_i+1:]
        visibleOthers = findVisibleOthers(asteroid, others, space)
        visibleCount[asteroid]+=len(visibleOthers)
        for other in visibleOthers:
            visibleCount[other]+=1

    printVisibleSpace(space, visibleCount)

    highest_visible = 0
    best_point = None
    for asteroid in visibleCount:
        count = visibleCount[asteroid]
        if count > highest_visible:
            highest_visible = count
            best_point = asteroid
    return best_point, highest_visible


laser, highest_visible = canSeeMostOthers(space)
print(f"best point is at {laser} which can see {highest_visible}")

@dataclass
class Delta:
    dx: int
    dy: int
    h: int
    w: int

def firstHit(laser,delta,space,vapourised):
    x = laser.x+delta.x
    y = laser.y+delta.y
    point = Point(x,y)
    while space.contains(point):
        if point in space.asteroids and point not in vapourised:
            return point
        x+=delta.x
        y+=delta.y
        point = Point(x,y)
    return None

def nextDelta(laser,delta,space):
    next_delta = None
    if delta.x==0 and delta.y==-1: # N
        return Delta(1,-laser.y)
    elif delta.x==1 and delta.y==-1: # NE
        return Delta(-1,-1)
    # imagine four squares all with the common point of the laser.
    # each square has a side length of the sum of the distance of the laser from the two edges
    # 
    return next_target


def vapourise(laser, space, nth):
    vapourised=set()
    delta = Delta(0,-1,space.height, space.width) # straight up
    zaps = 0
    last=None
    while len(vapourised) < nth:
        gone = firstHit(laser,delta,space,vapourised)
        if gone:
            nth_gone = gone
            vapourised.add(gone)
            print(f"\tvapourised #{len(vapourised)} as position {nth_gone}")
        delta = delta.nextDelta(laser,delta)
    return nth_gone

#winner = vapourise(best_point, space, 200)

def calcAngle(centre, point):
        dx = point.x - centre.x
        dy = point.y - centre.y
        # quadrants matter for clockwise rotation
        theta = None
        if dx==0: #N/S
            theta = [180,0][dy<0]
        elif dy==0: #E/W
            theta = [270,90][dx>0]
        elif dx>0 and dy<0: #NE
            theta = math.degrees(math.atan(abs(dx)/abs(dy)))
        elif dx<0 and dy>0: #SW
            theta = 180 + math.degrees(math.atan(abs(dx)/abs(dy)))
        elif dx>0 and dy>0: #SE
            theta = 90 + math.degrees(math.atan(abs(dy)/abs(dx)))
        elif dx<0 and dy<0: #SE
            theta = 270 + math.degrees(math.atan(abs(dy)/abs(dx)))
        return round(theta,2)

def pointsByAngle(laser, space):
    angle_to_points = {}
    for point in space.asteroids:
        if point != laser:
            angle = calcAngle(laser,point)
            points = angle_to_points.get(angle, [])
            points.append(point)
            if len(points)>1:
                points = sorted(points, key=lambda p: abs(p.x-laser.x)+abs(p.y-laser.y))
            angle_to_points[angle] = points
    return angle_to_points

def find_nth_vapourised(laser, space, nth):
    angle_to_points = pointsByAngle(laser, space)
    vapourised = set()
    last = None
    while len(vapourised) < nth and len(angle_to_points) > 0:
        new_angle_to_points={}
        for angle in sorted(angle_to_points):
            points = angle_to_points[angle]
            last = points[0]
            vapourised.add(last)
            if len(vapourised) == nth:
                return last
            if len(points) > 1:
                new_angle_to_points[angle] = points[1:]
        angle_to_points = new_angle_to_points
    return None

nth_vapourised = find_nth_vapourised(laser, space, 200)
print(f"{elapsedTimeMs()} the 200th points to be vapourised is {nth_vapourised} which has a result value of {nth_vapourised.x * 100 + nth_vapourised.y}")

