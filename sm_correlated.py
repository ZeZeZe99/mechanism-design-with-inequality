"""
Linear Program to solve for optimal allocation rules
Setting: vm = 1 - vt, uniform on (0,1), vs = g(vm) for g increasing, converted to discrete case
"""

import gurobipy as gp
from gurobipy import GRB
from prettytable import PrettyTable
import random
from scipy.stats import beta

# parameters
v_precision = 4
LAMBDA = 50000  # social value for revenue
n = 3  # number of types
q = 1  # ex ante constraint

# distribution parameters
a = 8
b = 2

# vsList = [.2, .3, .375, .5, .625, .75, .875]
vsList = [.33, .5, .75]
vmList = []
vtList = []
pdf = []

"""
vs: generate random values and sort increasingly
"""
# for i in range(n):
#     vsList.append(random.random())
# vsList.sort()


"""
vm: uniform distribution
"""
for i in range(n):
    vmList.append((i+1)/(n+1))
    vtList.append((n-i)/(n+1))
    pdf.append(1/n)


"""
vm: beta distribution
"""

# for i in range(n):
#     vmList.append(beta.rvs(a, b))
# vmList.sort()
# for i in range(n):
#     vtList.append(1-vmList[i])

# pdf_sum = 0
# for i in range(n):
#     d = beta.pdf(vmList[i], a, b)
#     pdf.append(d)
#     pdf_sum += d
# for i in range(n):
#     pdf[i] = pdf[i] / pdf_sum


try:
    m = gp.Model("SMT")
    m.Params.LogToConsole = 0
    m.Params.DualReductions = 0

    # variables
    x = m.addVars(n, vtype=GRB.CONTINUOUS, name="x", lb=0, ub=1)
    p = m.addVars(n, vtype=GRB.CONTINUOUS, name="p", lb=0)
    w = m.addVars(n, vtype=GRB.CONTINUOUS, name="w", lb=0)

    # objective
    # m.setObjective(gp.quicksum((vsList[i]*x[i] - vmList[i]*p[i] - vtList[i]*w[i] + LAMBDA*p[i]) for i in range(n)),
    #                GRB.MAXIMIZE)
    m.setObjective(
        gp.quicksum((vsList[i] * x[i] - vmList[i] * p[i] - vtList[i] * w[i] + LAMBDA * p[i]) * pdf[i] for i in range(n)),
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
    # m.addConstr(gp.quicksum(x[i] for i in range(n))/n <= q, "supply")
    m.addConstr(gp.quicksum(x[i] * pdf[i] for i in range(n)) <= q, "supply")

    # test constraints
    # m.addConstr((x[2] <= .5), "test")
    # m.addConstr((w[1] == .0037), "test2")
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
    t = PrettyTable(["index", "prob", "vs", "vm", "vt", "x", "p", "w", "vs/vm", "vs/vt", "eta"])
    for i in range(n):
        x = round(solution[i].x, v_precision)
        p = round(solution[n + i].x, v_precision)
        w = round(solution[2 * n + i].x, v_precision)
        t.add_row([i+1, round(pdf[i], 4),
                   round(vsList[i], v_precision), round(vmList[i], v_precision), round(vtList[i], v_precision),
                   x, p, w,
                   round(vsList[i] / vmList[i], v_precision), round(vsList[i] / vtList[i], v_precision),
                   p-w])
    print(t)
    print('q: %.2f, Obj: %g' % (q, m.objVal))

    # find tight constraints
    slack = m.getAttr("slack")
    # print("Tight constraints: ", end="")
    # for i in range(len(slack)):
    #     if slack[i] == 0:
    #         print(i, end=" ")
    # print()

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
                #     print("u(%d,%d)>u(%d,%d)" % (i, i, i, j), end=" | ")
                index += 1
        print()

    print("IR constraints:")
    print("|", end=" ")
    for i in range(n):
        if slack[index] == 0:
            print("u(%d)=0" % (i+1), end=" | ")
        index += 1
    print()


except gp.GurobiError as e:
    print('Error code ' + e.errno + ': ' + e.message)

except AttributeError:
    print('Encountered an attribute error')
