import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from scipy.stats import linregress
import matplotlib.pyplot as plt


def fit_laser_curve(current, power):
    """
    Fit the linear region of a laser curve.

    Parameters
    ----------
    current : array-like
        Laser drive current (mA)
    power : array-like
        Measured optical power (mW)

    Returns
    -------
    Ith : float
        Threshold current (mA)
    slope : float
        Slope efficiency (mW/mA)
    intercept : float
        Intercept of fitted line
    power_fn : callable
        Function mapping current -> power
    """

    current = np.asarray(current)
    power = np.asarray(power)

    # Smooth power to reduce noise
    power_smooth = savgol_filter(power, 5, 2)

    dP_dI = np.gradient(power_smooth, current)
    d2P_dI2 = np.gradient(dP_dI, current)

    # Threshold = max curvature
    idx = np.argmax(d2P_dI2)
    Ith = current[idx]

    # Keep only region above threshold
    mask = current > Ith

    slope, intercept, *_ = linregress(current[mask], power[mask])

    def power_fn(I):
        return 2 * max(0, slope * I + intercept)    # multiplied by 2 because calibration was done after 50% splitter

    return Ith, slope, intercept, power_fn

class ExtLaser:
    def __init__(self, calibration: str):
        df = (
            pd.read_csv(
                calibration,
                skiprows=5,
                na_values="X",    # convert X -> NaN
            )
        ).fillna(value=-np.inf)

        df = df.rename(columns={
            "I laser (mA)": "current_mA",
            "Laser power a 20ºC (dBm) (*)": "power_dBm_20",
            "Laser power a 25ºC (dBm) (*)": "power_dBm_25",
            "Laser power a 30ºC (dBm) (*)": "power_dBm_30",
            "Laser power a 20ºC (mW) (*)": "power_mW_20",
            "Laser power a 25ºC (mW) (*)": "power_mW_25",
            "Laser power a 30ºC (mW) (*)": "power_mW_30",
        })
        self.temps = (20,25,30)
        current=df["current_mA"]
        power_mW_20=df["power_mW_20"]
        power_mW_25=df["power_mW_25"]
        power_mW_30=df["power_mW_30"]
        
        self.Ith_20, self.slope_20, self.intercept_20, self.power_mW_T_20 = fit_laser_curve(current, power_mW_20)
        self.Ith_25, self.slope_25, self.intercept_25, self.power_mW_T_25 = fit_laser_curve(current, power_mW_25)
        self.Ith_30, self.slope_30, self.intercept_30, self.power_mW_T_30 = fit_laser_curve(current, power_mW_30)

    def power_dBm_T_20(self, i):
        return 10 * np.log10(self.power_mW_20(i))

    def power_dBm_T_25(self, i):
        return 10 * np.log10(self.power_mW_25(i))

    def power_dBm_T_30(self, i):
        return 10 * np.log10(self.power_mW_30(i))
