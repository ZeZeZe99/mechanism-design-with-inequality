"""
Search for counterexamples based on solution pattern

Zejian Huang
"""
import gurobipy as gp
from population import Population
from model import Model
from dual import Dual
from printer import print_solution, print_dual_solution

# parameters

LAMBDA = 50000  # social value for revenue
n = 9  # number of types
q = 1  # ex ante constraint
v_precision = 4
num_loop = 10000

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

'''
Check whether the dual variable IC[a,b] is 0
'''
def dual_zero_IC(a, b):
    name = "ic[" + str(a-1) + "," + str(b-1) + "]"
    if d.getVarByName(name).x == 0:
        return True
    else:
        return False

pop = Population(n)
count = 0
counter_ex = 0
while count <= num_loop:

    try:
        '''
        Generate population
        '''
        pop.clear_values()
        pop.vsList = pop.value_uniform(1, 5)
        pop.vmList = pop.value_uniform(2, 3)
        pop.vtList = pop.value_uniform(4, 2)
        pop.perturbation(-1e-3, 1e-3, precision=v_precision)
        pop.type_uniform()
        pop.calculate_ratio()
        pop.calculate_virtual_s()

        '''
        Build model
        '''
        m = Model(pop, q, LAMBDA).m
        d = Dual(pop, q, LAMBDA).m

        # optimize model
        m.optimize()
        d.optimize()

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
        # if not mono_s_over_m() and pop.mono_regularity_s():
        # if not mono_s_over_m():
        if not dual_zero_IC(1, 4) or not dual_zero_IC(2, 5):
            counter_ex += 1
            print_solution(m, pop, q, v_precision)
            print_dual_solution(d, pop, q, v_precision)
            exit(1)

    except gp.GurobiError as e:
        print('Error code ' + e.errno + ': ' + e.message)

    except AttributeError:
        print('Encountered an attribute error')

print(counter_ex)
