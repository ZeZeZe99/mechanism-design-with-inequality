"""
Linear Program to solve for optimal allocation rules
Setting: vm = 1 - vt, vs independent of vm, all uniform on (0,1), converted to discrete case
"""

import gurobipy as gp
from gurobipy import GRB
from prettytable import PrettyTable
import itertools

# parameters
LAMBDA = 10000000 # social value for revenue
q = 5 # ex ante constraint
n = 3 # number of types

l1 = []
l2 = []
l3 = []
vsList = []
vmList = []
vtList = []
for i in range(n):
    l1.append((i+1)/(n+1))
    l2.append((i+1)/(n+1))
    l3.append((n-i)/(n+1))

for i in itertools.product(l1,l2):
    vsList.append(i[0])
    vmList.append(i[1])
    # vtList.append(1-i[1])

for i in itertools.product(l1,l3):
    vtList.append(i[1])

try:
    m = gp.Model("SMT")
    m.Params.LogToConsole = 0
    m.Params.DualReductions = 0


    # variables
    x = m.addVars(n**2, vtype=GRB.CONTINUOUS, name="x", lb=0, ub=1)
    p = m.addVars(n**2, vtype=GRB.CONTINUOUS, name="p", lb=0)
    w = m.addVars(n**2, vtype=GRB.CONTINUOUS, name="w", lb=0)

    # objective
    m.setObjective(gp.quicksum((vsList[i]*x[i] - vmList[i]*p[i] - vtList[i]*w[i] + LAMBDA*p[i]) for i in range(n**2)),
                   GRB.MAXIMIZE)

    # constraints
    # IC
    m.addConstrs((vsList[i]*x[i] - vmList[i]*p[i] - vtList[i]*w[i] >=
                 vsList[i]*x[j] - vmList[i]*p[j] - vtList[i]*w[j]
                 for i in range(n**2) for j in range(n**2) if i != j), "IC")

    # IR
    m.addConstrs((vsList[i]*x[i] - vmList[i]*p[i] - vtList[i]*w[i] >= 0
                 for i in range(n**2)), "IR")

    # supply
    m.addConstr(gp.quicksum(x[i] for i in range(n**2)) <= q, "supply")

    # test constraints
    # m.addConstr((w[13] == 0), "test")
    # m.addConstr((p[6] <= 2), "test2")
    # m.addConstr(gp.quicksum(p[i] for i in range(n)) == 0, "no payment")
    # m.addConstr(gp.quicksum(w[i] for i in range(n)) == 0, "no wait time")
    # m.addConstr(gp.quicksum(p[i] for i in range(n)) >= 0.1, "has payment")
    # m.addConstr(gp.quicksum(w[i] for i in range(n)) >= 0.1, "has wait time")


    # optimize model
    m.optimize()

    m.display()

    if m.status == 5:
        print("unbounded")
        exit(1)
    elif m.status == 3:
        print("infeasible")
        exit(1)

    # solution
    solution = m.getVars()
    t = PrettyTable(["index", "vs", "vm", "vt", "x", "p", "w"])
    for i in range(n**2):
        t.add_row([i, vsList[i], vmList[i], vtList[i], solution[i].x, solution[n**2+i].x, solution[2*n**2+i].x])
    print(t)
    print('Obj: %g' % m.objVal)

except gp.GurobiError as e:
    print('Error code ' + e.errno + ': ' + e.message)

except AttributeError:
    print('Encountered an attribute error')