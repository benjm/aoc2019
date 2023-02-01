import sys
import math
from dataclasses import dataclass
from datetime import datetime

datetime_start = datetime.now()

def elapsedTimeMs(since=datetime_start):
    return datetime.now()-since

def processLines(lines):
    recipes = {}
    for line in lines:
        inputs, result = line.split(" => ")
        qty_m, typ_m = result.split()
        ingredients = {}
        for ingredient in inputs.split(", "):
            qty_i, typ_i = ingredient.split()
            ingredients[typ_i] = int(qty_i)
        recipe = Recipe(typ_m, int(qty_m), ingredients)
        recipes[typ_m] = recipe
    return recipes

def readFile(filename = sys.argv[1]):
    filename = sys.argv[1]
    lines = []
    with open(filename) as f:
        lines = f.read().splitlines()
    return processLines(lines)

FUEL="FUEL"
ORE="ORE"
@dataclass
class Recipe:
    typ: str
    qty: int
    ingredients: dict

print(elapsedTimeMs(),"starting part1")
recipes = readFile()

def howMuchOre(recipes):
    need = {}
    storage = {}
    for typ in recipes:
        storage[typ]=0
        need[typ]=0
    need[FUEL]=1
    ore=0
    fuel=0
    while sum(need.values()) > 0:
        new_need={}
        for typ in need:
            qty=need[typ]
            #print("breaking down",typ,qty)
            if qty>0:
                if qty<=storage[typ]:
                    storage[typ]-=qty
                    #print("\tgot it from storage, which now holds",storage[typ])
                else:
                    qty-=storage[typ]
                    recipe=recipes[typ]
                    n = math.ceil(qty/recipe.qty)
                    #print(f"{tabs}emptied any storage and need to produce {n} sets of recipe {recipe}")
                    for typ_r in recipe.ingredients:
                        qty_r = recipe.ingredients[typ_r]
                        #print(f"{tabs}\twill require {qty_r} of {typ_r}")
                        if typ_r == ORE:
                            ore+=qty_r*n
                        else:
                            new_need[typ_r]=new_need.get(typ_r,0) + n*qty_r
                    storage[typ] = n*recipe.qty - qty
        need = new_need
        fuel+=recipes[FUEL].qty
    return ore, fuel, storage

oreRequired,fuelProduced,storage = howMuchOre(recipes)
print(f"{elapsedTimeMs()} To make {fuelProduced} FUEL (the minimum for one run) requires {oreRequired} ORE and produces a total of {sum(storage.values())} leftover things in storage")

DEBUG_LEVEL = 0
def makeStuff(recipes, storage, typ, qty,depth=1):
    tabs = ".\t"*depth
    if typ == ORE:
        print(f"{tabs}down to ORE. {qty} needed and {storage[ORE]} in store")
        if storage[ORE] < qty:
            return 0, storage
        storage[ORE]-=qty
        return qty, storage
    made = 0
    recipe = recipes[typ]
    n_runs = math.ceil(qty / recipe.qty)
    if DEBUG_LEVEL>1: print(f"{tabs}will need to run {typ} recipe {n_runs} times to make at least {qty} {typ}")
    for sub_typ in recipe.ingredients:
        sub_qty = recipe.ingredients[sub_typ] * n_runs
        if storage[sub_typ]>=sub_qty:
            storage[sub_typ]-=sub_qty
            if DEBUG_LEVEL>0: print(f"{tabs}got {sub_qty} {sub_typ} from storage ({storage[sub_typ]} left)")
        else:
            sub_qty-=storage[sub_typ]
            sub_made, storage = makeStuff(recipes, storage, sub_typ, sub_qty, depth+1)
            if DEBUG_LEVEL>0: print(f"{tabs}made {sub_made} {sub_typ} using storage items")
            if sub_made<sub_qty:
                if DEBUG_LEVEL>1: print(f"{tabs}only have {sub_made} {sub_typ} and cannot satisfy {sub_qty} need")
                return made, storage
            storage[sub_typ] = sub_made - sub_qty
    made = recipe.qty * n_runs
    if DEBUG_LEVEL>1: print(f"{tabs}made {made} {typ}")
    return made, storage

def shapeify(storage):
    ",".join(typ for typ in sorted(storage))

def howMuchFuel(recipes, storage, ore_req_one_batch):
    fuel_prod_one_batch = recipes[FUEL].qty
    fuel = 0
    for typ in recipes:
        storage[typ]=storage.get(typ, 0)
    delta = 1
    n=0
    storageShape=set()
    storageShape.add(shapeify(storage))
    batch_size = storage[ORE] // ore_req_one_batch
    while delta > 0:
        if delta==batch_size==1:
            pass
        else:
            batch_size = round(0.5*storage[ORE])*fuel_prod_one_batch // ore_req_one_batch
        delta, storage = makeStuff(recipes,storage,FUEL,batch_size)
        fuel+=delta
        if delta == 0 and batch_size > 1:
            delta=batch_size=1
        # logging...
        n+=1
        if n%10000==0:
            print(f"up to iteration {n} with {sum(storage.values())} things left in storage and a batch_size of {batch_size}")
        if DEBUG_LEVEL>0: print(f"made another {delta} FUEL from storage for a total of {fuel} so far and {sum(storage.values())} things left in storage")
    return fuel, storage

ore_qty = 1000000000000

fuel, new_storage = howMuchFuel(recipes, {ORE:ore_qty}, oreRequired)
print(f"{elapsedTimeMs()} From a trillion ORE we can make {fuel} with {sum(new_storage.values())} things in storage")
print("STORAGE:")
for typ in new_storage:
    print(f"\t{typ}:\t{new_storage[typ]}")

exit()

prod_runs = ore_qty // oreRequired
print(f"could do {prod_runs} total not caring about leftovers")
prod_runs = round(0.8 * prod_runs)
print(f"will assume {prod_runs} total done so there's ORE left for other things")
fuelProduced*=prod_runs
ore_left = ore_qty - (prod_runs * oreRequired)
new_storage={}
for stuff in storage:
    new_storage[stuff] = storage[stuff] * prod_runs
new_storage[ORE] = ore_left
print("STORAGE:")
for typ in new_storage:
    print(f"\t{typ}:\t{new_storage[typ]}")
print(f"{elapsedTimeMs()} From a trillion ORE we can do {prod_runs} production runs to make {fuelProduced} and have {sum(new_storage.values())} things in storage to make more...")
fuel, new_storage = howMuchFuel(recipes, new_storage)
print(f"{elapsedTimeMs()} From a trillion ORE we can initially make {fuelProduced} and then from all the leftovers we can make {fuel} for a total of {fuelProduced + fuel}, leaving {sum(new_storage.values())} things in storage")

# for 13312 example the answer should be 82892753 but only getting 225360577