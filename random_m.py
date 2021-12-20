"""
Linear Program to solve for optimal allocation rules
Setting: vm = 1 - vt, vs = g(vm) for g increasing, randomly distributed with density 1/n, converted to discrete case
"""

import gurobipy as gp
from gurobipy import GRB
from prettytable import PrettyTable
import random
from scipy.stats import beta

# parameters
v_precision = 1
LAMBDA = .5  # social value for revenue
n = 4  # number of types
q = 1/n  # ex ante constraint


vsList = []
vmList = []
vtList = []

# vs: generate random values and sort increasingly
for i in range(n):
    vsList.append(round(random.random(), v_precision))
    vmList.append(round(random.random(), v_precision))
vsList.sort()
vmList.sort()
for i in range(n):
    vtList.append(1-vmList[i])




try:
    m = gp.Model("SMT")
    m.Params.LogToConsole = 0
    m.Params.DualReductions = 0

    # variables
    x = m.addVars(n, vtype=GRB.CONTINUOUS, name="x", lb=0, ub=1)
    p = m.addVars(n, vtype=GRB.CONTINUOUS, name="p", lb=0)
    w = m.addVars(n, vtype=GRB.CONTINUOUS, name="w", lb=0)

    # objective
    m.setObjective(gp.quicksum((vsList[i]*x[i] - vmList[i]*p[i] - vtList[i]*w[i] + LAMBDA*p[i])/n for i in range(n)),
                   GRB.MAXIMIZE)


    # constraints
    # IC
    m.addConstrs((vsList[i]*x[i] - vmList[i]*p[i] - vtList[i]*w[i] >=
                 vsList[i]*x[j] - vmList[i]*p[j] - vtList[i]*w[j]
                 for i in range(n) for j in range(n) if i != j), "IC")
    # IR
    m.addConstrs((vsList[i]*x[i] - vmList[i]*p[i] - vtList[i]*w[i] >= 0
                 for i in range(n)), "IR")
    # supply
    m.addConstr(gp.quicksum(x[i] / n for i in range(n)) <= q, "supply")

    # test constraints
    # m.addConstr((x[3] == 1), "test")
    # m.addConstr((p[3] == .1), "test2")
    # m.addConstr(gp.quicksum(p[i] for i in range(n)) == 0, "no payment")
    # m.addConstr(gp.quicksum(w[i] for i in range(n)) == 0, "no wait time")
    # m.addConstr(gp.quicksum(w[i] for i in range(n)) >= 0.1, "has wait time")

    # optimize model
    m.optimize()

    m.display()

    if m.status == 5:
        print("unbounded")
        exit(1)
    elif m.status == 3:
        print("infeasible")
        m.computeIIS()
        m.write("model.ilp")
        exit(1)

    # solution
    solution = m.getVars()
    t = PrettyTable(["index", "vs", "vm", "vt", "x", "p", "w", "eta", "vs/vm", "vs/vt", "lambda-vm"])
    for i in range(n):
        x = round(solution[i].x, 5)
        p = round(solution[n + i].x, 5)
        w = round(solution[2 * n + i].x, 5)
        t.add_row([i, vsList[i], vmList[i], round(vtList[i], v_precision),
                   x, p, w, p-w,
                   round(vsList[i] / vmList[i], 2), round(vsList[i] / vtList[i], 2), round(LAMBDA - vmList[i], 2)])
    print(t)
    print('Obj: %g' % m.objVal)

    # find tight constraints
    slack = m.getAttr("slack")
    print("Tight constraints: ", end="")
    for i in range(len(slack)):
        if slack[i] == 0:
            print(i, end=" ")


except gp.GurobiError as e:
    print('Error code ' + e.errno + ': ' + e.message)

except AttributeError:
    print('Encountered an attribute error')
