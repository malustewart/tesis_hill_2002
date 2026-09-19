import numpy as np

# Ptot1_max = 2 #mW
# Ptot2_max = 2 #mW


def db_to_linear(x):
    return 10**(x / 10)

def linear_to_db(x):
    return 10 * np.log10(x)





# Tac11_dB = -3.43
# Tac12_dB = -3.31
# Tac21_dB = -3.06
# Tac22_dB = -3.38


def db_to_linear(x):
    return 10**(x / 10)

def linear_to_db(x):
    return 10 * np.log10(x)


def calc_transition_power(
    T11_dB,
    T12_dB,
    T21_dB,
    T22_dB,
    Ptot1_mW,
    Ptot2_mW,
):
    T11 = db_to_linear(T11_dB)
    T12 = db_to_linear(T12_dB)
    T21 = db_to_linear(T21_dB)
    T22 = db_to_linear(T22_dB)

    lateral1 = Ptot1_mW*T11 - Ptot2_mW*T22*T11/T12
    lateral2 = Ptot1_mW*T11 - Ptot2_mW*T21
    center = (lateral1 + lateral2) / 2

    if lateral2 > lateral1:
        upper = lateral2
        lower = lateral1
    else:
        lower = lateral2
        upper = lateral1
            
    return lower, center, upper


def main():
    from calc_T_estimation import T_est_by_Ptot_dB
    from calc_T_estimation import G_dB_vs_Pout_curve_params_1 as params1
    from calc_T_estimation import G_dB_vs_Pout_curve_params_2 as params2

    def T1(Ptot1_mW):
        return T_est_by_Ptot_dB(Ptot1_mW, params1)

    def T2(Ptot2_mW):
        return T_est_by_Ptot_dB(Ptot2_mW, params2)

    Ptot1_mW = 2.56 / 0.56
    Ptot2_mW = 1.04 / 0.56

    # T11_dB = -9.14
    T11_dB = T1(Ptot1_mW)
    T12_dB = -9.43
    T21_dB = -15.17
    # T22_dB = -15.25
    T22_dB = T2(Ptot2_mW)


    lower, center, upper = calc_transition_power(
        T11_dB,
        T12_dB,
        T21_dB,
        T22_dB,
        Ptot1_mW,
        Ptot2_mW,
    )

    T11 = db_to_linear(T11_dB)
    T12 = db_to_linear(T12_dB)
    T21 = db_to_linear(T21_dB)
    T22 = db_to_linear(T22_dB)


    T1_diff = T11 - T12
    T2_diff = T22 - T21

    print("Ptot (mW):")
    print(f"\tPtot1: {Ptot1_mW}")
    print(f"\tPtot2: {Ptot2_mW}")

    print()

    print("Loop transmissions (dB):")
    print(f"\tT11_db: {T11_dB}")
    print(f"\tT12_db: {T12_dB}")
    print(f"\tT21_db: {T21_dB}")
    print(f"\tT22_db: {T22_dB}")

    print()
    print("Loop transmissions (linear):")

    print(f"\tT11: {T11}")
    print(f"\tT12: {T12}")
    print(f"\tT21: {T21}")
    print(f"\tT22: {T22}")

    print()

    print(f"T11 - T12 = {T1_diff}")
    print(f"T22 - T21 = {T2_diff}")

    print(f"case A (Tii-Tij=0) (perfect step):")
    print(f"case B (Tii-Tij>0) (slope):")
    print(f"case C (Tii-Tij<0) (histeresis):")
    print()

    print(f"\tlower: {lower}")
    print(f"\tcenter:{center}")
    print(f"\tupper: {upper}")


if __name__=="__main__":
    main()