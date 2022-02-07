"""
Linear Program to solve for optimal allocation rules
Setting: vm = 1 - vt, uniform on (0,1), vs = g(vm) for g increasing, converted to discrete case

Zejian Huang
"""

import gurobipy as gp
from prettytable import PrettyTable
from population import Population
from model import Model
from dual import Dual

# parameters
LAMBDA = 50000  # social value for revenue
n = 9   # number of types
q = 1  # ex ante constraint
v_precision = 4

try:
    '''
    Generate population
    '''
    pop = Population(n)
    # pop.vsList = [0.2, 0.4, 0.6, 0.8]
    # pop.dist_s_uniform(3, 6)
    pop.draw_s_uniform(0, 1, 2)

    pop.dist_mt_uniform(0, 1)
    pop.calculate_ratio()
    pop.calculate_regularity_s()

    '''
    Build model
    '''
    m = Model(pop, q, LAMBDA).m

    # extra testing constraints
    # m.addConstr(gp.quicksum(p[i] for i in range(n)) == 0, "no payment")
    # m.addConstr(gp.quicksum(w[i] for i in range(n)) == 0, "no wait time")

    # write model to file
    m.write("model.lp")

    '''
    Solve LP
    '''
    # optimize model
    m.optimize()
    # m.display()

    # handle unbounded and infeasible problems
    if m.status == 5:
        print("unbounded primal")
        exit(1)
    elif m.status == 3:
        print("infeasible primal")
        m.computeIIS()
        m.write("model.ilp")
        exit(1)


    '''
    Print result
    '''
    # solution
    solution = m.getVars()
    t = PrettyTable(["index", "prob", "vs", "vm", "vt", "x", "p", "w", "vs/vm", "vs/vt", "vt/vm", "vs_reg", "eta"])
    for i in range(n):
        x = round(solution[i].x, v_precision)
        p = round(solution[n + i].x, v_precision)
        w = round(solution[2 * n + i].x, v_precision)
        t.add_row([i+1, round(pop.pdf[i], v_precision),
                   round(pop.vsList[i], v_precision),
                   round(pop.vmList[i], v_precision),
                   round(pop.vtList[i], v_precision),
                   x, p, w,
                   round(pop.smList[i], v_precision),
                   round(pop.stList[i], v_precision),
                   round(pop.tmList[i], v_precision),
                   round(pop.regularity[i], v_precision),
                   p-w])
    print(t)
    print('q: %.2f, Obj: %g' % (q, m.objVal))
    # exit(1)

    # constraints
    # find tight constraints
    slack = m.getAttr("slack")
    print("IC constraints:")
    index = 0
    for i in range(n):
        print("|", end=" ")
        for j in range(n):
            if i != j:
                s = slack[index]
                if s == 0:
                    print("u(%d,%d)=u(%d,%d)" % (i+1, i+1, i+1, j+1), end=" | ")
                else:
                    print("_____________", end=" | ")
                index += 1
        print()
    print("IR constraints:")
    print("|", end=" ")
    for i in range(n):
        if slack[index] == 0:
            print("u(%d)=0" % (i+1), end=" | ")
        index += 1
    print()

    """
    Dual model
    """
    d = Dual(pop, q, LAMBDA).m
    d.write("dual.lp")
    d.optimize()
    print(d.objVal)



except gp.GurobiError as e:
    print('GurobiError: ' + e.message)

except AttributeError:
    print('Encountered an attribute error')
