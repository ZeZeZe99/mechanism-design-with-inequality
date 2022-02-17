from prettytable import PrettyTable
import matplotlib.pyplot as plt

"""
Print primal solution and constraints
:param myerson: indicate whether the problem is in Myerson's environment
"""
def print_solution(model, pop, q, precision, myerson=False):
    print('Primal: q: %.2f, Obj: %g' % (q, model.objVal))
    solution = model.getVars()
    n = pop.num_type

    # Columns
    if myerson:
        t = PrettyTable(["index", "prob", "vs", "x", "p", "vs_reg"])
    else:
        t = PrettyTable(["index", "prob", "vs", "vm", "vt", "x", "p", "w", "vs/vm", "vs/vt", "vt/vm",
                        "vs_reg", "eta"])

    # Solutions
    if myerson:
        for i in range(n):
            x = round(solution[i].x, precision)
            p = round(solution[n + i].x, precision)
            t.add_row([i + 1, round(pop.pdf[i], precision),
                       round(pop.vsList[i], precision),
                       x, p,
                       round(pop.regularity[i], precision)])
    else:
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

    # Constraints
    # Find tight constraints
    slack = model.getAttr("slack")
    index = 0
    header = ["constraint"]
    for i in range(n):
        header.append(str(i + 1))
    t2 = PrettyTable(header)
    for i in range(n):
        row = ["IC(" + str(i + 1) + ", c)"]
        for j in range(n):
            if i == j:
                row.append("****")
            elif slack[index] == 0:
                row.append("u({i},{i})=u({i},{j})".format(i=i + 1, j=len(row)))
                index += 1
            else:
                row.append("___>___")
                index += 1
        t2.add_row(row)
    row = ["IR"]
    for i in range(n):
        if slack[index] == 0:
            row.append("u({i})=0".format(i=i + 1))
            index += 1
        else:
            row.append("____>0")
            index += 1
    t2.add_row(row)
    print(t2)


"""
Print dual solution
:param myerson: indicate whether the problem is in Myerson's environment
"""
def print_dual_solution(model, pop, q, precision, myerson=False):
    print('Dual: q: %.2f, Obj: %g' % (q, model.objVal))
    n = pop.num_type

    # Solutions
    header = ["var"]
    for i in range(n):
        header.append(str(i + 1))
    t = PrettyTable(header)
    # print IC
    for i in range(n):
        row = ["IC(" + str(i + 1) + ", c)"]
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
    for i in range(n - 1):
        row.append("")
    t.add_row(row)
    print(t)

    # tight / slack constraints
    slack = model.getAttr("slack")
    header2 = ["constraint"]
    for i in range(n):
        header2.append(str(i + 1))
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
    if not myerson:
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


"""
Draw the line graphs for values
"""
def plot_values(pop, vs=True, vm=False, vt=False, augmentation=1):
    if vs:
        temp = []
        if len(pop.vs_perturbation) == 0:
            temp = pop.vsList
        else:
            for i in range(pop.num_type):
                temp.append(pop.vsList[i] + augmentation * pop.vs_perturbation[i])
        plt.plot(temp)
    if vm:
        temp = []
        if len(pop.vm_perturbation) == 0:
            temp = pop.vmList
        else:
            for i in range(pop.num_type):
                temp.append(pop.vmList[i] + augmentation * pop.vm_perturbation[i])
        plt.plot(temp)
    if vt:
        temp = []
        if len(pop.vt_perturbation) == 0:
            temp = pop.vtList
        else:
            for i in range(pop.num_type):
                temp.append(pop.vtList[i] + augmentation * pop.vt_perturbation[i])
        plt.plot(temp)
    plt.show()
