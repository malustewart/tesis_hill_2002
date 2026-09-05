import numpy as np
import manual_steps
from matplotlib.figure import Figure
# import osa.viavi as osa
from dataclasses import dataclass, asdict, fields, replace
import tomllib
import tomli_w
from pathlib import Path
import argparse
import csv
from datetime import datetime
from scope import scope
import copy

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


@dataclass(frozen=True)
class SetupConfig:
    # Configurable setup parameters
    tbf_0_lambda_nm: float
    tbf_1_lambda_nm: float
    tbf_2_lambda_nm: float
    soa_1_I : float
    soa_2_I : float
    soa_1_T : float
    soa_2_T : float
    ext_laser_I : float
    ext_laser_T : float
    ext_laser_modulator_v_min: float
    ext_laser_modulator_v_max: float
    ext_laser_amplifier_setpoint : str = "First amplifier: 129 mA - Second amplifier: 66 mA"
    attenuator_and_PC_setup_instruction :str = "Configure attenuators to have a transition as close as possible to a step without histeresis"
    scope_ip : str = "10.0.0.10"


@dataclass(frozen=True)
class ExperimentParams:
    scope_capture_ranges: tuple[str] = ("2 periods", "zoom on transition rise/fall time")
    sweep_waveforms: tuple[str] = ("triang", "square", "senoid")
    sweep_times: tuple[str] = ("100us", "1ms", "10ms")


@dataclass(frozen=True)
class SingleRunParams:
    scope_capture_range :str
    sweep_waveform: str
    sweep_time: str


