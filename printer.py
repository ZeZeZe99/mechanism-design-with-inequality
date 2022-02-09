from prettytable import PrettyTable

"""
Print primal solution and constraints
"""
def print_solution(model, pop, q, precision):
    solution = model.getVars()
    n = pop.num_type
    t = PrettyTable(["index", "prob", "vs", "vm", "vt", "x", "p", "w", "vs/vm", "vs/vt", "vt/vm",
                     "vs_reg", "eta"])
    for i in range(n):
        x = round(solution[i].x, precision)
        p = round(solution[n + i].x, precision)
        w = round(solution[2 * n + i].x, precision)
        t.add_row([i + 1, round(pop.pdf[i], precision),
                   round(pop.vsList[i], precision),
                   round(pop.vmList[i], precision),
                   round(pop.vtList[i], precision),
                   x, p, w,
                   round(pop.smList[i], precision),
                   round(pop.stList[i], precision),
                   round(pop.tmList[i], precision),
                   round(pop.regularity[i], precision),
                   p - w])
    print(t)
    print('q: %.2f, Obj: %g' % (q, model.objVal))

    # constraints
    # find tight constraints
    slack = model.getAttr("slack")
    print("IC constraints:")
    index = 0
    for i in range(n):
        print("|", end=" ")
        for j in range(n):
            if i != j:
                s = slack[index]
                if s == 0:
                    print("u(%d,%d)=u(%d,%d)" % (i + 1, i + 1, i + 1, j + 1), end=" | ")
                else:
                    print("_____________", end=" | ")
                index += 1
        print()
    print("IR constraints:")
    print("|", end=" ")
    for i in range(n):
        if slack[index] == 0:
            print("u(%d)=0" % (i + 1), end=" | ")
        index += 1
    print()


"""
Print dual solution
"""
def print_dual_solution(model, pop, q, precision):
    n = pop.num_type

    # solutions
    header = ["var"]
    for i in range(n):
        header.append(str(i+1))
    t = PrettyTable(header)
    # print IC
    for i in range(n):
        row = ["IC(" + str(i+1) + ", c)"]
        for j in range(n):
            if i == j:
                row.append("")
            else:
                name = "ic[" + str(i) + "," + str(j) + "]"
                row.append(round(model.getVarByName(name).x, precision))
        t.add_row(row)
    # print IR
    row = ["IR"]
    for i in range(n):
        row.append(round(model.getVarByName("ir[" + str(i) + "]").x, precision))
    t.add_row(row)
    # print bound
    row = ["Bound"]
    for i in range(n):
        row.append(round(model.getVarByName("bound[" + str(i) + "]").x, precision))
    t.add_row(row)
    # print supply
    row = ["Supply", round(model.getVarByName("supply").x, precision)]
    for i in range(n-1):
        row.append("")
    t.add_row(row)
    print(t)

    # tight / slack constraints
    slack = model.getAttr("slack")
    header2 = ["constraint"]
    for i in range(n):
        header2.append(str(i+1))
    t2 = PrettyTable(header2)
    index = 0
    # x
    row = ["x"]
    for i in range(n):
        if slack[index] == 0:
            row.append("tight")
            index += 1
        else:
            row.append("_____")
            index += 1
    t2.add_row(row)
    # p
    row = ["p"]
    for i in range(n):
        if slack[index] == 0:
            row.append("tight")
            index += 1
        else:
            row.append("_____")
            index += 1
    t2.add_row(row)
    # w
    row = ["w"]
    for i in range(n):
        if slack[index] == 0:
            row.append("tight")
            index += 1
        else:
            row.append("_____")
            index += 1
    t2.add_row(row)
    print(t2)
