import numpy as np
import manual_steps
from matplotlib.figure import Figure
import osa.viavi as osa
from dataclasses import dataclass, asdict
import tomllib
import tomli_w
from pathlib import Path
import argparse
import csv
from datetime import datetime

@dataclass(frozen=True)
class SetupDescription:
    # Fixed setup parameters
    name: str = "Hill2002TwoRingsB"

    ext_laser : str = "SN:XXXX-PN:XXXX"
    ext_laser_lambda_min_nm : float = 1553.0
    ext_laser_lambda_max_nm : float = 1560.0
    mzm : str = "SN:XXXX-PN:XXXX"
    PC_3 : str = "SN:XXXX-PN:XXXX"
    polarizing_beamsplitter : str = "SN:XXXX-PN:XXXX"
    tap_0 : str = "SN:XXXX-PN:XXXX"
    tap_0_loss_dB : float = np.nan
    PM_0 : str = "SN:XXXX-PN:XXXX"
    coupler_1: str = "SN:XXXX-PN:XXXX"
    coupler_1_T_dB: float = np.nan

    attenuator_1: str = "SN:XXXX-PN:XXXX"
    attenuator_1_att_dB: float = np.nan
    soa_1 : str = "SN:XXXX-PN:XXXX"
    PC_1 : str = "SN:XXXX-PN:XXXX"
    tbf_1: str = "SN:XXXX-PN:XXXX"
    tbf_1_bw_nm: float = 1
    tap_1: str = "SN:XXXX-PN:XXXX"
    tap_1_loss_dB: float = np.nan
    PD_1: str = "SN:XXXX-PN:XXXX"
    PD_1_resp: float = 1.0  # A/W

    soa_2 : str = "SN:XXXX-PN:XXXX"
    PC_2 : str = "SN:XXXX-PN:XXXX"
    tbf_2: str = "SN:XXXX-PN:XXXX"
    tbf_2_bw_nm: float = 1
    tap_2: str = "SN:XXXX-PN:XXXX"
    tap_2_loss_dB: float = np.nan
    PD_2: str = "SN:XXXX-PN:XXXX"

    tap_3: str = "SN:XXXX-PN:XXXX"
    tap_3_loss_dB: float = np.nan
    coupler_2: str = "SN:XXXX-PN:XXXX"
    coupler_2_T_1_dB: float = np.nan
    coupler_2_T_2_dB: float = np.nan


@dataclass(frozen=True)
class SetupConfig:
    # Configurable setup parameters
    tbf_1_lambda_nm: float
    tbf_2_lambda_nm: float
    soa_1_I : float
    soa_2_I : float
    soa_T : float
    attenuator_1: str = "SN:XXXX-PN:XXXX"
    attenuator_1_att_dB: float = np.nan
    attenuator_2: str = "SN:XXXX-PN:XXXX"
    attenuator_2_att_dB: float = np.nan
    ext_laser_T : float

@dataclass(frozen=True)
class ExperimentParams:
    mzm_v_min: float
    mcm_v_max: float
    mcm_v_steps: float

@dataclass(frozen=True)
class SingleRunParams:
    mzm_v : float

@dataclass(frozen=True)
class SingleRunResults:
    run_params: SingleRunParams
    T : float   # todo, poner en otro lado, aca queda medio colgado
    ring_laser_1_power_dBm_from_osa : float
    ring_laser_2_power_dBm_from_osa : float
    ext_laser_power_dBm_from_osa : float
    ring_laser_1_power_dBm_from_scope : float
    ring_laser_2_power_dBm_from_scope : float
    ext_laser_power_dBm_from_scope : float
    ext_laser_polarization_power_loss : float
    spectrum_fig : Figure
    spectrum_raw : dict[str, np.ndarray]
    scope_fig : Figure
    scope_raw : dict[str, np.ndarray]

def parse_setup_description_toml(
        setup_description_path: str,
    ) -> SetupDescription:

    """Load setup description from TOML file."""
    
    with open(Path(setup_description_path), "rb") as f:
        toml_data = tomllib.load(f)
        setup_description = toml_data["SetupDescription"]

    return SetupDescription(**setup_description)

