import gurobipy as gp
from gurobipy import GRB
from prettytable import PrettyTable

LAMBDA = .03
q = 1
n = 9
vsList = []
vmList = []
vtList = []
for i in range(n):
    vsList.append((i+1)/(n+1))
    vtList.append((i+1)/(n+1))
    vmList.append((n-i)/(n+1))

try:
    m = gp.Model("SMT")
    m.Params.LogToConsole = 0

    # variables
    x = m.addVars(n, vtype=GRB.CONTINUOUS, name="x", lb=0, ub=1)
    p = m.addVars(n, vtype=GRB.CONTINUOUS, name="p", lb=0)
    w = m.addVars(n, vtype=GRB.CONTINUOUS, name="w", lb=0)

    # objective
    m.setObjective(gp.quicksum((vsList[i]*x[i] - vmList[i]*p[i] - vtList[i]*w[i] + LAMBDA*p[i]) for i in range(n)),
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
    m.addConstr(gp.quicksum(x[i] for i in range(n)) <= q, "supply")

    # test constraints
    # m.addConstr((x[3] == .5), "test")
    # m.addConstr((p[3] == 1.5), "test2")

    # optimize model
    m.optimize()

    m.display()

    # solution
    solution = m.getVars()
    t = PrettyTable(["index", "vs", "vm", "vt", "x", "p", "w"])
    for i in range(n):
        t.add_row([i, vsList[i], vmList[i], vtList[i], solution[i].x, solution[n + i].x, solution[2 * n + i].x])
    print(t)

    print('Obj: %g' % m.objVal)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')
