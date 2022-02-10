"""
Linear Program to solve for optimal allocation rules in the Myerson setting
Setting: single parameter environment, people have different vs

Zejian Huang
"""

import gurobipy as gp
from population import Population
from myerson import Myerson
from printer import myerson_solution, myerson_dual_solution

# parameters
n = 2   # number of types
q = 1  # ex ante constraint
v_precision = 4

try:
    '''
    Generate population
    '''
    pop = Population(n)
    # pop.vsList = [.09, .33, .46, .56, .61, .65, .7, .73, .78]
    pop.dist_s_uniform(0, 1)
    # pop.draw_s_uniform(0, 1, 2)
    pop.pdf_uniform()

    pop.calculate_regularity_s()

    '''
    Build LP model (primal and dual)
    '''
    model = Myerson(pop, q, rev_max=True)
    primal = model.primal
    dual = model.dual

    # write model to file
    primal.write("lp/myerson_primal.lp")
    dual.write("lp/myerson_dual.lp")

    '''
    Solve primal LP
    '''
    # optimize model
    primal.optimize()

    # handle unbounded and infeasible problems
    if primal.status == 5:
        print("unbounded primal")
        exit(1)
    elif primal.status == 3:
        print("infeasible primal")
        primal.computeIIS()
        primal.write("lp/model.ilp")
        exit(1)

    '''
    Print result
    '''
    # solution
    myerson_solution(primal, pop, q, v_precision)

    """
    Solve dual LP
    """
    # optimize model
    dual.optimize()

    # handle unbounded and infeasible problems
    if dual.status == 5:
        print("unbounded dual")
        exit(1)
    elif dual.status == 3:
        print("infeasible dual")
        dual.computeIIS()
        dual.write("lp/dual.ilp")
        exit(1)

    '''
    Print result
    '''
    # solution
    myerson_dual_solution(dual, pop, q, v_precision)

except gp.GurobiError as e:
    print('GurobiError: ' + e.message)

except AttributeError:
    print('Encountered an attribute error')