def parse_setup_config_toml(
        setup_config_path: str,
    ) -> SetupConfig:

    """Load setup config from TOML file."""
    
    with open(Path(setup_config_path), "rb") as f:
        toml_data = tomllib.load(f)
        setup_config = toml_data["SetupConfig"]

    return SetupConfig(**setup_config)

def parse_experiment_params_toml(
        exper_params_path: str,
    ) -> ExperimentParams:

    """Load experiment parameters from TOML file."""
    
    with open(Path(exper_params_path), "rb") as f:
        toml_data = tomllib.load(f)
        exper_params = toml_data["ExperimentParams"]

    return ExperimentParams(**exper_params)

def save_result_metrics_csv(
        results: list[SingleRunResults],
        path: Path | str
    ):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    csvpath = path / "results.csv"
    with csvpath.open("w", newline="") as f:
        writer = csv.writer(f)

        # header
        writer.writerow([
            "mzm_v",
            "ring_laser_1_power_dBm_from_osa",
            "ring_laser_2_power_dBm_from_osa",
            "ext_laser_power_dBm_from_osa",
            "ring_laser_1_power_dBm_from_scope",
            "ring_laser_2_power_dBm_from_scope",
            "ext_laser_power_dBm_from_scope",
            "ext_laser_polarization_power_loss_dBm",
            "T"
        ])

        for r in results:
            writer.writerow([
                r.run_params.mzm_v,
                r.ring_laser_1_power_dBm,
                r.ring_laser_2_power_dBm,
                r.ext_laser_power_dBm,
                r.ext_laser_polarization_power_loss,
                r.T,
            ])

def save_result_metrics_npz(
        results: list[SingleRunResults],
        path: Path | str
    ):

    print("TODO: implement saving metrics in .npz")

def save_setup_and_experiment_conditions_toml(
        setup_description: SetupDescription, 
        setup_config: SetupConfig, 
        exper_params: ExperimentParams,
        path: Path | str,
    ):
    conditions = {}

    for c in (setup_description, setup_config, exper_params):
        name  = c.__class__.__name__   # TODO: feo, sacar de otro lado mejor el nombre de la tabla de toml
        conditions[name] = asdict(c)
    
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    tomlpath = path / "conditions.toml"
    with tomlpath.open("wb") as f:
        tomli_w.dump(conditions, f)

def save_artifacts(
        results: list[SingleRunResults],
        path: Path | str,
    ):
    path = Path(path) 
    for result in results:
        dir_path = path / str(result.run_params) / "artifacts"
        dir_path.mkdir(parents=True, exist_ok=True)
        result.spectrum_fig.savefig(dir_path / "spectrum.svg")
        np.savez(dir_path / "spectrum.npz", **result.spectrum_raw)
        result.scope_fig.savefig(dir_path / "scope.svg")
        np.savez(dir_path / "scope.npz", **result.scope_raw)

def save_result(
        setup_description: SetupDescription, 
        setup_config: SetupConfig, 
        exper_params: ExperimentParams,
        results: list[SingleRunResults],
        path: Path | str
    ):

    save_result_metrics_csv(results, path)
    save_result_metrics_npz(results, path)
    save_setup_and_experiment_conditions_toml(setup_description, setup_config, exper_params, path)
    save_artifacts(results, path)

def log_to_mlflow(
        outputdir: Path,
        setup_description: SetupDescription, 
        setup_config: SetupConfig, 
        exper_params : ExperimentParams,
        results: list[SingleRunResults],
        exper_name: str = "hill2002_two_rings",
    ):
    import mlflow

    mlflow.set_tracking_uri("http://127.0.0.1:5000")    #todo: receive from cli
    mlflow.set_experiment(exper_name)

    with mlflow.start_run(run_name=str(exper_params)):    # todo: improve run name
        mlflow.log_params(asdict(setup_description))
        mlflow.log_params(asdict(setup_config))
        mlflow.log_params(asdict(exper_params))

        for result in results:
            with mlflow.start_run(run_name=str(result.run_params), nested=True):

                # ---- parameters ----
                mlflow.log_params(asdict(result.run_params))
                
                # ---- metrics ----
                mlflow.log_metric(
                    "ring_laser_1_power_dBm_from_osa", 
                    result.ring_laser_1_power_dBm_from_osa
                )
                mlflow.log_metric(
                    "ring_laser_2_power_dBm_from_osa", 
                    result.ring_laser_2_power_dBm_from_osa
                )
                mlflow.log_metric(
                    "ext_laser_power_dBm_from_osa", 
                    result.ext_laser_power_dBm_from_osa
                )
                mlflow.log_metric(
                    "ring_laser_1_power_dBm_from_scope", 
                    result.ring_laser_1_power_dBm_from_scope
                )
                mlflow.log_metric(
                    "ring_laser_2_power_dBm_from_scope", 
                    result.ring_laser_2_power_dBm_from_scope
                )
                mlflow.log_metric(
                    "ext_laser_power_dBm_from_scope", 
                    result.ext_laser_power_dBm_from_scope
                )
                mlflow.log_metric(
                    "ext_laser_polarization_power_loss",
                    result.ext_laser_polarization_power_loss
                )
                mlflow.log_metric(
                    "T",
                    result.T
                )

                # ---- OSA and scope artifacts ----
                mlflow.log_artifacts(outputdir/ str(result.run_params) / "artifacts")


