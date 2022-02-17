"""
Linear Program to solve for optimal allocation rules
Setting: vm = 1 - vt, uniform on (0,1), vs = g(vm) for g increasing, converted to discrete case

Zejian Huang
"""

import gurobipy as gp


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
    # vs
    pop.vsList = pop.dist_uniform(3, 4)
    # pop.vsList = pop.dist_exponential(0, 1, scale=1/1)  # scale = 1 / lambda
    # pop.vsList = pop.dist_geometric(0, 1, 0.5)
    # pop.vsList = [.14, .19, .51, .59, .61, .69, .7, .75, .78]

    # vm
    pop.vmList = pop.dist_uniform(0, 1)

    # vt
    pop.vtList = pop.dist_uniform(1, 0)
    # for i in range(pop.num_type):
    #     pop.vtList.append(2 - pop.vmList[i])

    # add perturbation to values
    # pop.perturbation(-1e-3, 1e-3, precision=v_precision, vs=True, vm=False, vt=False)
    for i in range(0, 9):
        pop.vsList[i] += - 1 * i ** 2 / 1000
        pop.vs_perturbation.append(-1 * i ** 2 / 1000)

    # pdf for each type
    pop.pdf_uniform()
    # pop.pdf_geometric(.5)

    pop.calculate_ratio()
    pop.calculate_regularity_s()

    '''
    Draw value graphs
    '''
    plot_values(pop, vs=True, vm=False, vt=False, augmentation=1)

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
    print("Dual obj: %g" % d.objVal)
    print_dual_solution(d, pop, q, v_precision)

except gp.GurobiError as e:
    print('GurobiError: ' + e.message)

except AttributeError:
    print('Encountered an attribute error')
