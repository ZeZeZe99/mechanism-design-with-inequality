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
    regularity = []

    def __init__(self, num_type):
        self.num_type = num_type

    """
    draw random values from uniform (0, 1) and sort (ascending)
    """
    def draw_uniform_0_1(self, precision=4):
        for i in range(self.num_type):
            self.vsList.append(round(random.random(), precision))
        self.vsList.sort()

    """
    draw random values from uniform (a, b) and sort (ascending)
    :param precision: decimal precision
    """
    def draw_uniform(self, a, b, precision=2):
        values = []
        for i in range(self.num_type):
            values.append(round(random.uniform(a, b), precision))
        values.sort()
        return values

    """
    generate discrete uniform distribution in (a, b)
    """
    def dist_uniform(self, a, b):
        values = []
        for i in range(self.num_type):
            values.append((i + 1) * (b - a) / (self.num_type + 1) + a)
        return values

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
    Add a perturbation to vs or vm or vt, draw uniformly from (a, b)
    """
    def perturbation(self, a, b, vs=True, vm=True, vt=True, precision=4):
        if vs:
            for i in range(len(self.vsList)):
                self.vsList[i] += round(random.uniform(a, b), precision)
        if vm:
            for i in range(len(self.vmList)):
                self.vmList[i] += round(random.uniform(a, b), precision)
        if vt:
            for i in range(len(self.vtList)):
                self.vtList[i] += round(random.uniform(a, b), precision)

    """
    pdf: generate a uniform type distribution
    """
    def pdf_uniform(self):
        for i in range(self.num_type):
            self.pdf.append(1 / self.num_type)

    """
    Calculate list of vs/vm, vt/vm, and vs/vt
    """
    def calculate_ratio(self):
        for i in range(self.num_type):
            self.smList.append(self.vsList[i] / self.vmList[i])
            self.tmList.append(self.vtList[i] / self.vmList[i])
            self.stList.append(self.vsList[i] / self.vtList[i])

    """
    Calculate vs values for regularity, i.e. v_i - (1-F(v_i)) / f(v_i) * (v_{i+1} - v_i)
    """
    def calculate_regularity_s(self):
        cdf = 0
        for i in range(self.num_type - 1):
            cdf += self.pdf[i]
            self.regularity.append(self.vsList[i] - (1 - cdf) / self.pdf[i] * (self.vsList[i+1] - self.vsList[i]))
        self.regularity.append(self.vsList[-1])  # last type

    """
    Check if the distribution of vs satisfies monotone regularity constraint
    """
    def mono_regularity_s(self):
        for i in range(self.num_type - 1):
            if self.regularity[i] > self.regularity[i+1]:
                return False
        return True

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
        self.regularity.clear()