"""
Search for counterexamples based on solution pattern

Zejian Huang
"""
import gurobipy as gp
from prettytable import PrettyTable
from population import Population
from model import Model

# parameters

LAMBDA = 50000  # social value for revenue
n = 9  # number of types
q = 1  # ex ante constraint
v_precision = 4
num_loop = 100


"""
Functions checking counterexamples
"""
'''
Check whether x(vs/vm) is monotone non-decreasing
'''
def mono_s_over_m():
    for i in range(n):
        for j in range(n):
            if round(solution[i].x, 8) < round(solution[j].x, 8) and round(pop.smList[i], 8) > round(pop.smList[j], 8):
                print(i+1, solution[i].x, pop.smList[i])
                print(j+1, solution[j].x, pop.smList[j])
                return False
    return True


pop = Population(n)
count = 0
counter_ex = 0
while count <= num_loop:

    try:
        '''
        Generate population
        '''
        pop.clear_values()
        pop.draw_s_uniform(0, 1, 2)
        pop.dist_mt_uniform(0, 1)
        pop.calculate_ratio()
        pop.calculate_regularity_s()

        '''
        Build model
        '''
        m = Model(pop, q, LAMBDA).m

        # optimize model
        m.optimize()

        m.display()

        # handle unbounded or infeasible
        if m.status == 5:
            print("unbounded")
            continue
        elif m.status == 3:
            print("infeasible")
            m.computeIIS()
            continue

        # solution
        solution = m.getVars()

        # check counterexample conditions, print counterexample and stop
        if mono_s_over_m():
            count += 1
        else:
            counter_ex += 1
            t = PrettyTable(["index", "prob", "vs", "vm", "vt", "x", "p", "w", "vs/vm", "vs/vt", "vt/vm",
                             "vs_reg", "eta"])
            for i in range(n):
                x = round(solution[i].x, v_precision)
                p = round(solution[n + i].x, v_precision)
                w = round(solution[2 * n + i].x, v_precision)
                t.add_row([i + 1, round(pop.pdf[i], v_precision),
                           round(pop.vsList[i], v_precision),
                           round(pop.vmList[i], v_precision),
                           round(pop.vtList[i], v_precision),
                           x, p, w,
                           round(pop.smList[i], v_precision),
                           round(pop.stList[i], v_precision),
                           round(pop.tmList[i], v_precision),
                           round(pop.regularity[i], v_precision),
                           p - w])
            print(t)
            print('q: %.2f, Obj: %g' % (q, m.objVal))

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

    except gp.GurobiError as e:
        print('Error code ' + e.errno + ': ' + e.message)

    except AttributeError:
        print('Encountered an attribute error')

print(counter_ex)
