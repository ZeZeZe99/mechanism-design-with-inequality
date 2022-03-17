"""
Module for building LP models in the Myerson environment
Setting: single parameter environment

Zejian Huang
"""

import gurobipy as gp
from gurobipy import GRB, tuplelist


class Myerson:
    primal = None
    dual = None

    """
    Build the LP model, both primal and dual
    :param pop: a population instance
    :param q: ex ante constraint
    :param LAMBDA: social value for revenue
    """

    def __init__(self, pop, q, LAMBDA, rev_max=True):
        self.build_primal(pop, q, LAMBDA, rev_max)
        self.build_dual(pop, q, LAMBDA, rev_max)

    """
    Build the primal LP model
    """
    def build_primal(self, pop, q, LAMBDA, rev_max=True):
        self.primal = gp.Model("primal")
        self.primal.Params.LogToConsole = 0
        self.primal.Params.DualReductions = 0

        # variables
        x = self.primal.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="x", lb=0)
        p = self.primal.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="p", lb=0)

        self.primal.setObjective(
            gp.quicksum(
                (pop.vsList[i] * x[i] - p[i] + LAMBDA * p[i]) * pop.pdfList[i] for i in range(pop.num_type)
            ),
            GRB.MAXIMIZE
        )

        # constraints
        # incentive compatibility
        self.primal.addConstrs((pop.vsList[i] * x[i] - p[i] >= pop.vsList[i] * x[j] - p[j]
                                for i in range(pop.num_type) for j in range(pop.num_type) if i != j),
                               "IC")
        # individual rationality
        self.primal.addConstrs((pop.vsList[i] * x[i] - p[i] >= 0 for i in range(pop.num_type)),
                               "IR")
        # supply
        self.primal.addConstr(gp.quicksum(x[i] * pop.pdfList[i] for i in range(pop.num_type)) <= q, "supply")
        # bound
        self.primal.addConstrs((x[i] <= 1 for i in range(pop.num_type)), "bound")

        # self.primal.addConstr(p[1] >= 0.6, "test")

    """
    Build the dual LP model
    """
    def build_dual(self, pop, q, LAMBDA, rev_max):
        self.dual = gp.Model("dual")
        self.dual.Params.LogToConsole = 0
        self.dual.Params.DualReductions = 0

        # variables
        ic_list = []
        for i in range(pop.num_type):
            for j in range(pop.num_type):
                if i != j:
                    ic_list.append((i, j))
        ic = self.dual.addVars(tuplelist(ic_list), vtype=GRB.CONTINUOUS, name="ic", lb=0)  # ic[i, j]
        ir = self.dual.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="ir", lb=0)
        b = self.dual.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="bound", lb=0)
        sup = self.dual.addVar(vtype=GRB.CONTINUOUS, name="supply", lb=0)

        # objective
        self.dual.setObjective(q * sup + gp.quicksum(b), GRB.MINIMIZE)

        # constraints
        "x"
        self.dual.addConstrs(
            (
                # IC constraints
                gp.quicksum(-pop.vsList[i] * ic[i, j] for j in range(pop.num_type) if i != j)  # Ui >= Uj
                + gp.quicksum(pop.vsList[j] * ic[j, i] for j in range(pop.num_type) if i != j)  # Uj >= Ui
                # IR constraints
                - pop.vsList[i] * ir[i]
                # supply constraint
                + pop.pdfList[i] * sup
                # bound
                + b[i]
                >= pop.vsList[i] * pop.pdfList[i]
                for i in range(pop.num_type)
            ), "x"
        ),
        "p"
        self.dual.addConstrs(
            (
                # IC constraints
                gp.quicksum(ic[i, j] for j in range(pop.num_type) if i != j)  # Ui >= Uj
                + gp.quicksum(-ic[j, i] for j in range(pop.num_type) if i != j)  # Uj >= Ui
                # IR constraints
                + ir[i]
                >= (LAMBDA - 1) * pop.pdfList[i]
                for i in range(pop.num_type)
            ), "p"
        )
