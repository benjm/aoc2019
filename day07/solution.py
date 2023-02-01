import sys
import math
import itertools
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

DEBUG_LEVEL = 0

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

def getParam(program,i,op,param_num):
    p_val = program[i+param_num]
    if op[3-param_num] == "1": #immediate mode
        return p_val
    return program[p_val]

def putValue(program,i,put_val):
    addr = program[i]
    program[addr] = put_val
    return program

def nextOp(program,i,inputs):
    inp=0
    op = str(program[i]).zfill(5)
    op_i = int(op[3:])
    outp=None
    if op_i == 1: # ADD
        param1 = getParam(program,i,op,1)
        param2 = getParam(program,i,op,2)
        add_val = param1 + param2
        program = putValue(program,i+3,add_val)
        if DEBUG_LEVEL>0: print(f"\tIP={i}, op={op} ({param1}, {param2}, {add_val})")
        i+=4
    elif op_i == 2: # MUL
        param1 = getParam(program,i,op,1)
        param2 = getParam(program,i,op,2)
        mul_val = param1 * param2
        program = putValue(program,i+3,mul_val)
        if DEBUG_LEVEL>0: print(f"\tIP={i}, op={op} ({param1}, {param2}, {mul_val})")
        i+=4
    elif op_i == 3: # INP
        inp_val = inputs[inp]
        if DEBUG_LEVEL>0: print(f"\tinputting {inp_val} for instruction {i}")
        inp+=1
        program = putValue(program,i+1,inp_val)
        i+=2
    elif op_i == 4: # OUTP
        param1 = getParam(program,i,op,1)
        if DEBUG_LEVEL>0: print(f"\tOUTP: {param1}")
        outp=param1
        i+=2
    elif op_i == 5: #jump-if-true (if param1 is non-zero set i to param2)
        param1 = getParam(program,i,op,1)
        param2 = getParam(program,i,op,2)
        if DEBUG_LEVEL>0: print(f"\tIP={i}, op={op} ({param1}, {param2})")
        i = [i+3, param2][param1 != 0]
    elif op_i == 6: #jump-if-false (if param1 is zero set i to param2)
        param1 = getParam(program,i,op,1)
        param2 = getParam(program,i,op,2)
        if DEBUG_LEVEL>0: print(f"\tIP={i}, op={op} ({param1}, {param2})")
        i = [i+3, param2][param1 == 0]
    elif op_i == 7: #less-than (if param1 < param2 set param3 to 1)
        param1 = getParam(program,i,op,1)
        param2 = getParam(program,i,op,2)
        put_val = int(param1 < param2)
        program = putValue(program,i+3,put_val)
        if DEBUG_LEVEL>0: print(f"\tIP={i}, op={op} ({param1}, {param2}, {put_val})")
        i+=4
    elif op_i == 8: #equals (if param1 == param2 set param3 to 1)
        param1 = getParam(program,i,op,1)
        param2 = getParam(program,i,op,2)
        put_val=int(param1 == param2)
        program = putValue(program,i+3,put_val)
        if DEBUG_LEVEL>0: print(f"\tIP={i}, op={op} ({param1}, {param2}, {put_val})")
        i+=4
    else:
        raise Exception(f"confused by {op}")
    if DEBUG_LEVEL>1: print(f"\t{program}")
    return program,i,outp,inputs[inp:]

def runIntCode(program,inputs,i=0):
    n = 0
    been={}
    while program[i] != 99:
        program,i,outp,inputs = nextOp(program,i,inputs)
        if outp != None:
            if DEBUG_LEVEL>0:
                halt = ["CONTINUE","HALT"][program[i]==99]
                print(f"{elapsedTimeMs()} up to instruction {n} which produced OUTPUT: {outp} at which point the program would {halt}")
            return outp,i,program
        n+=1
        been[i]=been.get(i,0)+1
        if been[i] > 1:
            print(f"{elapsedTimeMs()} up to instruction {n} and at IP {i} which we have been at {been[i]} times!")
            if been[i] > 1000:
                raise Exception(f"PRobably an error: we have returned to IP {i} {been[i]} times")
    return None,i,program

def runWithInputs(program,inputs,ip=0):
    if DEBUG_LEVEL>0: print(f"running program{inputs}")
    res,i,program = runIntCode(program,inputs,ip)
    if DEBUG_LEVEL>0: print(f"\tresult={res}")
    return res,i,program

if DEBUG_LEVEL>1:
    print(program)


def calcOutputFeedback(inp, phases, amps, iteration):
    if DEBUG_LEVEL>0 or iteration%1000==0: print(f"feedback iteration {iteration} with phase order {phases}")
    outp=0
    for amp_index in range(5):
        amp = amps[amp_index]
        phase = phases[amp_index]
        inputs=[]
        if iteration==1:
            inputs.append(phase)
        inputs.append(inp)
        outp,i,program = runWithInputs(amp.program,inputs,amp.ip)
        if DEBUG_LEVEL>1: print(f"\t{inp} --> Amp {amp_id} ({phase}) --> {outp}")
        if outp == None:
            print(f"iteration {iteration} {inp} --> Amp {amp.id} ({phase}) --> {outp}")
            outp=inp
        inp = outp
        amp.program = program
        amp.ip = i
        amps[amp_index] = amp
    return outp,amps,iteration

def highestOutputFeedbackAmps(n_amps,base_phases):
    highest = 0
    order = None
    for phases in itertools.permutations(base_phases,5):
        amps = createAmps(n_amps)
        feedback = True
        outp = 0
        iteration = 0
        while feedback:
            outp,amps,iteration = calcOutputFeedback(outp, phases, amps, iteration+1)
            if amps[-1].program[amps[-1].ip] == 99:
                feedback=False
        if outp > highest:
            highest = outp
            order = phases
    print(f"highest output found WITH feedback was {highest} using the phase ordering {order}")

def calcOutput(inp,phases,feedback=0):
    if DEBUG_LEVEL>0: print(f"trying with phase order {phases}")
    if feedback>5: print(f"into feedback iteration {feedback}")
    outp=0
    for amp_id in range(5):
        phase = phases[amp_id]
        outp,i,program = runWithInputs(readFile(),[phase,inp])
        if DEBUG_LEVEL>0: print(f"\t{inp} --> Amp {amp_id} ({phase}) --> {outp}")
        inp = outp
    if feedback>0 and program[i] != 99:
        feedback+=1
        return calcOutput(outp,phases,feedback)
    return outp

def highestOutput(base_phases,feedback=0):
    highest = 0
    order = None
    for phases in itertools.permutations(base_phases,5):
        outp = calcOutput(0, list(phases), feedback)
        if outp > highest:
            highest = outp
            order = phases
    print(f"highest output found WITHOUT feedback was {highest} using the phase ordering {order}")

#highestOutput([0,1,2,3,4])
### NO ... going to have to create an amplifier class ...

@dataclass
class Amp:
    id: str
    program: list
    ip: int

def createAmps(qty):
    amps=[]
    ord_a = ord("A")
    for i in range(qty):
        program = readFile()
        amps.append(Amp(chr(ord_a+i), program, 0))
    print("Amps:",[amp.id for amp in amps])
    return amps

#highestOutputFeedbackAmps(5,[0,1,2,3,4])
highestOutputFeedbackAmps(5,[5,6,7,8,9])




