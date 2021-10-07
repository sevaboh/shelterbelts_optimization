#!/usr/bin/python
import math
from random import random
import all_fields
import all_shelterbelts

# NDVI(VTCI)
deps = [lambda x:math.log(x/0.194413)/1.46792,  # type 0 - irr/0 shelterbelts
        lambda x:math.log(x/0.18488)/1.549554,  # type 1 - irr/1 shelterbelts
        lambda x:math.log(x/0.181422)/1.578241,  # type 2 - irr/2 shelterbelts
        lambda x:math.log(x/0.182862)/1.56468,  # type 3 - irr/3 shelterbelts
        lambda x:math.log(x/0.182862)/1.56468,  # type 4 - irr/4 shelterbelts
        # type 5 - no irr/0 shelterbelts
        lambda x:math.log(x/0.166555)/1.405127,
        # type 6 - no irr/1 shelterbelts
        lambda x:math.log(x/0.1541059)/1.558659,
        lambda x:math.log(x/0.147)/1.636,  # type 7 - no irr/2 shelterbelts
        # type 8 - no irr/3 shelterbelts
        lambda x:math.log(x/0.134896)/1.748264,
        lambda x:math.log(x/0.134896)/1.748264]  # type 9 - no irr/4 shelterbelts
# shifted NDWI (sector mask) - now random
deps2= []
for i in range(256):
    deps2.append(random())
# weights for NDVI/NDWI
weights=[0.55,0.45]

# fields-shelterbelts graph
fields = all_fields.gen_fields() # (area(m^2),avg vtci,irrigation,id in shp,[shelterbelts ids],[sector masks])
shelterbelts = all_shelterbelts.gen_shelterbelts() # ([field1s ids],length(m),present, id in shp of present or potential places)
first0=0
for i in range(len(shelterbelts)):
    if shelterbelts[i][2]==0:
        first0=i
        break

def fitness_function(state):
    global shelterbelts, fields,first0
    f = 0.0
    # loop fields/ calc sector mask
    for i in range(len(fields)):
        cl=0
        for b in range(len(fields[i][4])):
            present=0
            if shelterbelts[fields[i][4][b]][2]:
                present = 1
            else:
                if state[fields[i][4][b]-first0]:
                    present = 1
            if present:
                cl = cl | fields[i][5][b]
        n1=0
        for b in range(8):
              if cl & (1<<b):
                   n1=n1+1
        n_belts=int(n1/2)
        if n1>=8:
            n_belts=4
        # f+= w0*area * ndvi for avg vtci and calculated number of shelterbelts
        # assume that irrigated state doesn't change and avg vtci is typical for the field
        try:
            if deps[(1-fields[i][2])*5+n_belts](fields[i][1])>0:
                f = f+weights[0]*fields[i][0]*deps[(1-fields[i][2])*5+n_belts](fields[i][1])
            # f+= w1*area * ndwi for sector mask
            f = f+weights[1]*fields[i][0]*deps2[cl]
        except:
            pass
    return f

# simple genetic algorithm
max_new_shelterbelts_length = 900*1000
pop_size = 50
state_size = 0
population = []
f_values=[]

max_steps = 10000
min_diff = 1.0

worst = 1e100
worst_id = -1
best = 0
best_id = -1
do_greedy = 1
print_state=0

# calc state size - number of non-present shelterbelts
for b in shelterbelts:
    if b[2] == 0:
        state_size = state_size+1
print("state size - "+str(state_size))

# length of new shelterbelts
def length(state):
    global shelterbelts,first0
    l=0
    for i in range(len(state)):
        if state[i]:
            l=l+shelterbelts[first0+i][1]
    return l
# number of new shleterbelts
def number(state):
    global shelterbelts,first0
    l=0
    for i in range(len(state)):
        if state[i]:
            l=l+1
    return l

def crossover(state1, state2):
    ret = []
    for i in range(len(state1)):
        r = random()
        if r > 0.5:
            ret.append(state2[i])
        else:
            ret.append(state1[i])
    return ret

# generate new state, replace in population if new state is better than the worst state
def new_state():
    global population, pop_size, worst, best, state_size, worst_id, best_id
    global shelterbelts, fields,first0
    # add random state if population has less than pop_size members
    if len(population) != pop_size:
        st = []
        for i in range(state_size):
            st.append(0)
        l=0
        while l<max_new_shelterbelts_length:
            r = int(random()*state_size)
            if st[r]==0:
                st[r]=1
                l=l+shelterbelts[first0+r][1]
        population.append(st)
        # recalc worst/best
        f = fitness_function(st)
        f_values.append(f)
        if f < worst:
            worst = f
            worst_id = len(population)-1
        if f > best:
            best = f
            best_id = len(population)-1
    else:  # mix two random states with crossover operation
        while True:
            r1 = int(random()*len(population))
            while True:
                r2 = int(random()*len(population))
                if r1 != r2:
                    break
            st = crossover(population[r1], population[r2])
            if length(st) < max_new_shelterbelts_length:
                f = fitness_function(st)
                if f > worst:
                    population.pop(worst_id)
                    f_values.pop(worst_id)
                    population.append(st)
                    f_values.append(f)
                    # recalc worst/best
                    worst = 1e100
                    worst_id = -1
                    best = 0
                    best_id = -1
                    for i in range(len(population)):
                        f = f_values[i]
                        if f < worst:
                            worst = f
                            worst_id = i
                        if f > best:
                            best = f
                            best_id = i
                break

st = []
for i in range(state_size):
    st.append(0)
f0 = fitness_function(st)
print("fitness function for 0 state - "+str(f0))
# main GA loop
i = 0
while True:
    new_state()
    i = i+1
    if i > max_steps:
        break
    if len(population) == pop_size:
        if abs(best-worst) < min_diff:
            break
    print(str(i)+"("+str(abs(best-worst))+")"+" worst "+str(worst)+"("+str(worst_id) + ") best "+str(best)+"("+str(best_id)+") improvment by "+str(int(100*(best-f0)/f0))+"% number "+str(number(population[best_id])))
if print_state:
    for i in range(state_size):
        print(str(i)+" "+str(population[best_id][i]))
print("total new shelterbelts length "+str(length(population[best_id]))+" number "+str(number(population[best_id])))
# greedy search
if do_greedy and state_size < 31:
    best = 0
    best_st = []
    n_vars = int(math.pow(2, state_size))
    for i in range(n_vars):
        st = []
        for j in range(state_size):
            st.append((i & (1 << j)) >> j)
        if length(st) < max_new_shelterbelts_length:
            f = fitness_function(st)
            if f > best:
                best = f
                best_st = st
    print("greedy best "+str(best))
    for i in range(state_size):
        print(str(i)+" "+str(best_st[i]))
    print("improvement by "+str(int(100*(best-f0)/f0))+"%")
    print("total new shelterbelts length - "+str(length(best_st)))
