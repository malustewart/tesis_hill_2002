import numpy as np

G_dB_vs_Pout_curve_params_1 = (11.40506784,  0.08843997, -0.11878584,  0.88176066, -0.10244627)
G_dB_vs_Pout_curve_params_2 = ( 7.07659937, -0.74377734, -0.19111317,  0.12290653, -0.03331924)

T_tbf_isolator_1 = -2.48
T_tbf_isolator_2 = T_tbf_isolator_1  # no fue medido, solo estimo

def G_dB_vs_Ptot_curve_model(Pout, a, b, c, d, e):
    return a + b * Pout + c * Pout**2 + d / (Pout + e) 

def T_est_by_Ptot_lin(Ptot_mW, G_dB_vs_Ptot_curve_params):
    T_dB = T_est_by_Ptot_dB(Ptot_mW, G_dB_vs_Ptot_curve_params)
    return np.pow(10, T_dB/10)

def T_est_by_Ptot_dB(Ptot_mW, G_dB_vs_Ptot_curve_params):
    G_dB = G_dB_vs_Ptot_curve_model(Ptot_mW, *G_dB_vs_Ptot_curve_params)
    T_dB = -G_dB
    return T_dB

def T_est_by_slope_lin(delta_x, delta_y):
    return delta_x / delta_y

def T_est_by_slope_dB(delta_x, delta_y):
    return 10*np.log10(T_est_by_slope_lin(delta_x, delta_y))

