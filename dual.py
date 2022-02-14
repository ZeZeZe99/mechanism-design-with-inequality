"""
Module for building the dual linear programming model

Zejian Huang
"""

import gurobipy as gp
from gurobipy import GRB, tuplelist


class Dual:
    m = None

    """
    Initialize the LP model
    :param pop: a population instance
    :param q: ex ante constraint
    :param LAMBDA: social value for revenue
    """

    def __init__(self, pop, q, LAMBDA):
        self.m = gp.Model("Dual")
        self.m.Params.LogToConsole = 0
        self.m.Params.DualReductions = 0

        # variables
        # ic = self.m.addVars(pop.num_type * (pop.num_type - 1), vtype=GRB.CONTINUOUS, name="ic", lb=0)  # ic[i]

        ic_list = []
        for i in range(pop.num_type):
            for j in range(pop.num_type):
                if i != j:
                    ic_list.append((i, j))
        ic = self.m.addVars(tuplelist(ic_list), vtype=GRB.CONTINUOUS, name="ic", lb=0)  # ic[i, j]
        ir = self.m.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="ir", lb=0)
        b = self.m.addVars(pop.num_type, vtype=GRB.CONTINUOUS, name="bound", lb=0)
        sup = self.m.addVar(vtype=GRB.CONTINUOUS, name="supply", lb=0)

        # objective
        self.m.setObjective(q * sup + gp.quicksum(b), GRB.MINIMIZE)

        # constraints using ic[i, j]
        # x
        self.m.addConstrs(
            (
                # IC constraints
                gp.quicksum(-pop.vsList[i] * ic[i, j] for j in range(pop.num_type) if i != j)  # Ui >= Uj
                + gp.quicksum(pop.vsList[j] * ic[j, i] for j in range(pop.num_type) if i != j)  # Uj >= Ui
                # IR constraints
                - pop.vsList[i] * ir[i]
                # supply constraint
                + pop.pdf[i] * sup
                # bound
                + b[i]
                >= pop.vsList[i] * pop.pdf[i]
                for i in range(pop.num_type)
            ), "x"
        )
        # p
        self.m.addConstrs(
            (
                # IC constraints
                gp.quicksum(pop.vmList[i] * ic[i, j] for j in range(pop.num_type) if i != j)  # Ui >= Uj
                + gp.quicksum(-pop.vmList[j] * ic[j, i] for j in range(pop.num_type) if i != j)  # Uj >= Ui
                # IR constraints
                + pop.vmList[i] * ir[i]
                >= (LAMBDA - pop.vmList[i]) * pop.pdf[i]
                for i in range(pop.num_type)
            ), "p"
        )
        # w
        self.m.addConstrs(
            (
                # IC constraints
                gp.quicksum(pop.vtList[i] * ic[i, j] for j in range(pop.num_type) if i != j)  # Ui >= Uj
                + gp.quicksum(-pop.vtList[j] * ic[j, i] for j in range(pop.num_type) if i != j)  # Uj >= Ui
                # IR constraints
                + pop.vtList[i] * ir[i]
                >= -pop.vtList[i] * pop.pdf[i]
                for i in range(pop.num_type)
            ), "w"
        )
        self.m.addConstr(sup == 0, "test")

        # constraints using ic[i]
        # # x
        # self.m.addConstrs(
        #     (  # IC constraints
        #         gp.quicksum(-pop.vsList[i] * ic[i * (pop.num_type - 1) + j]
        #                     for j in range(pop.num_type-1))  # Ui >= Uj
        #         + gp.quicksum(pop.vsList[j] * ic[j * (pop.num_type - 1) + i - 1]
        #                       for j in range(i))  # Uj >= Ui when i > j
        #         + gp.quicksum(pop.vsList[j] * ic[j * (pop.num_type - 1) + i]
        #                       for j in range(i + 1, pop.num_type))  # Uj >= Ui when i < j
        #         # IR constraints
        #         - pop.vsList[i] * ir[i]
        #         # supply constraint
        #         + pop.pdf[i] * sup[0]
        #         # bound
        #         + b[i]
        #         >= pop.vsList[i] * pop.pdf[i]
        #         for i in range(pop.num_type)
        #     ), "x"
        # )
        # # p
        # self.m.addConstrs(
        #     (  # IC constraints
        #         gp.quicksum(pop.vmList[i] * ic[i * (pop.num_type - 1) + j]
        #                     for j in range(pop.num_type - 1))  # Ui >= Uj
        #         + gp.quicksum(-pop.vmList[j] * ic[j * (pop.num_type - 1) + i - 1]
        #                       for j in range(i))  # Uj >= Ui when i > j
        #         + gp.quicksum(-pop.vmList[j] * ic[j * (pop.num_type - 1) + i]
        #                       for j in range(i + 1, pop.num_type))  # Uj >= Ui when i < j
        #         # IR constraints
        #         + pop.vmList[i] * ir[i]
        #         >= (LAMBDA - pop.vmList[i]) * pop.pdf[i]
        #         for i in range(pop.num_type)
        #     ), "p"
        # )
        # # w
        # self.m.addConstrs(
        #     (  # IC constraints
        #         gp.quicksum(pop.vtList[i] * ic[i * (pop.num_type - 1) + j]
        #                     for j in range(pop.num_type - 1))  # Ui >= Uj
        #         + gp.quicksum(-pop.vtList[j] * ic[j * (pop.num_type - 1) + i - 1]
        #                       for j in range(i))  # Uj >= Ui when i > j
        #         + gp.quicksum(-pop.vtList[j] * ic[j * (pop.num_type - 1) + i]
        #                       for j in range(i + 1, pop.num_type))  # Uj >= Ui when i < j
        #         # IR constraints
        #         + pop.vtList[i] * ir[i]
        #         >= -pop.vtList[i] * pop.pdf[i]
        #         for i in range(pop.num_type)
        #     ), "t"
        # )