@dataclass(frozen=True)
class SingleRunResults:
    run_params: SingleRunParams
    scope_raw_fig : Figure
    scope_processed_fig_vs_t : Figure
    scope_processed_fig_vs_ext_laser_power : Figure
    scope_processed_no_arrival_time_compensation_fig_vs_t : Figure
    scope_processed_no_arrival_time_compensation_fig_vs_ext_laser_power : Figure
    scope_raw : dict[str, np.ndarray]
    scope_processed: dict[str, np.ndarray]
    scope_processed_no_arrival_time_compensation: dict[str, np.ndarray]
    #TODO: agregar captura de OSa con promediado    # limitacion: no puedo hacer la captura automatica porque solo tengo una salida ethernet en la compu que estoy usando para el scope
    T : float   # temperature #TODO: poner en otro lado, aca queda medio colgado
    T11_dB: float = None
    T12_dB: float = None
    T21_dB: float = None
    T22_dB: float = None


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

    def should_be_saved_to_csv(x):
        TYPES_TO_SAVE = (int, float, bool, str, np.number)
        return isinstance(x, TYPES_TO_SAVE)

    def flatten_and_filter_result(result):
        out = {}

        # run_param fields:
        for k, v in vars(result.run_params).items():
            if should_be_saved_to_csv(v):
                out[f"run_params.{k}"] = v
        
        # top-level fields:
        for k, v in vars(result).items():
            if should_be_saved_to_csv(v):
                out[k] = v

        return out

    results = [flatten_and_filter_result(r) for r in results]

    with csvpath.open("w", newline="") as f:
        writer = csv.writer(f)

        # header
        headers = [k for k in results[0]]
        writer.writerow(headers)

        # result data
        for r in results:
            row = [r[header] for header in headers]
            writer.writerow(row)


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

    def save_array_dicts(result: SingleRunResults, path: Path | str):
        path = Path(path)
        # arrays = {}

        for field in fields(result):
            value = getattr(result, field.name)

            # Solo guarda los elementos de SingleRunResults que son de tipo dict[str, np.ndarray]
            if isinstance(value, dict) and all(
                isinstance(k, str) and isinstance(v, np.ndarray) for k,v in value.items()
            ):
                # for key, array in value.items():
                #     arrays[f"{field.name}.{key}"] = array
                np.savez(path/f"{field.name}.npz", **value)

    def save_figs(result: SingleRunResults, path: Path | str):
        path = Path(path)
        
        for field in fields(result):
            value = getattr(result, field.name)

            # Solo guarda los elementos de SingleRunResults que son de tipo Figures
            if isinstance(value, Figure):
                
                value.savefig(dir_path / (field.name + ".svg"))

    path = Path(path) 
    for result in results:
        dir_path = path / str(result.run_params) / "artifacts" # TODO: mejor nombre para el single run
        dir_path.mkdir(parents=True, exist_ok=True)
        save_array_dicts(result, dir_path/"")
        save_figs(result, dir_path/"")


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
    ) -> SingleRunResults:
    manual_steps.give_instruction(f"Configure waveform generator output shape to {run_params.sweep_waveform}")
    manual_steps.give_instruction(f"Configure waveform generator output period to {run_params.sweep_time}")
    # Scope
    manual_steps.give_instruction(f"Scope config: If display XY is ON, turn OFF")
    manual_steps.give_instruction(f"Scope config: Show CH1, CH2, and CH3")
    manual_steps.give_instruction(f"Scope config: Adjust vertical scale of CH1, CH2, and CH3 to avoid clipping signals")
    manual_steps.give_instruction(f"Scope config: Adjust horizontal scale to show {run_params.scope_capture_range}")
    manual_steps.give_instruction(f"Press enter to acquire signals with scope")

    print("Acquiring scope capture...")
    scope_id = scope.get_scope_id_ethernet(setup_config.scope_ip)
    try:
        scope_raw = scope.acquire_signal(
            scope_id,
            ["CH1", "CH2", "CH3"],
        )
    except Exception as e:
        print(f"Scope acquisition failed: {e}")
        return None

    print("Scope capture acquisition done!")

    T_string = manual_steps.ask_for_input("Enter temperature in Celsius: ").replace(",", ".")
    try:
        T = float(T_string)
    except ValueError:
        T = -273.15
        print(f"Couldn't parse temperature. Recording default value T={T:.2f}")


    def compensate_arrival_time_diff(
            scope_measurement : dict,
            setup_description : SetupDescription,
        ):
        t = scope_measurement['t']
        CH1 = scope_measurement['CH1']
        CH2 = scope_measurement['CH2']
        CH3 = scope_measurement['CH3']
        meas_arrival_time_diff_scope_ch1_to_ch2_ns = setup_description.meas_arrival_time_diff_scope_ch1_to_ch2_ns
        meas_arrival_time_diff_scope_ch1_to_ch3_ns = setup_description.meas_arrival_time_diff_scope_ch1_to_ch2_ns + meas_arrival_time_diff_scope_ch1_to_ch2_ns

        time_step_ns = (t[-1] - t[0]) / (len(t) - 1) * 1e9

        arrival_time_diff_scope_ch1_to_ch2_in_samples = round(meas_arrival_time_diff_scope_ch1_to_ch2_ns / time_step_ns)
        arrival_time_diff_scope_ch1_to_ch3_in_samples = round(meas_arrival_time_diff_scope_ch1_to_ch3_ns / time_step_ns)

        CH2 = np.roll(CH2, -arrival_time_diff_scope_ch1_to_ch2_in_samples)
        CH3 = np.roll(CH3, -arrival_time_diff_scope_ch1_to_ch3_in_samples)

        new_length = t.size - arrival_time_diff_scope_ch1_to_ch3_in_samples

        scope_measurement["t"] = t[:new_length]
        scope_measurement["CH1"] = CH1[:new_length]
        scope_measurement["CH2"] = CH2[:new_length]
        scope_measurement["CH3"] = CH3[:new_length]

        return scope_measurement


    def convert_measured_V_to_optical_power(
        scope_measurement : dict,
        setup_description : SetupDescription
        ):

        # measured currents (mA)
        meas_current_ch1 = scope_measurement['CH1'] / setup_description.scope_impedance_ch1_ohm * 1000
        meas_current_ch2 = scope_measurement['CH2'] / setup_description.scope_impedance_ch2_ohm * 1000
        meas_current_ch3 = scope_measurement['CH3'] / setup_description.scope_impedance_ch3_ohm * 1000

        # optical powers arriving at PD (mW)
        meas_power_ch1 = meas_current_ch1 / setup_description.PD_0_resp
        meas_power_ch2 = meas_current_ch2 / setup_description.PD_1_resp
        meas_power_ch3 = meas_current_ch3 / setup_description.PD_2_resp

        # optical powers arriving at PD (dBm)

        ## avoid division by zero
        meas_power_ch1 = np.abs(meas_power_ch1) + 1e-30
        meas_power_ch2 = np.abs(meas_power_ch2) + 1e-30
        meas_power_ch3 = np.abs(meas_power_ch3) + 1e-30

        ## calc dBm
        meas_power_ch1_dBm = 10 * np.log10(meas_power_ch1)
        meas_power_ch2_dBm = 10 * np.log10(meas_power_ch2)
        meas_power_ch3_dBm = 10 * np.log10(meas_power_ch3)

        # real optical powers (dBm)
        real_power_ext_laser_dBm = (
            meas_power_ch1_dBm
            + setup_description.tap_0_loss_in_to_out_meas_dB
            - setup_description.tap_0_loss_in_to_out_pass_dB
            + setup_description.coupler_1_T_from_ext_laser_dB
            - setup_description.tap_3_loss_in_to_out_pass_dB
        )

        real_power_ring_laser_1_dBm = (
            meas_power_ch2_dBm
            + setup_description.tap_1_loss_in_to_out_meas_dB
            - setup_description.tap_1_loss_in_to_out_pass_dB
        )

        real_power_ring_laser_2_dBm = (
            meas_power_ch3_dBm
            + setup_description.tap_2_loss_in_to_out_meas_dB
            - setup_description.tap_2_loss_in_to_out_pass_dB
        )

        # real optical powers (mW)
        real_power_ext_laser = np.pow(10, real_power_ext_laser_dBm / 10)
        real_power_ring_laser_1 = np.pow(10, real_power_ring_laser_1_dBm / 10)
        real_power_ring_laser_2 = np.pow(10, real_power_ring_laser_2_dBm / 10)

        scope_measurement["ext_laser_mW"] = real_power_ext_laser
        scope_measurement["ring_laser_1_mW"] = real_power_ring_laser_1
        scope_measurement["ring_laser_2_mW"] = real_power_ring_laser_2

        scope_measurement.pop("CH1")
        scope_measurement.pop("CH2")
        scope_measurement.pop("CH3")

        return scope_measurement

    # Raw capture
    scope_raw_fig = scope.plot_signal(scope_raw, show=False)

    # Processed capture with arrival time compensation
    scope_processed = copy.deepcopy(scope_raw) 
    compensate_arrival_time_diff(scope_processed, setup_description)
    convert_measured_V_to_optical_power(scope_processed, setup_description)

    scope_processed_fig_vs_t = scope.plot_signal(
        scope_processed, 
        show=False,
        labels={"ring_laser_1_mW": "Ring laser 1", "ring_laser_2_mW": "Ring laser 2", "ext_laser_power": "Ext. laser power"},
        ylabel="Power [mW]"
    )
    scope_processed_fig_vs_ext_laser_power = scope.plot_signal(
        scope_processed, 
        show=False, 
        x_axis="ext_laser_mW", 
        y_axis = ["ring_laser_1_mW", "ring_laser_2_mW"], 
        xlabel="Ext. laser power [mW]",
        ylabel="Ring laser power [mW]", 
        labels={"ring_laser_1_mW": "Ring laser 1", "ring_laser_2_mW": "Ring laser 2"},
    )

    # Processed capture with no arrival time compensation
    scope_processed_no_arrival_time_compensation = copy.deepcopy(scope_raw) 
    convert_measured_V_to_optical_power(scope_processed_no_arrival_time_compensation, setup_description)

    scope_processed_no_arrival_time_compensation_fig_vs_t = scope.plot_signal(
        scope_processed_no_arrival_time_compensation, 
        show=False,
        labels={"ring_laser_1_mW": "Ring laser 1", "ring_laser_2_mW": "Ring laser 2", "ext_laser_power": "Ext. laser power"},
        ylabel="Power [mW]"
    )
    scope_processed_no_arrival_time_compensation_fig_vs_ext_laser_power = scope.plot_signal(
        scope_processed_no_arrival_time_compensation, 
        show=False, 
        x_axis="ext_laser_mW", 
        y_axis = ["ring_laser_1_mW", "ring_laser_2_mW"], 
        xlabel="Ext. laser power [mW]",
        ylabel="Ring laser power [mW]", 
        labels={"ring_laser_1_mW": "Ring laser 1", "ring_laser_2_mW": "Ring laser 2"},
    )

    results = SingleRunResults(
        run_params=run_params, 
        T=T,
        scope_raw_fig=scope_raw_fig,
        scope_processed_fig_vs_t = scope_processed_fig_vs_t,
        scope_processed_fig_vs_ext_laser_power = scope_processed_fig_vs_ext_laser_power,
        scope_processed_no_arrival_time_compensation_fig_vs_t = scope_processed_no_arrival_time_compensation_fig_vs_t,
        scope_processed_no_arrival_time_compensation_fig_vs_ext_laser_power = scope_processed_no_arrival_time_compensation_fig_vs_ext_laser_power,
        scope_raw=scope_raw,
        scope_processed=scope_processed,
        scope_processed_no_arrival_time_compensation=scope_processed_no_arrival_time_compensation,
    )
    return results


