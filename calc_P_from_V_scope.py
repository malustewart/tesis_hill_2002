import tomllib
from pathlib import Path
from dataclasses import dataclass
import math
import argparse

@dataclass(frozen=True)
class SetupDescription:
    # Fixed setup parameters
    name: str = "Hill2002TwoRingsD"

    ext_laser : str = "SN:XXXX-PN:XXXX"
    ext_laser_lambda_nm : float = 1555.0
    ext_laser_amplifier : str = "SN:XXXX-PN:XXXX"
    tbf_0: str = "SN:XXXX-PN:XXXX"
    tap_0 : str = "SN:XXXX-PN:XXXX"
    tap_0_loss_in_to_out_meas_dB : float = None
    tap_0_loss_in_to_out_pass_dB : float = None
    PD_0: str = "SN:XXXX-PN:XXXX"
    PD_0_resp: float = 1.0  # A/W
    coupler_1: str = "SN:XXXX-PN:XXXX"
    coupler_1_T_from_ext_laser_dB: float = None
    coupler_1_T_from_ring_laser_dB: float = None

    soa_1 : str = "SN:XXXX-PN:XXXX"
    PC_1 : str = "SN:XXXX-PN:XXXX"
    tbf_1: str = "SN:XXXX-PN:XXXX"
    # tbf_1_bw_nm: float = 1
    tap_1: str = "SN:XXXX-PN:XXXX"
    tap_1_loss_in_to_out_meas_dB : float = None
    tap_1_loss_in_to_out_pass_dB : float = None
    PD_1: str = "SN:XXXX-PN:XXXX"
    PD_1_resp: float = 1.0  # A/W
    attenuator_1_out: str = "None"
    attenuator_1_in: str = "SN:XXXX-PN:XXXX"

    soa_2 : str = "SN:XXXX-PN:XXXX"
    PC_2 : str = "SN:XXXX-PN:XXXX"
    tbf_2: str = "SN:XXXX-PN:XXXX"
    # tbf_2_bw_nm: float = 1
    tap_2: str = "SN:XXXX-PN:XXXX"
    tap_2_loss_in_to_out_meas_dB : float = None
    tap_2_loss_in_to_out_pass_dB : float = None
    PD_2: str = "SN:XXXX-PN:XXXX"
    PD_2_resp: float = 1.0  # A/W
    attenuator_2_out: str = "SN:XXXX-PN:XXXX"
    attenuator_2_in: str = "SN:XXXX-PN:XXXX"

    tap_3: str = "SN:XXXX-PN:XXXX"
    tap_3_loss_in_to_out_meas_dB : float = None
    tap_3_loss_in_to_out_pass_dB : float = None
    coupler_2: str = "SN:XXXX-PN:XXXX"
    coupler_2_T_1_1_dB: float = None
    coupler_2_T_1_2_dB: float = None
    coupler_2_T_2_1_dB: float = None
    coupler_2_T_2_2_dB: float = None

    scope_impedance_ch1_ohm: float = 497.0
    scope_impedance_ch2_ohm: float = 500.0
    scope_impedance_ch3_ohm: float = 490.0
    scope_impedance_ch4_ohm: float = 50.0

    meas_arrival_time_diff_scope_ch1_to_ch2_ns : float = 0.0
    meas_arrival_time_diff_scope_ch2_to_ch3_ns : float = 0.0

    T1in_dB = -5.4
    T1_iso_tbf_dB = -2.48
    T2_iso_tbf_dB = -2.48


def parse_setup_description_toml(
        setup_description_path: str,
    ) -> SetupDescription:

    """Load setup description from TOML file."""
    
    with open(Path(setup_description_path), "rb") as f:
        toml_data = tomllib.load(f)
        setup_description = toml_data["SetupDescription"]

    return SetupDescription(**setup_description)

def calc_P_ext(setup_description : SetupDescription, V_scope_mV : float):
    # measured currents (mA)
    meas_current_ch1 = V_scope_mV / setup_description.scope_impedance_ch1_ohm

    # optical powers arriving at PD (mW)
    meas_power_ch1 = meas_current_ch1 / setup_description.PD_0_resp

    # optical powers arriving at PD (dBm)

    ## avoid division by zero
    meas_power_ch1 = abs(meas_power_ch1) + 1e-30

    ## calc dBm
    meas_power_ch1_dBm = 10 * math.log10(meas_power_ch1)

    # real optical powers (dBm)
    real_power_ext_laser_dBm = (
        meas_power_ch1_dBm
        + setup_description.tap_0_loss_in_to_out_meas_dB
        - setup_description.tap_0_loss_in_to_out_pass_dB
        + setup_description.coupler_1_T_from_ext_laser_dB
        - setup_description.tap_3_loss_in_to_out_pass_dB
    )

    # real optical powers (mW)
    real_power_ext_laser = pow(10, real_power_ext_laser_dBm / 10)

    return real_power_ext_laser


