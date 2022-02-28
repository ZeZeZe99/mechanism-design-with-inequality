"""
Linear Program to solve for optimal allocation rules
Setting: vm = 1 - vt, uniform on (0,1), vs = g(vm) for g increasing, converted to discrete case

Zejian Huang
"""

import gurobipy as gp
import math

from population import Population
from model import Model
from dual import Dual
from printer import print_solution, print_dual_solution, plot_values

# parameters
LAMBDA = 50000  # social value for revenue
n = 9  # number of types
q = 1  # ex ante constraint
v_precision = 4

try:
    '''
    Generate population
    '''
    pop = Population(n)

    '''vm'''
    pop.vmList = pop.value_uniform(1, 1)

    '''vs'''
    pop.vsList = pop.value_uniform(0, 1)
    # pop.vsList = pop.value_kumaraswamy(1.75, 10, 8, 5, 0.75)  # a, b, c, d, q
    # pop.vsList = pop.value_exponential(scale=1/1)  # scale = 1 / lambda
    # for i in range(pop.num_type):
    #     pop.vsList.append(math.log(pop.vmList[i]))

    '''vt'''
    # pop.vtList = pop.value_uniform(1, 0)
    for i in range(pop.num_type):
        pop.vtList.append(pop.vsList[i]**2)

    '''add perturbation to values'''
    # pop.perturbation(-1e-3, 1e-3, precision=v_precision, vs=True, vm=False, vt=False)
    # for i in range(0, 9):
    #     if i < 9:
    #         off = -1 * (i+1) ** 2 / 1000
    #     else:
    #         off = 0 * (i+1) ** 2 / 1000
    #     pop.vsList[i] += off
    # pop.vsList[7] = (pop.vsList[6]+pop.vsList[8])/2
    #     pop.vs_perturbation.append(off)

    '''pdf for each type'''
    # pop.type_uniform()
    pop.type_kumaraswamy(1.75, 10, 8, 5, 0.75)

    pop.calculate_ratio()
    pop.calculate_virtual_s()

    '''
    Draw value graphs
    '''
    # plot_values(pop, vs=True, vm=False, vt=False)

    '''
    Build model
    '''
    m = Model(pop, q, LAMBDA).m

    # write model to file
    m.write("lp/model.lp")

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
        m.write("lp/model.ilp")
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
    d.write("lp/dual.lp")
    d.optimize()
    # print_dual_solution(d, pop, q, v_precision)

except gp.GurobiError as e:
    print('GurobiError: ' + e.message)

except AttributeError:
    print('Encountered an attribute error')
