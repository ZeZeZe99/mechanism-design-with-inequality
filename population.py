"""
Module for a population, which contains distributions of values for service, money, and time
Setting: vm = 1 - vt, uniform on (0,1), vs = g(vm) for g increasing, converted to discrete case

Zejian Huang
"""

import random

from scipy.stats import beta


class Population:
    # number of type
    num_type = 0

    # values
    vsList = []
    vmList = []
    vtList = []
    pdf = []
    smList = []
    tmList = []
    stList = []

    def __init__(self, num_type):
        self.num_type = num_type

    """
    vs: draw random values from uniform (0, 1) and sort (ascending)
    """
    def draw_s_uniform_0_1(self, precision):
        for i in range(self.num_type):
            self.vsList.append(round(random.random(), precision))
        self.vsList.sort()

    """
    vs: draw random values from uniform (a, b) and sort (ascending)
    :param precision: decimal precision
    """
    def draw_s_uniform(self, a, b, precision):
        for i in range(self.num_type):
            self.vsList.append(round(random.uniform(a, b), precision))
        self.vsList.sort()

    """
    vs: generate discrete uniform distribution in (a, b)
    """
    def dist_s_uniform(self, a, b):
        for i in range(self.num_type):
            self.vsList.append((i + 1) * (b - a) / (self.num_type + 1) + a)

    """
    vm & vt: generate discrete uniform distributions in (a, b)
    """
    def dist_mt_uniform(self, a, b):
        for i in range(self.num_type):
            self.vmList.append((i + 1) * (b - a) / (self.num_type + 1) + a)
            self.vtList.append((self.num_type - i) * (b - a) / (self.num_type + 1) + a)
            self.pdf.append(1 / self.num_type)

    # TODO: might need to revise this function
    """
    vm: beta distribution
    """
    def generate_mt_beta(self, a, b):
        for i in range(self.num_type):
            self.vmList.append(beta.rvs(a, b))
        self.vmList.sort()
        for i in range(self.num_type):
            self.vtList.append(1 - self.vmList[i])

        pdf_sum = 0
        for i in range(self.num_type):
            d = beta.pdf(self.vmList[i], a, b)
            self.pdf.append(d)
            pdf_sum += d
        for i in range(self.num_type):
            self.pdf[i] = self.pdf[i] / pdf_sum

    """
    Calculate list of vs/vm, vt/vm, and vs/vt
    """
    def calculate_ratio(self):
        for i in range(self.num_type):
            self.smList.append(self.vsList[i] / self.vmList[i])
            self.tmList.append(self.vtList[i] / self.vmList[i])
            self.stList.append(self.vsList[i] / self.vtList[i])

    """
    clear value lists
    """
    def clear_values(self):
        self.vsList.clear()
        self.vmList.clear()
        self.vtList.clear()
        self.pdf.clear()
        self.smList.clear()
        self.tmList.clear()
        self.stList.clear()