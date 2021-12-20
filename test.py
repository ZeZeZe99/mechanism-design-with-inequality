xlist = [0.07348803229205303, 0.3504329776649915, 0.7397042940277669]
glist = [0.22947302130996428, 0.3422928984295388, 0.841987047543203]
etalist = [1.756142837094286, 3.31003063553273, 3.928365804373632]

print(xlist[1] - xlist[0] < (glist[1] - glist[0]) * (etalist[1] - etalist[0]))
print(xlist[2] - xlist[1] < (glist[2] - glist[1]) * (etalist[2] - etalist[1]))
print(2 * (xlist[2] - xlist[0]) < (glist[2] - glist[0]) * (etalist[2] - etalist[0]))
print(xlist[1] + xlist[2] - 2 * xlist[0] < (glist[1] - glist[0]) * (etalist[1] - etalist[0]) + \
            (glist[2] - glist[1]) * (etalist[2] - etalist[0]))
print(xlist[1] + xlist[2] - 2 * xlist[0])
print((glist[1] - glist[0]) * (etalist[1] - etalist[0]) + \
            (glist[2] - glist[1]) * (etalist[2] - etalist[0]))