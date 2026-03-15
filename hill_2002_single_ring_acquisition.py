import numpy as np
import matplotlib.pyplot as plt
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
    """
    Setup description for Single Ring setup.
    This class stores the hardware component information
    for the single ring setup used to replicate Hill 2002 results.
    Attributes:
        coupler (str): Serial number and part number identifier for the optical coupler.
        tbf (str): Serial number and part number identifier for the tunable bandpass filter.
        tbf_bw_nm (float): Bandwidth of the tunable bandpass filter in nanometers. Defaults to 1.
        tap1 (str): Serial number and part number identifier for optical tap 1.
        tap2 (str): Serial number and part number identifier for optical tap 2.
        polarization_splitter (str): Serial number and part number identifier for the polarization splitter.
        soa (str): Serial number and part number identifier for the semiconductor optical amplifier.
        ext_laser (str): Serial number and part number identifier for the external laser source.
        ext_laser_lambda_min_nm(float): Minimum wavelength of the external laser spectrum (used to calculate its power from osa measurement)
        ext_laser_lambda_max_nm(float): Maximum wavelength of the external laser spectrum (used to calculate its power from osa measurement)
        PC1 (str): Serial number and part number identifier for polarization controller 1.
        PC2 (str): Serial number and part number identifier for polarization controller 2.
    """
    # Fixed setup parameters
    name: str = "Hill2002"
    coupler: str = "SN:XXXX-PN:XXXX"
    tbf: str = "SN:XXXX-PN:XXXX"
    tbf_bw_nm: float = 1
    tap1: str = "SN:XXXX-PN:XXXX"
    tap2: str = "SN:XXXX-PN:XXXX"
    polarization_splitter : str = "SN:XXXX-PN:XXXX"
    soa : str = "SN:XXXX-PN:XXXX"
    ext_laser : str = "SN:XXXX-PN:XXXX"
    ext_laser_lambda_min_nm : float = 1553.0
    ext_laser_lambda_max_nm : float = 1560.0
    PC1 : str = "SN:XXXX-PN:XXXX"
    PC2 : str = "SN:XXXX-PN:XXXX"

@dataclass(frozen=True)
class SetupConfig:
    """
    Setup configurations for Single Ring setup.
    This class stores the configurations of the single ring setup used to replicate 
    Hill 2002 results.
    Attributes:

        coupler_position (float): Physical position of the optical coupler in the setup.
        tbf_lambda_nm (float): Wavelength tuned in the tunable bandpass filter in nm.
        soa_I (float): Input current for the SOA in mA.
        soa_T (float): Temperature setting for the SOA in celsius.
        ext_laser_T (float): The temperature configured for the external laser.
    """
    # Configurable setup parameters
    coupler_position: float
    tbf_lambda_nm: float
    soa_I : float
    soa_T : float
    ext_laser_T : float

@dataclass(frozen=True)
class ExperimentParams:
    """
    Parameters for the external laser current sweep.
    This class stores the definition of the external laser current sweep used to replicate 
    Hill 2002 results (each current in the sweep corresponds to one run)
    Attributes:
        ext_laser_I_min (float): The minimum current configured for the external laser 
            current sweep (inclusive).
        ext_laser_I_max (float): The maximum current configured for the external laser 
            current sweep (inclusive).
        ext_laser_I_steps (int): The number of steps for the sweep (corresponds to number of runs)
    Example:
        ext_laser_I_min = 10.0
        ext_laser_I_max = 30.0
        ext_laser_I_steps = 3
        => There will be 3 runs with the following currents: 10.0 mA, 20.0 mA, and 30.0 mA
    """
    ext_laser_I_min : float
    ext_laser_I_max : float
    ext_laser_I_steps : int

@dataclass(frozen=True)
class SingleRunParams:
    """
    Parameters for a single run of the Hill 2002 single ring model.
    Attributes:
        ext_laser_I (float): The current configured for the external laser.
        T (float): Room temperature
    """
    ext_laser_I : float

