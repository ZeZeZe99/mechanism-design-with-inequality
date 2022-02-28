"""
Module for a population, which contains distributions of values for service, money, and time
Setting: vm = 1 - vt, uniform on (0,1), vs = g(vm) for g increasing, converted to discrete case

Zejian Huang
"""

import random

from scipy.stats import beta, geom, expon
from scipy.optimize import fsolve


class Population:
    # number of type
    num_type = 0

    # values
    vsList = []
    vmList = []
    vtList = []
    # distribution
    pdfList = []
    cdfList = []
    # ratio of values
    smList = []
    tmList = []
    stList = []
    # virtual values
    vir_vsList = []
    # virtual ratio of values
    vir_smList = []

    def __init__(self, num_type):
        self.num_type = num_type

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
    def value_uniform(self, a, b):
        values = []
        for i in range(self.num_type):
            values.append((i + 1) * (b - a) / (self.num_type + 1) + a)
        return values

    """
    Generate values according to (discrete) exponential distribution
    :param scale: 1 / lambda in pdf lambda * e ^ (- lambda * x)
    """
    def value_exponential(self, scale=1):
        values = []
        cdf = 0
        for i in range(self.num_type):
            cdf += 1 / (self.num_type + 1)
            values.append(expon.ppf(cdf, scale=scale))
        return values

    """
    Generate values according to (discrete) mixture Kumaraswamy distribution
    The CDF of the mixture distribution is q*(1-(1-x)^a)^b + (1-q)*(1-(1-x)^c)^d
    """
    def value_kumaraswamy(self, a, b, c, d, q, precision=4):
        values = []
        cdf = 0
        for i in range(self.num_type):
            cdf += 1 / (self.num_type + 1)

            # cdf = q * F(x) + (1-q) * G(x)
            def func(x):
                return q * (1 - (1-x**a)**b) + (1-q) * (1 - (1-x**c)**d) - cdf
            v = fsolve(func, 1e-4)[0]
            values.append(round(v.item(), precision))
        return values

    """
    Add a perturbation to vs or vm or vt, draw uniformly from (a, b)
    """
    def perturbation(self, a, b, vs=True, vm=True, vt=True, precision=4):
        if vs:
            for i in range(len(self.vsList)):
                off = round(random.uniform(a, b), precision)
                self.vsList[i] += off
        if vm:
            for i in range(len(self.vmList)):
                off = round(random.uniform(a, b), precision)
                self.vmList[i] += off
        if vt:
            for i in range(len(self.vtList)):
                off = round(random.uniform(a, b), precision)
                self.vtList[i] += off

    """
    Generate a uniform type distribution
    """
    # TODO: Can we generate values using this pdf and cdf? We don't want end points for values
    def type_uniform(self):
        cdf = 0
        for i in range(self.num_type):
            pdf = 1 / self.num_type
            # cdf += pdf  # include right end point
            cdf = (i+1) / (self.num_type + 1)  # exclude both end points
            self.pdfList.append(pdf)
            self.cdfList.append(cdf)

    """
    Generate a type distribution according to a mixture of two Kumaraswamy distributions,
    by taking n points from (0,1) evenly (excluding endpoints), calculating the PMF, then normalizing.
    The PMF is q * abx^(a-1) * (1-x^a)^(b-1) + (1-q) * cdx^(c-1) * (1-x^c)^(d-1)
    """
    def type_kumaraswamy(self, a, b, c, d, q, precision=4):
        total = 0
        cdf = 0
        temp = []
        for i in range(self.num_type):
            x = (i+1) / (self.num_type + 1)
            pmf = q * a*b*x**(a-1) * (1-x**a)**(b-1) + (1 - q) * c*d*x**(c-1) * (1-x**c)**(d-1)
            temp.append(pmf)
            total += pmf
        for i in range(self.num_type):
            pmf = round(temp[i] / total, precision)
            cdf += pmf
            self.pdfList.append(pmf)
            self.cdfList.append(cdf)

    """
    Calculate list of vs/vm, vt/vm, and vs/vt
    """
    def calculate_ratio(self):
        for i in range(self.num_type):
            self.smList.append(self.vsList[i] / self.vmList[i])
            self.tmList.append(self.vtList[i] / self.vmList[i])
            self.stList.append(self.vsList[i] / self.vtList[i])

    """
    Calculate virtual value for vs, i.e. v_i - (1-F(v_i)) / f(v_i) * (v_{i+1} - v_i)
    """
    def calculate_virtual_s(self):
        for i in range(self.num_type - 1):
            self.vir_vsList.append(self.vsList[i] - (1 - self.cdfList[i]) / self.pdfList[i]
                                   * (self.vsList[i+1] - self.vsList[i]))
        self.vir_vsList.append(self.vsList[-1])  # last type

    """
    Calculate virtual value for vs/vm
    """
    def calculate_virtual_sm(self):
        for i in range(self.num_type - 1):
            self.vir_smList.append(self.smList[i] - (1 - self.cdfList[i]) / self.pdfList[i]
                                   * (self.smList[i + 1] - self.smList[i]))
        self.vir_smList.append(self.smList[-1])  # last type

    """
    Check if the distribution of vs satisfies monotone regularity constraint
    """
    def regular_s(self):
        for i in range(self.num_type - 1):
            if self.vir_vsList[i] > self.vir_vsList[i+1]:
                return False
        return True

    """
    clear value lists
    """
    def clear_values(self):
        self.vsList.clear()
        self.vmList.clear()
        self.vtList.clear()
        self.pdfList.clear()
        self.cdfList.clear()
        self.smList.clear()
        self.tmList.clear()
        self.stList.clear()
        self.vir_vsList.clear()
        self.vir_smList.clear()

