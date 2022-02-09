"""
Search for counterexamples based on solution pattern

Zejian Huang
"""
import gurobipy as gp
from population import Population
from model import Model
from printer import print_solution

# parameters

LAMBDA = 50000  # social value for revenue
n = 4  # number of types
q = 1  # ex ante constraint
v_precision = 4
num_loop = 100000

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
                # print(i + 1, solution[i].x, pop.smList[i])
                # print(j + 1, solution[j].x, pop.smList[j])
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
        count += 1
        if count % 1000 == 0:
            print(count)
        if not mono_s_over_m() and pop.mono_regularity_s():
        # if not mono_s_over_m():
            counter_ex += 1
            print_solution(m, pop, q, v_precision)

    except gp.GurobiError as e:
        print('Error code ' + e.errno + ': ' + e.message)

    except AttributeError:
        print('Encountered an attribute error')

print(counter_ex)