@dataclass(frozen=True)
class SingleRunResults:
    """
    Results from a single run of the Hill 2002 single ring laser setup run.
    Attributes:
        run_params (SinglerunParams): Parameters used for the run
        T (float): Room temperature
        ring_laser_power_dBm (float): The optical power output from the ring laser in dBm
            (including only power in the configured tbf range, which should not overlap with 
            the configured external laser range).
        ext_laser_power_dBm (float): The optical power from the external laser in dBm 
            (measured inside the ring, after SOA and before TBF, and including only power in 
            the external laser range, which should not overlap with the tbf range).
        ext_laser_polarization_power_loss (float): The optical power measured at the
            polarization splitter output terminal that is not fed into the ring laser.
        spectrum_fig (Figure): Matplotlib Figure object containing the spectrum visualization.
        spectrum_raw (dict[str, np.ndarray]): Dictionary containing raw spectrum data.
    """
    run_params: SingleRunParams
    T : float   # todo, poner en otro lado, aca queda medio colgado
    ring_laser_power_dBm : float
    ext_laser_power_dBm : float
    ext_laser_polarization_power_loss : float
    spectrum_fig : Figure
    spectrum_raw : dict[str, np.ndarray]

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
            "ext_laser_I_mA",
            "ring_laser_power_dBm",
            "ext_laser_power_dBm",
            "ext_laser_polarization_power_loss_dBm",
        ])

        for r in results:
            writer.writerow([
                r.run_params.ext_laser_I,
                r.ring_laser_power_dBm,
                r.ext_laser_power_dBm,
                r.ext_laser_polarization_power_loss,
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
        exper_name: str = "hill2002_single_ring",
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
                    "ring_laser_power_dBm", 
                    result.ring_laser_power_dBm
                )
                mlflow.log_metric(
                    "ext_laser_power_dBm", 
                    result.ext_laser_power_dBm
                )
                mlflow.log_metric(
                    "ext_laser_polarization_power_loss",
                    result.ext_laser_polarization_power_loss
                )

                # ---- spectrum artifacts ----
                mlflow.log_artifacts(outputdir/ str(result.run_params) / "artifacts")


def single_run(
        setup_description: SetupDescription, 
        setup_config: SetupConfig, 
        run_params :  SingleRunParams,
        osa_endpoint : tuple[str, int]
    ):

    manual_steps.give_instruction(f"Configure external laser current at {run_params.ext_laser_I} mA")
    T = manual_steps.ask_for_input("Enter room temperature (Celsius)")
    if not T:
        print("Error: could not read input for room temperature. Quitting...")
        exit()
    manual_steps.give_instruction(f"Adjust ring laser polarization controller to reduce ring laser bandwidth")
    manual_steps.give_instruction(f"Adjust external laser polarization controller to minimize power meter 1 measurement")
    pm1_meas = manual_steps.ask_for_input("Enter power meter 1 measurement (dBm)")
    if not pm1_meas:
        print("Error: could not read input for pm1 value. Quitting...")
        exit()

    print("Acquiring spectrum...")
    meas = osa.acquire_spectrum(ip=osa_endpoint[0], port=osa_endpoint[1])
    #meas = osa.load_spectrum("dummy_spectrum.csv")  #debug only
    print("Spectrum acquisition done!")

    ext_laser_lambda_range = [
        setup_description.ext_laser_lambda_min_nm, 
        setup_description.ext_laser_lambda_max_nm,
    ]
    ring_laser_lambda_range = [
        setup_config.tbf_lambda_nm - setup_description.tbf_bw_nm,
        setup_config.tbf_lambda_nm + setup_description.tbf_bw_nm,
    ]
    ext_laser_power = osa.get_spectrum_power(meas['lambda_nm'], meas['power_dB'], *ext_laser_lambda_range)
    ring_laser_power = osa.get_spectrum_power(meas['lambda_nm'], meas['power_dB'], *ring_laser_lambda_range)
    spectrum_fig = osa.plot_spectrum(
        meas["lambda_nm"],
        meas["power_dB"],
        show=False,
        lambda_min = min(ext_laser_lambda_range[0], ring_laser_lambda_range[0]) - 1, 
        lambda_max = max(ext_laser_lambda_range[1], ring_laser_lambda_range[1]) + 1, 
    )

    results = SingleRunResults(run_params, T, ring_laser_power, ext_laser_power, pm1_meas, spectrum_fig, meas)
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