"""
Module for building linear programming model

Zejian Huang
"""

import gurobipy as gp
from gurobipy import GRB


class Model:
    m = None

    """
    Initialize the LP model
    :param pop: a population instance
    :param q: ex ante constraint
    :param LAMBDA: social value for revenue
    """
    def __init__(self, pop, q, LAMBDA):

        self.m = gp.Model("SMT")
        self.m.Params.LogToConsole = 0
        self.m.Params.DualReductions = 0

        # variables
        x = self.m.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="x", lb=0, ub=1)
        p = self.m.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="p", lb=0)
        w = self.m.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="w", lb=0)

        # objective
        self.m.setObjective(
            gp.quicksum(
                (pop.vsList[i] * x[i] - pop.vmList[i] * p[i] - pop.vtList[i] * w[i] + LAMBDA * p[i]) * pop.pdf[i]
                for i in range(pop.num_type)),
            GRB.MAXIMIZE)

        # constraints
        # incentive compatibility
        self.m.addConstrs((pop.vsList[i] * x[i] - pop.vmList[i] * p[i] - pop.vtList[i] * w[i] >=
                           pop.vsList[i] * x[j] - pop.vmList[i] * p[j] - pop.vtList[i] * w[j]
                           for i in range(pop.num_type) for j in range(pop.num_type) if i != j), "IC")
        # individual rationality
        self.m.addConstrs((pop.vsList[i] * x[i] - pop.vmList[i] * p[i] - pop.vtList[i] * w[i] >= 0
                           for i in range(pop.num_type)), "IR")
        # supply
        self.m.addConstr(gp.quicksum(x[i] * pop.pdf[i] for i in range(pop.num_type)) <= q, "supply")

        # extra testing constraints
        # self.m.addConstr(gp.quicksum(p[i] for i in range(n)) == 0, "no payment")
        # self.m.addConstr(gp.quicksum(w[i] for i in range(n)) == 0, "no wait time")
        # self.m.addConstr(x[0] >= 0.1, "test")
        # self.m.addConstrs((x[i] == 1 for i in range(pop.num_type)), "full allocation")