def complete_run(
        setup_description: SetupDescription, 
        setup_config: SetupConfig, 
        exper_params : ExperimentParams,
    ) -> list[SingleRunResults]:

    manual_steps.give_instruction(f"If ON, turn OFF all lasers")
    manual_steps.give_instruction(f"If ON, turn OFF external laser modulator controller")

    manual_steps.give_instruction(f"Configure SOA 1 current to {setup_config.soa_1_I:.1f} mA")
    manual_steps.give_instruction(f"Configure SOA 1 temperature to {setup_config.soa_1_T:.1f} C")
    manual_steps.give_instruction(f"Configure SOA 2 current to {setup_config.soa_2_I:.1f} mA")
    manual_steps.give_instruction(f"Configure SOA 2 temperature to {setup_config.soa_2_T:.1f} C")
    manual_steps.give_instruction(f"Configure external laser current to {setup_config.ext_laser_I:.0f} mA")
    manual_steps.give_instruction(f"Configure external laser temperature to {setup_config.ext_laser_T:.0f} C")

    manual_steps.give_instruction(f"Turn ON external laser")
    manual_steps.give_instruction(f"Configure tbf0 to {setup_config.tbf_0_lambda_nm:.1f} nm")
    manual_steps.give_instruction(f"Turn OFF external laser ")

    manual_steps.give_instruction(f"Turn ON SOA 1")
    manual_steps.give_instruction(f"Configure tbf1 to {setup_config.tbf_1_lambda_nm:.1f} nm")
    manual_steps.give_instruction(f"Turn OFF SOA 1")
    
    manual_steps.give_instruction(f"Turn ON SOA 2")
    manual_steps.give_instruction(f"Configure tbf2 to {setup_config.tbf_2_lambda_nm:.1f} nm")
    manual_steps.give_instruction(f"Turn OFF SOA 2")

    manual_steps.give_instruction(f"Configure external laser modulator controller (AWG) load to match external laser modulator input impedance")
    manual_steps.give_instruction(f"Configure external laser modulator controller (AWG) to output a signal between {setup_config.ext_laser_modulator_v_min:.1f} V and  {setup_config.ext_laser_modulator_v_max:.1f} V")
    manual_steps.give_instruction(f"Configure external laser amplifier currents to {setup_config.ext_laser_amplifier_setpoint}")

    manual_steps.give_instruction(setup_config.attenuator_and_PC_setup_instruction)

    # manual_steps.give_instruction(f"Turn ON SOA 1")
    # manual_steps.give_instruction(f"Configure PC 1 to maximise power in ring laser 1")
    # manual_steps.give_instruction(f"Turn OFF SOA 1")
    
    # manual_steps.give_instruction(f"Turn ON SOA 2")
    # manual_steps.give_instruction(f"Configure PC 2 to maximise power in ring laser 2")
    # manual_steps.give_instruction(f"Turn OFF SOA 2")

    manual_steps.give_instruction(f"If OFF, turn ON all lasers")
    manual_steps.give_instruction(f"If OFF, turn ON external laser modulator controller")

    results = []

    for scope_capture_range in exper_params.scope_capture_ranges:
        for sweep_waveform in exper_params.sweep_waveforms:
            for sweep_time in exper_params.sweep_times:
                single_run_params = SingleRunParams(scope_capture_range, sweep_waveform, sweep_time)
                result = single_run(setup_description, setup_config, single_run_params)
                if result:
                    results.append(result)

    def parse_T_db_input(input_str : str) -> float:
        input_str = input_str.lower().replace("dbm", "").replace("db", "").replace("-","").replace(",", ".").strip()
        return -1 * float(input_str)

    T11_dB_str = manual_steps.ask_for_input(f"Measure T11 and enter its value in dB: ")
    T12_dB_str = manual_steps.ask_for_input(f"Measure T12 and enter its value in dB: ")
    T21_dB_str = manual_steps.ask_for_input(f"Measure T21 and enter its value in dB: ")
    T22_dB_str = manual_steps.ask_for_input(f"Measure T22 and enter its value in dB: ")

    T11_dB = parse_T_db_input(T11_dB_str)
    T12_dB = parse_T_db_input(T12_dB_str)
    T21_dB = parse_T_db_input(T21_dB_str)
    T22_dB = parse_T_db_input(T22_dB_str)

    results = [
        replace(
            result,
            T11_dB=T11_dB,
            T12_dB=T12_dB,
            T21_dB=T21_dB,
            T22_dB=T22_dB,
        )
        for result in results
    ]

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

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    setup_description = parse_setup_description_toml(args.setup_description)
    setup_config = parse_setup_config_toml(args.setup_config)
    experiment_params = parse_experiment_params_toml(args.experiment_params)

    experiment_results = complete_run(setup_description, setup_config, experiment_params)
    
    timestamp = datetime.now().strftime("%Y%m%d%Hh%Mm%Ss")
    outputdir = Path("out/2026_agosto/final/" + timestamp)
    save_result(setup_description, setup_config, experiment_params, experiment_results, outputdir)
    # log_to_mlflow(outputdir, setup_description, setup_config, experiment_params, experiment_results)


if __name__ == '__main__':
    main()