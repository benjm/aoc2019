import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    return [int(c) for c in lines[0]]

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

@dataclass
class Layer:
    id: int
    height: int
    width: int
    pixels: list

def extractLayers(filename,height,width):
    raw = readFile(filename)
    layers = []
    layer_size = height * width
    n_layers = math.ceil(len(raw) / layer_size)
    for i in range(n_layers):
        raw_index = i * layer_size
        pixels = raw[raw_index:raw_index+layer_size]
        layer = Layer(i,height,width,pixels)
        layers.append(layer)
    return layers

testImageLayers = extractLayers("test",2,3)
# for layer in testImageLayers:
#     print("Layer",layer.id)
#     for y in range(layer.height):
#         print(layer.pixels[y*layer.width:(y+1)*layer.width])
def checksum(layers):
    layer_id = None
    leastZeros = math.inf
    checksum = 0
    for layer in layers:
        num_zeros = sum(1 for p in layer.pixels if p==0)
        if num_zeros < leastZeros:
            leastZeros = num_zeros
            layer_id = layer.id
            num_ones = sum(1 for p in layer.pixels if p==1)
            num_twos = sum(1 for p in layer.pixels if p==2)
            checksum = num_ones * num_twos
    print(f"least zeros: {leastZeros} in layer {layer_id} which has a checksum of {checksum}")

print("TEST:")
checksum(testImageLayers)

imageLayers = extractLayers("input",6,25)
print("INPUT:")
checksum(imageLayers)

def mergeDown(layers):
    pixels = None
    height = None
    width = None
    combined_id = -1
    for layer in layers:
        if not pixels:
            pixels = layer.pixels.copy()
            height = layer.height
            width = layer.width
        else:
            for i in range(len(pixels)):
                if pixels[i] == 2:
                    pixels[i] = layer.pixels[i]
    return Layer(combined_id, height, width, pixels)


finalLayer = mergeDown(imageLayers)
for y in range(finalLayer.height):
    row_data = finalLayer.pixels[y*finalLayer.width:(y+1)*finalLayer.width]
    print(" ".join([".","#"][p==1]for p in row_data))