"""
Module for a population, which contains distributions of values for service, money, and time
Setting: vm = 1 - vt, uniform on (0,1), vs = g(vm) for g increasing, converted to discrete case

Zejian Huang
"""

import random

from scipy.stats import beta, geom, expon


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
    vs_perturbation = []
    vm_perturbation = []
    vt_perturbation = []

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
    Generate values uniformly distributed in (a, b)
    """
    def dist_uniform(self, a, b):
        values = []
        for i in range(self.num_type):
            values.append((i + 1) * (b - a) / (self.num_type + 1) + a)
        return values

    """
    Generate values in (a, b) according to exponential distribution
    :param scale: 1 / lambda in pdf lambda * e ^ (- lambda * x)
    """
    def dist_exponential(self, a, b, scale=1):
        values = []
        cdf = 0
        for i in range(self.num_type):
            cdf += 1 / (self.num_type + 1)
            values.append(expon.ppf(cdf, scale=scale))
        return values

    """
    
    """
    def dist_geometric(self, a, b, p):
        values = []
        cdf = 0
        for i in range(self.num_type):
            cdf += 1 / (self.num_type + 1)
            values.append(geom.ppf(cdf, p))
        print(values)
        return values

    """
    Add a perturbation to vs or vm or vt, draw uniformly from (a, b)
    """
    def perturbation(self, a, b, vs=True, vm=True, vt=True, precision=4):
        if vs:
            for i in range(len(self.vsList)):
                off = round(random.uniform(a, b), precision)
                self.vsList[i] += off
                self.vs_perturbation.append(off)
        if vm:
            for i in range(len(self.vmList)):
                off = round(random.uniform(a, b), precision)
                self.vmList[i] += off
                self.vm_perturbation.append(off)
        if vt:
            for i in range(len(self.vtList)):
                off = round(random.uniform(a, b), precision)
                self.vtList[i] += off
                self.vt_perturbation.append(off)

    """
    pdf: generate a uniform type distribution
    """
    def pdf_uniform(self):
        for i in range(self.num_type):
            self.pdf.append(1 / self.num_type)

    """
    pdf: generate a geometric type distribution
    """
    def pdf_geometric(self, p):
        pmf = []
        total = 0
        for i in range(self.num_type):
            temp = geom.pmf(i+1, p)
            total += temp
            pmf.append(temp)
        # for i in range(self.num_type):
        #     pmf[i] /= total
        self.pdf = pmf
        print(sum(pmf))

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
        self.vs_perturbation.clear()
        self.vm_perturbation.clear()
        self.vt_perturbation.clear()