def single_run(
        setup_description: SetupDescription, 
        setup_config: SetupConfig, 
        run_params :  SingleRunParams,
        osa_endpoint : tuple[str, int]
    ):

    manual_steps.give_instruction(f"Configure modulator voltage at {run_params.mzm_v} V")
    T = manual_steps.ask_for_input("Enter room temperature (Celsius)")
    if not T:
        print("Error: could not read input for room temperature. Quitting...")
        exit()
    manual_steps.give_instruction(f"Adjust ring laser 1 polarization controller (PC 1) to reduce ring laser bandwidth")
    manual_steps.give_instruction(f"Adjust ring laser 2 polarization controller (PC 2) to reduce ring laser bandwidth")
    manual_steps.give_instruction(f"Adjust external laser polarization controller (PC 3) to minimize power meter 0  (PM 0) reading")
    pm0_meas = manual_steps.ask_for_input("Enter power meter 0 (PM 0) reading (dBm)")
    if not pm0_meas:
        print("Error: could not read input for PM 0 value. Quitting...")
        exit()

    # OSA
    print("Acquiring spectrum...")
    meas = osa.acquire_spectrum(ip=osa_endpoint[0], port=osa_endpoint[1])
    #meas = osa.load_spectrum("dummy_spectrum.csv")  #debug only
    print("Spectrum acquisition done!")

    ext_laser_lambda_range = [
        setup_description.ext_laser_lambda_min_nm, 
        setup_description.ext_laser_lambda_max_nm,
    ]
    ring_laser_1_lambda_range = [
        setup_config.tbf_1_lambda_nm - setup_description.tbf_1_bw_nm,
        setup_config.tbf_1_lambda_nm + setup_description.tbf_1_bw_nm,
    ]
    ring_laser_2_lambda_range = [
        setup_config.tbf_2_lambda_nm - setup_description.tbf_2_bw_nm,
        setup_config.tbf_2_lambda_nm + setup_description.tbf_2_bw_nm,
    ]

    ext_laser_power_from_osa = osa.get_spectrum_power(meas['lambda_nm'], meas['power_dB'], *ext_laser_lambda_range)
    ring_laser_1_power_from_osa = osa.get_spectrum_power(meas['lambda_nm'], meas['power_dB'], *ring_laser_1_lambda_range)
    ring_laser_2_power_from_osa = osa.get_spectrum_power(meas['lambda_nm'], meas['power_dB'], *ring_laser_2_lambda_range)
    spectrum_fig = osa.plot_spectrum(
        meas["lambda_nm"],
        meas["power_dB"],
        show=False,
        lambda_min = np.amin([
            ext_laser_lambda_range[0], 
            ring_laser_1_lambda_range[0],
            ring_laser_2_lambda_range[0],
        ]) - 1, 
        lambda_max = np.max([
            ext_laser_lambda_range[1], 
            ring_laser_1_lambda_range[1],
            ring_laser_2_lambda_range[1],
        ]) + 1, 
    )

    # Scope
    print("Acquiring scope capture...")
    meas_scope = None   #todo: read scope

    print("Scope capture acquisition done!")

    # TODO: repeat for the 3 channels
    v_avg = 4   # TODO: get average channel V from scope measurement
    zin = 50
    i = v_avg / zin
    pow = i / setup_description.PD_1_resp

    ring_laser_1_power_from_scope = -np.inf
    ring_laser_2_power_from_scope = -np.inf
    ext_laser_power_from_scope = -np.inf

    results = SingleRunResults(
        run_params, 
        T, 
        ring_laser_1_power_from_osa,
        ring_laser_2_power_from_osa,
        ext_laser_power_from_osa, 
        ring_laser_1_power_from_scope,
        ring_laser_2_power_from_scope,
        ext_laser_power_from_scope, 
        pm0_meas, 
        spectrum_fig, 
        meas
    )
    return results

