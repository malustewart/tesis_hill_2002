from ext_laser.laser import ExtLaser
import argparse
from pathlib import Path
import tomllib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_run_results(rundir: Path, laser: ExtLaser):
    with open(rundir / "conditions.toml", "rb") as f:
        toml_data = tomllib.load(f)
        T = toml_data["SetupConfig"]["ext_laser_T"]
        setup_configs = toml_data["SetupConfig"]
    if T not in laser.temps:
        print(f"Error! laser power not measured for {T} degrees C.")

    df = pd.read_csv(rundir / "results.csv")
    ext_laser_I_mA = df["ext_laser_I_mA"].to_list()

    ring_laser_power_mW = np.pow(10, df["ring_laser_power_dBm"].values / 10.0)
    ext_laser_power_mW_in_ring = [np.pow(10, PdBm / 10.0) for PdBm in df["ext_laser_power_dBm"].values]

    I_to_power_fn = {
        20: laser.power_mW_T_20,
        25: laser.power_mW_T_25,
        30: laser.power_mW_T_30,
    }[T]

    ext_laser_power_mW = [I_to_power_fn(i) for i in ext_laser_I_mA]
    return ring_laser_power_mW, ext_laser_power_mW_in_ring, ext_laser_power_mW, setup_configs

def plot_run_results(
        ring_laser_power_mW: list, 
        ext_laser_power_mW_in_ring: list,
        ext_laser_power_mW: list,
        tap_1_att_dB: float,
        params: dict[str]
    ):

    tap_1_att = np.pow(10, tap_1_att_dB/10)

    conditions = ' - '.join([f"{k}: {v}" for k,v in params.items()])
    
    plt.figure()
    plt.plot(ext_laser_power_mW, ring_laser_power_mW/tap_1_att)
    plt.xlabel("External laser power (mW)")
    plt.ylabel("Ring laser power (mW)")
    plt.ylim(bottom=0)
    plt.grid(True, 'both')
    plt.suptitle("Ring laser power vs. External laser power")
    plt.title(conditions, fontsize=8)
    plt.tight_layout()
    plt.savefig(rundir / "ring_laser_vs_ext_laser_power.svg")

    plt.figure()
    plt.plot(ext_laser_power_mW, ext_laser_power_mW_in_ring/tap_1_att)
    plt.xlabel("External laser power (mW)")
    plt.ylabel("External laser power in ring (mW)")
    plt.ylim(bottom=0)
    plt.grid(True, 'both')
    plt.suptitle("External laser power in ring vs. External laser power")
    plt.title(conditions, fontsize=8)
    plt.savefig(rundir / "ext_laser_in_ring_vs_ext_laser_power.svg")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", 
                        type=Path, 
                        default=Path("out/single_ring_laser"),
                        help="Path to directory where results are stored")
    parser.add_argument("--laser-calib", 
                        type=Path, 
                        required=True,
                        help="Path of laser calibration file")

    return parser

if __name__ == "__main__":
    args = build_parser().parse_args()

    if not args.outdir.is_dir():
        print("Error: outdir argument is not a directory.")
        exit()
    
    root = args.outdir
    laser_calib = args.laser_calib

    laser = ExtLaser(laser_calib)

    for rundir in root.iterdir():
        ring_laser_power_mW, ext_laser_power_mW_in_ring, ext_laser_power_mW, configs = get_run_results(rundir, laser)
        plot_run_results(ring_laser_power_mW, ext_laser_power_mW_in_ring, ext_laser_power_mW, -19.91, configs)    # tap 1 attenuation is hardcoded, improve
