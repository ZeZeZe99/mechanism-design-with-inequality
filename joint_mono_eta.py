"""
Look at the discrete version of joint monotonicity function
(v-v')(x(v)-x(v')) >= (g(v)-g(v'))(eta(v)-eta(v'))
This program would randomly draw some x, g, eta values and check whether the joint monotonicity is sufficient for BIC

Zejian Huang
"""

import random
from scipy.stats import expon


def draw():
    xlist = []
    glist = []
    etalist = []

    for i in range(3):
        # draw x, g from U(0,1)
        xlist.append(random.random())
        glist.append(random.random())
        # draw eta from Expo(1)
        etalist.append(expon.rvs(1))
    # sort x, g, eta
    xlist.sort()
    glist.sort()
    etalist.sort()
    return xlist, glist, etalist


# Check the IR and IC constraints
def checkJointMono(xlist, glist, etalist):
    # Check the IC constraints
    if xlist[1] - xlist[0] < (glist[1] - glist[0]) * (etalist[1] - etalist[0]):
        return False
    if xlist[2] - xlist[1] < (glist[2] - glist[1]) * (etalist[2] - etalist[1]):
        return False
    if 2 * (xlist[2] - xlist[0]) < (glist[2] - glist[0]) * (etalist[2] - etalist[0]):
        return False
    # Check the IR constraints
    if xlist[0] - etalist[0] < 0:
        return False
    if xlist[0] + xlist[1] - etalist[0] - etalist[1] < 0:
        return False
    return True


# Check the goal inequality
def checkGoal(xlist, glist, etalist):
    if xlist[1] + xlist[2] - 2 * xlist[0] < (glist[1] - glist[0]) * (etalist[1] - etalist[0]) + \
            (glist[2] - glist[1]) * (etalist[2] - etalist[0]):
        print("x: ", end='')
        print(xlist)
        print("g: ", end='')
        print(glist)
        print("eta: ", end='')
        print(etalist)
        print(xlist[1] + xlist[2] - 2 * xlist[0], (glist[1] - glist[0]) * (etalist[1] - etalist[0]) + \
            (glist[2] - glist[1]) * (etalist[2] - etalist[0]))
        return True
    return False


if __name__ == '__main__':
    done = False
    count = 0
    while not done:
        count += 1
        x, g, eta = draw()
        if checkJointMono(x, g, eta):
            print(count)
            if checkGoal(x, g, eta):
                print(count)
                done = True