def complete_run(
        setup_description: SetupDescription, 
        setup_config: SetupConfig, 
        exper_params : ExperimentParams,
        osa_endpoint: tuple[str, int]
    ) -> list[SingleRunResults]:

    manual_steps.give_instruction(f"Configure coupler at {setup_config.coupler_position} position")
    manual_steps.give_instruction(f"Configure tbf central wavelength at {setup_config.tbf_lambda_nm} nm")
    manual_steps.give_instruction(f"Configure SOA current at {setup_config.soa_I} mA")
    manual_steps.give_instruction(f"Configure SOA temperature control setpoint at {setup_config.soa_T} °C")
    manual_steps.give_instruction(f"Configure external laser temperature control setpoint at {setup_config.ext_laser_T} °C")
    manual_steps.give_instruction(f"Configure external laser current at 0 mA")
    manual_steps.give_instruction(f"Turn on external laser")

    I_max = exper_params.ext_laser_I_max
    I_min = exper_params.ext_laser_I_min
    I_steps = exper_params.ext_laser_I_steps

    results = []
    I_sweep = np.linspace(I_min, I_max, I_steps)
    for I in I_sweep:
        single_run_params = SingleRunParams(I)
        result = single_run(setup_description, setup_config, single_run_params, osa_endpoint)
        results.append(result)

    manual_steps.give_instruction(f"Turn off external laser")

    return results

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--setup-description", 
        default="setup.toml",
        help="Path to TOML file containing the setup description"
    )
    parser.add_argument(
        "--setup-config", 
        default="setup.toml",
        help="Path to TOML file containing the setup configuration"
    )

    parser.add_argument(
        "--experiment-params",
        required=False,
        help="Path to TOML file containing the setup configuration"
    )

    parser.add_argument(
        "--Imin",
        type=float,
        help="Minimum external laser current (overrides value of file specified with --experiment-params)"
    )

    parser.add_argument(
        "--Imax", 
        type=float,
        help="Maximum external laser current (overrides value of file specified with --experiment-params)"
    )

    parser.add_argument(
        "--Isteps", 
        type=int,
        default=10,
        help="Number of points in external laser current sweep (overrides value of file specified with --experiment-params)"
    )

    parser.add_argument(
        "--ip", 
        default="10.0.0.1",
        help='OSA ip',
    )

    parser.add_argument(
        "--port", 
        type=int, 
        default=8003,
        help='OSA port'
    )

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    setup_description = parse_setup_description_toml(args.setup_description)
    setup_config = parse_setup_config_toml(args.setup_config)

    if args.experiment_params:
        experiment_params = parse_experiment_params_toml(args.experiment_params)
        # override file params with cli params (if present):
        newImin = args.Imin if args.Imin else experiment_params.ext_laser_I_min
        newImax = args.Imax if args.Imax else experiment_params.ext_laser_I_max
        newIsteps = args.Isteps if args.Isteps else experiment_params.ext_laser_I_steps
        experiment_params = ExperimentParams(newImin, newImax, newIsteps)
    elif args.Imin and args.Imax and args.Isteps:
        experiment_params = ExperimentParams(args.Imin, args.Imax, args.Isteps)
    else:
        print("Error: missing information on external laser current (Imax, Imin, and Isteps need to be specified).")
        exit()

    osa_endpoint = (args.ip, args.port)

    experiment_results = complete_run(setup_description, setup_config, experiment_params, osa_endpoint)
    
    timestamp = datetime.now().strftime("%Y%m%d%Hh%Mm%Ss")
    outputdir = Path("out/single_ring_laser/" + timestamp)
    save_result(setup_description, setup_config, experiment_params, experiment_results, outputdir)
    log_to_mlflow(outputdir, setup_description, setup_config, experiment_params, experiment_results)


if __name__ == '__main__':
    main()