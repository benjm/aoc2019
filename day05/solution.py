import sys
import math
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
        print(f"\tOUTP: {param1}")
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
    return program,i

def runIntCode(program,inputs=[]):
    i = 0
    n = 0
    been={}
    while program[i] != 99:
        program,i = nextOp(program,i,inputs)
        n+=1
        been[i]=been.get(i,0)+1
        if been[i] > 1:
            print(f"{elapsedTimeMs()} up to instruction {n} and at IP {i} which we have been at {been[i]} times!")
            if been[i] > 1000:
                raise Exception(f"PRobably an error: we have returned to IP {i} {been[i]} times")
    return program[0]

def runWithInputs(program,inputs):
    print(f"running program{inputs}")
    res = runIntCode(program,inputs)
    print(f"\tresult={res}")

if DEBUG_LEVEL>1:
    print(program)
# runWithInputs(readFile(),[0])
# runWithInputs(readFile(),[1])
runWithInputs(readFile(),[5])
# runWithInputs(readFile(),[8])
# runWithInputs(readFile(),[10])
