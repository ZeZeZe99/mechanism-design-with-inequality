"""
With the Joint Monotonicity:
[x(v)-x(v')]*[v/M(v)-v'/M(v')] >= [w(v)-w(v')]*[T(v)/M(v)-T(v')/M(v')],
this program draws x's and w's that satisfy the JM, calculates p's, and checks whether BIC is satisfied,
i.e., whether JM is sufficient for implementation.
"""

import random

from population import Population

x_list = []
p_list = []
w_list = []
# derivatives of vs/vm and vt/vm
d_sm_list = []
d_tm_list = []

"""
Draw random values for x's and w's
0 <= x <= 1
0 <= w <= max_w
"""
def draw(num, max_w=1, precision=4):
    for i in range(num):
        x_list.append(round(random.random(), precision))
        w_list.append(round(max_w*random.random(), precision))


"""
Clear lists
"""
def clear():
    x_list.clear()
    p_list.clear()
    w_list.clear()


"""
Check if the Joint Monotonicity condition is satisfied
"""
def check_JM(num):
    for i in range(num):
        for j in range(num):
            if i != j:
                if (x_list[i] - x_list[j])*(pop.smList[i] - pop.smList[j]) \
                        < (w_list[i] - w_list[j]) * (pop.tmList[i] - pop.tmList[j]):
                    return False
    return True


if __name__ == '__main__':
    n = 9
    pop = Population(n)

    '''Generate vs, vm, vt'''
    pop.vsList = pop.value_kumaraswamy(1.75, 10, 8, 5, 0.75)
    pop.vmList = pop.value_uniform(1, 1)
    for i in range(n):
        pop.vtList.append(pop.vsList[i]**2)
    pop.calculate_ratio()

    '''Calculate derivatives of vs/vm and vt/vm'''
    for i in range(n):
        if i == 0:
            d_sm_list.append(pop.smList[0])
            d_tm_list.append(pop.tmList[0])
        else:
            d_sm_list.append(pop.smList[i] - pop.smList[i-1])
            d_tm_list.append(pop.tmList[i] - pop.tmList[i-1])

