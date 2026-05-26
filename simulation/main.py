import math
import numpy as np
import matplotlib.pyplot as plt

T11 = 0.9
T12 = 0.9
T21 = 0.9
T22 = 0.9

G01 = 100
Ps1 = 1  # mW

G02 = 100
Ps2 = 1  # mW

P1 = []
P2 = []

def P(Pe, T, Ps, G0):
    lnG0 = math.log(math.e, G0)
    return max((T)/(1-T)*lnG0*Ps-Pe/T, 0)

def calc_P1(Pe):
    return P(Pe, T11, Ps1, G01)

def calc_P2(Pe):
    return P(Pe, T22, Ps2, G02)

Pe1 = np.linspace(0,3, 200)
Pe2 = np.zeros_like(Pe1)

Pe1 = np.concatenate((Pe1, Pe1[::-1]))
Pe1 = np.concatenate((Pe1, Pe1[::-1]))
Pe2 = np.concatenate((Pe2, Pe2[::-1]))
Pe2 = np.concatenate((Pe2, Pe2[::-1]))

p1 = P(0, T11, Ps1, G01)
p2 = P(0, T22, Ps2, G02)

for _ in range(10):
    p1 = calc_P1(T21*p2)
    p2 = calc_P2(T12*p1)

for pe1, pe2 in zip(Pe1, Pe2):
    p1 = calc_P1(pe1+T21*p2)
    p2 = calc_P2(pe2+T12*p1)
    P1.append(p1)
    P2.append(p2)

plt.figure()
plt.plot(Pe1,P1)
plt.plot(Pe1,P2)
plt.grid()

P1 = np.array(P1)
P2 = np.array(P2)

plt.figure()
plt.plot(Pe1,P1*T11+P2*T21+Pe1)
plt.grid()
plt.show()