def calc_P_ring_1(setup_description : SetupDescription, V_scope_mV : float):
    # measured currents (mA)
    meas_current_ch2 = V_scope_mV / setup_description.scope_impedance_ch2_ohm

    # optical powers arriving at PD (mW)
    meas_power_ch2 = meas_current_ch2 / setup_description.PD_1_resp

    # optical powers arriving at PD (dBm)

    ## avoid division by zero
    meas_power_ch2 = abs(meas_power_ch2) + 1e-30

    ## calc dBm
    meas_power_ch2_dBm = 10 * math.log10(meas_power_ch2)

    real_power_ring_laser_1_dBm = (
        meas_power_ch2_dBm
        + setup_description.tap_1_loss_in_to_out_meas_dB
        - setup_description.tap_1_loss_in_to_out_pass_dB
        - setup_description.T1_iso_tbf_dB
    )
    real_power_ring_laser_1 = pow(10, real_power_ring_laser_1_dBm / 10)

    return real_power_ring_laser_1


def calc_P_ring_2(setup_description : SetupDescription, V_scope_mV : float):
    # measured currents (mA)
    meas_current_ch3 = V_scope_mV / setup_description.scope_impedance_ch3_ohm

    # optical powers arriving at PD (mW)
    meas_power_ch3 = meas_current_ch3 / setup_description.PD_2_resp

    # optical powers arriving at PD (dBm)

    ## avoid division by zero
    meas_power_ch3 = abs(meas_power_ch3) + 1e-30

    ## calc dBm
    meas_power_ch3_dBm = 10 * math.log10(meas_power_ch3)

    real_power_ring_laser_2_dBm = (
        meas_power_ch3_dBm
        + setup_description.tap_2_loss_in_to_out_meas_dB
        - setup_description.tap_2_loss_in_to_out_pass_dB
        - setup_description.T2_iso_tbf_dB
    )

    # real optical powers (mW)
    real_power_ring_laser_2 = pow(10, real_power_ring_laser_2_dBm / 10)

    return real_power_ring_laser_2

def calc_P(setup_description, laser, V_scope_mV):
    if laser == "e":
        return calc_P_ext(setup_description, V_scope_mV)
    elif laser == "1":
        return calc_P_ring_1(setup_description, V_scope_mV)
    elif laser == "2":
        return calc_P_ring_2(setup_description, V_scope_mV)
    else: 
        return None

def print_result(laser, P_mW):
    P_mW = calc_P(setup_description, laser, V_scope_mV)
    P_dBm = 10*math.log10(P_mW)
    print(f"scope reading: {V_scope_mV:8.4f} mV")
    print(f"laser {laser} power: {P_mW:8.4f} mW")
    print(f"               {P_dBm:8.4f} dBm")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("laser", choices=["e", "1", "2"], type=float, nargs="?")
    parser.add_argument("V_scope_mV", type=float, nargs="?")
    parser.add_argument("setup_description_path", nargs="?", default=r".\configs\two_rings_setup_D\setup_description.toml", type=Path)
    parser.add_argument("-i", "--interactive", action="store_true")

    args = parser.parse_args()

    setup_description_path = args.setup_description_path
    setup_description = parse_setup_description_toml(setup_description_path)

    if args.interactive:
        while True:
            # read laser
            while True:
                laser = input("Laser [e/1/2]: ").strip()
                if laser in {"e", "1", "2"}:
                    break
                print("Invalid laser.")
            # read scope measurement in mV
            while True:
                try:
                    V_scope_mV = float(input("Scope reading [mV]: "))
                    break
                except ValueError:
                    print("Invalid number.")
            P_mW = calc_P(setup_description, laser, V_scope_mV)
            print_result(laser, P_mW)
    else:
        laser = args.laser
        V_scope_mV = args.V_scope_mV
        P_mW = calc_P(setup_description, laser, V_scope_mV)
        print_result(laser, P_mW)



