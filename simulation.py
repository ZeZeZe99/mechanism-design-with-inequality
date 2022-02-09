"""
Linear Program to solve for optimal allocation rules
Setting: vm = 1 - vt, uniform on (0,1), vs = g(vm) for g increasing, converted to discrete case

Zejian Huang
"""

import gurobipy as gp
from population import Population
from model import Model
from dual import Dual
from printer import print_solution, print_dual_solution

# parameters
LAMBDA = 50000  # social value for revenue
n = 4   # number of types
q = 1  # ex ante constraint
v_precision = 4

try:
    '''
    Generate population
    '''
    pop = Population(n)
    # pop.vsList = [.09, .33, .46, .56, .61, .65, .7, .73, .78]
    pop.dist_s_uniform(.1, .6)
    # pop.draw_s_uniform(0, 1, 2)

    pop.dist_mt_uniform(0, 1)
    pop.calculate_ratio()
    pop.calculate_regularity_s()

    '''
    Build model
    '''
    m = Model(pop, q, LAMBDA).m



    # write model to file
    m.write("model.lp")

    '''
    Solve LP
    '''
    # optimize model
    m.optimize()
    # m.display()

    # handle unbounded and infeasible problems
    if m.status == 5:
        print("unbounded primal")
        exit(1)
    elif m.status == 3:
        print("infeasible primal")
        m.computeIIS()
        m.write("model.ilp")
        exit(1)

    '''
    Print result
    '''
    # solution
    print_solution(m, pop, q, v_precision)

    """
    Dual model
    """
    d = Dual(pop, q, LAMBDA).m
    d.write("dual.lp")
    d.optimize()
    print()
    print("Dual obj: %g" % d.objVal)
    print_dual_solution(d, pop, q, v_precision)



except gp.GurobiError as e:
    print('GurobiError: ' + e.message)

except AttributeError:
    print('Encountered an attribute error')
