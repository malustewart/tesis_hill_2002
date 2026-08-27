import math
import numpy as np
import matplotlib.pyplot as plt

T1_in = 0.3
T2_in = 1

T1_out = 1
T2_out = 1

Tac_11 = 0.5
Tac_12 = 0.5
Tac_22 = 0.5
Tac_21 = 0.5

T11 = T1_out * Tac_11 * T1_in
T12 = T1_out * Tac_12 * T2_in
T21 = T2_out * Tac_21 * T1_in
T22 = T2_out * Tac_22 * T2_in

G01 = 1000 # ganancia de pequeña señal del SOA, dependiente del bombeo
Psat1 = 32  # mW  # flujo de saturacion del SOA, dependiente del bombeo

G02 = 600 # ganancia de pequeña señal del SOA, dependiente del bombeo
Psat2 = 15  # mW # flujo de saturacion del SOA, dependiente del bombeo

P1 = []
P2 = []

# T[row][col]
# row: input SOA
# col: output SOA
# T = np.array([
#         [0.5, 0.5], # T11, T12
#         [0.5, 0.5]  # T21, T22
#     ])

Pe1 = np.linspace(0,3,200)
Pe2 = np.zeros_like(Pe1)

def calc_P(Pe, T, Psat, G0):
    lnG0 = math.log(math.e, G0)
    return max((T)/(1-T)*lnG0*Psat-Pe/T, 0)

def calc_P1(Pe):
    return calc_P(Pe, T11, Psat1, G01)

def calc_P2(Pe):
    return calc_P(Pe, T22, Psat2, G02)


Pe1 = np.concatenate((Pe1, Pe1[::-1]))
# Pe1 = np.concatenate((Pe1, Pe1[::-1]))
Pe2 = np.concatenate((Pe2, Pe2[::-1]))
# Pe2 = np.concatenate((Pe2, Pe2[::-1]))

p1 = calc_P(0, T11, Psat1, G01)
p2 = calc_P(0, T22, Psat2, G02)
cross_power_min = p1*T11-p2*T22*T11/T12
cross_power_max = p1*T11-p2*T21

print(f"P1 (P_in=0) = {p1}")
print(f"P2 (P_in=0) = {p2}")
print(f"P_cross min = {cross_power_min}")
print(f"P_cross max = {cross_power_max}")

for _ in range(10):
    p1 = calc_P1(T21*p2)
    p2 = calc_P2(T12*p1)

for pe1, pe2 in zip(Pe1, Pe2):
    for _ in range(100):
        p2 = calc_P2(pe2+T12*p1)
        p1 = calc_P1(pe1+T21*p2)
    P1.append(p1)
    P2.append(p2)

plt.figure()
plt.plot(Pe1,P1, marker='o')
plt.plot(Pe1,P2, marker='o')
plt.axvline(cross_power_min)
plt.axvline(cross_power_max)
plt.grid()

P1 = np.array(P1)
P2 = np.array(P2)

# plt.figure()
# plt.plot(Pe1,P1*T11+P2*T21+Pe1)
# plt.grid()
plt.show()


