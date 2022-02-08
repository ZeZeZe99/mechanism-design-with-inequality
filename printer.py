from prettytable import PrettyTable

"""
Print solution and constraints
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
