import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    moons = []
    for line in lines: # <x=-1, y=0, z=2>
        x,y,z = map(lambda xs: int(xs.split("=")[1]),line[1:-1].split(", "))
        moons.append(Moon(Point(x,y,z),Point(0,0,0)))
    return moons

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
    z: int
    def absoluteSum(self):
        return abs(self.x)+abs(self.y)+abs(self.z)

@dataclass
class Moon:
    pos: Point
    vel: Point
    def pot(self):
        return self.pos.absoluteSum()
    def kin(self):
        return self.vel.absoluteSum()
    def energy(self):
        return self.pot() * self.kin()
    def getState(self):
        return (self.pos.x, self.pos.y, self.pos.z, self.vel.x, self.vel.y, self.vel.z)

def getMoonsInitial():
    return readFile()

def getChange(a,b):
    if a>b:
        return -1
    elif a<b:
        return 1
    return 0

def updateVelocity(moons):
    new_moons = []
    for i in range(len(moons)):
        moon = moons[i]
        delta = Point(0,0,0)
        for j in range(len(moons)):
            if j!=i:
                other = moons[j]
                dx = getChange(moon.pos.x, other.pos.x)
                dy = getChange(moon.pos.y, other.pos.y)
                dz = getChange(moon.pos.z, other.pos.z)
                delta = Point(delta.x+dx, delta.y+dy, delta.z+dz)
        vel = Point(moon.vel.x+delta.x, moon.vel.y+delta.y, moon.vel.z+delta.z)
        new_moon = Moon(moon.pos, vel)
        new_moons.append(new_moon)
    return new_moons

def updatePositions(moons):
    new_moons = []
    for moon in moons:
        pos = Point(moon.pos.x+moon.vel.x, moon.pos.y+moon.vel.y, moon.pos.z+moon.vel.z)
        new_moon = Moon(pos, moon.vel)
        new_moons.append(new_moon)
    return new_moons

def totalEnergy(moons, steps):
    print(f"{elapsedTimeMs()} simulating {steps} steps...")
    for step in range(steps):
        # print(f"STEP {step}")
        # for moon in moons:
        #     print(f"\t{moon}")
        moons = updateVelocity(moons)
        moons = updatePositions(moons)
    tot_energy = sum(moon.energy() for moon in moons)
    print(f"{elapsedTimeMs()} The moons have tot_energy {tot_energy} after {steps} steps")
    for moon in moons:
        print(f"\t{moon}")

totalEnergy(getMoonsInitial(),1000)

def flattenVectors(moons):
    x = []
    y = []
    z = []
    for moon in moons:
        x.append(moon.pos.x)
        x.append(moon.vel.x)
        y.append(moon.pos.y)
        y.append(moon.vel.y)
        z.append(moon.pos.z)
        z.append(moon.vel.z)
    return tuple(x), tuple(y), tuple(z)

def firstRepeat(moons):
    step=0
    x,y,z = flattenVectors(moons)
    xs=set()
    ys=set()
    zs=set()
    xs.add(x)
    ys.add(y)
    zs.add(z)
    xrep=0
    yrep=0
    zrep=0
    while 0 in [xrep, yrep, zrep]:
        step+=1
        if step%100000 == 0:
            print(f"\t{elapsedTimeMs()} up to step {step}")
        moons = updatePositions(updateVelocity(moons))
        x,y,z = flattenVectors(moons)
        if xrep==0:
            if x in xs:
                xrep=step
            else:
                xs.add(x)
        if yrep==0:
            if y in ys:
                yrep=step
            else:
                ys.add(y)
        if zrep==0:
            if z in zs:
                zrep=step
            else:
                zs.add(z)
    repeatStep = math.lcm(xrep,yrep,zrep)
    print(f"{elapsedTimeMs()} found repeats for each parameter ({xrep},{yrep},{zrep}) giving a lcm {repeatStep}")

firstRepeat(getMoonsInitial())


## commented out first few approaches, then went hunting for a hint:
## "Note that the different dimensions are independent of each other. X's don't depend on y's and z's.""

# def flattenPosVel(moons):
#     pos = []
#     vel = []
#     for moon in moons:
#         pos.append(moon.pos)
#         vel.append(moon.vel)
#     return tuple(pos), tuple(vel), tuple(pos+vel)

# def firstRepeat(moons):
#     pos = {}
#     vel = {}
#     ful = set()
#     step = 0
#     p,v,f = flattenPosVel(moons)
#     pos[p] = step
#     vel[v] = step
#     ful.add(f)
#     seen_f = 0
#     seen_p = 0
#     seen_v = 0
#     while seen_f < 1: #seen_p<1 or seen_v<1:
#         step+=1
#         if step%100000 == 0:
#             print(f"\t{elapsedTimeMs()} up to step {step}")
#         moons = updateVelocity(moons)
#         moons = updatePositions(moons)
#         p,v,f = flattenPosVel(moons)
#         if p in pos:
#             print(f"\tafter {step - pos[p]} steps position {p} repeated")
#             seen_p=step
#         if v in vel:
#             print(f"\tafter {step - vel[v]} steps veocity {v} repeated")
#             seen_v=step
#         if f in ful:
#             seen_f = step
#             print(f"\tmoons repeated a state {f} after {step} steps")
#         pos[p] = step
#         vel[v] = step
#         ful.add(f)

# #firstRepeat(getMoonsInitial())

# def guesstimateOrbits(moons):
#     states = []
#     step = 0
#     orbits=[]
#     for moon in moons:
#         moon_orbits={}
#         moon_states = {moon.getState():step}
#         states.append(moon_states)
#         orbits.append(moon_orbits)

#     p,v,f = flattenPosVel(moons)
#     ful=set()
#     ful.add(f)
#     seen_f = 0
#     while seen_f < 1:
#         step+=1
#         if step%100000 == 0:
#             print(f"\t{elapsedTimeMs()} up to step {step}")
        
#         moons = updateVelocity(moons)
#         moons = updatePositions(moons)

#         p,v,f = flattenPosVel(moons)
#         if f in ful:
#             seen_f = step
#             print(f"\tmoons repeated a state {f} on step {step}")
#         ful.add(f)

#         for i in range(len(moons)):
#             moon = moons[i]
#             moon_state = moon.getState()
#             moon_states = states[i]

#             if moon_state in moon_states:
#                 this_orbit = step - moon_states[moon_state]
#                 moon_orbits = orbits[i]
#                 last_orbit = None
#                 if moon_state in moon_orbits:
#                     last_orbit = moon_orbits[moon_state]
#                 moon_orbits[moon_state] = this_orbit
#                 orbits[i] = moon_orbits
#                 #if i==1:
#                 print(f"\tpotential orbit for moon {i} took {this_orbit} (last time, if applicable it took {last_orbit}) and is in state {moon_state}")

#             moon_states[moon_state] = step
#             states[i] = moon_states

# guesstimateOrbits(getMoonsInitial())