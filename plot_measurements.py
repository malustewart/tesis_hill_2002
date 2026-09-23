from pathlib import Path
import numpy as np
from scope import scope
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba, to_rgb
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D
from calc_P_from_V_scope import parse_setup_description_toml, calc_P_ext, calc_P_ring_1, calc_P_ring_2
from calc_T_estimation import T_est_by_Ptot_dB, T_est_by_Ptot_lin, T_est_by_slope_dB, T_est_by_slope_lin, G_dB_vs_Pout_curve_params_1, G_dB_vs_Pout_curve_params_2
from calc_T_estimation import T_tbf_isolator_1 as ring_1_T_tbf_isolator_dB
from calc_T_estimation import T_tbf_isolator_2 as ring_2_T_tbf_isolator_dB

def compensate_arrival_time_diff(
        data : dict,
        ring_1_time_compensation_ns=0,
        ring_2_time_compensation_ns=0,
    ):

    t = data['t']
    ext_laser_mW = data['ext_laser_mW']
    ring_laser_1_mW = data['ring_laser_1_mW']
    ring_laser_2_mW = data['ring_laser_2_mW']

    time_step_ns = (t[-1] - t[0]) / (len(t) - 1) * 1e9

    ring_1_time_compensation_samples = round(ring_1_time_compensation_ns / time_step_ns)
    ring_2_time_compensation_samples = round(ring_2_time_compensation_ns / time_step_ns)

    ring_laser_1_mW = np.roll(ring_laser_1_mW, -ring_1_time_compensation_samples)
    ring_laser_2_mW = np.roll(ring_laser_2_mW, -ring_2_time_compensation_samples)

    new_length = t.size - np.maximum(ring_1_time_compensation_samples, ring_2_time_compensation_samples)

    data["t"] = t[:new_length]
    data["ext_laser_mW"] = ext_laser_mW[:new_length]
    data["ring_laser_1_mW"] = ring_laser_1_mW[:new_length]
    data["ring_laser_2_mW"] = ring_laser_2_mW[:new_length]

    return data


def convert_scope_capture_to_power(data, setup_description):
    data["ext_laser_mW"] = np.array([calc_P_ext(setup_description, V * 1000) for V in data["CH1"]])
    data["ring_laser_1_mW"] = np.array([calc_P_ring_1(setup_description, V * 1000) for V in data["CH2"]])
    data["ring_laser_2_mW"] = np.array([calc_P_ring_2(setup_description, V * 1000) for V in data["CH3"]])
    data.pop("CH1")
    data.pop("CH2")
    data.pop("CH3")
    return data


def compensate_tbf_and_isolator_loss(
        data : dict,
        T_tbf_isolator_dB_ring_1=ring_1_T_tbf_isolator_dB,
        T_tbf_isolator_dB_ring_2=ring_2_T_tbf_isolator_dB,
    ):

    data["ring_laser_1_mW"] = data["ring_laser_1_mW"] / np.pow(10, T_tbf_isolator_dB_ring_1 / 10)
    data["ring_laser_2_mW"] = data["ring_laser_2_mW"] / np.pow(10, T_tbf_isolator_dB_ring_2 / 10)

    return data


def parse_datafile(datafile):
    if isinstance(datafile,(str,Path)):
        return dict(np.load(datafile))
    elif isinstance(datafile, np.lib.npyio.NpzFile):
        return dict(datafile)
    elif isinstance(datafile, dict):
        return datafile
    return None


def plot_1_vs_t(datafile, outfile, show=False, xmin=None, xmax=None, ymin=None, ymax=None, figsize=(3.5, 2.5)):

    data = parse_datafile(datafile)
    data = compensate_tbf_and_isolator_loss(data)

    outfile=Path(outfile)

    for smooth in (True, False):
        if smooth:
            data_to_plot = {
                key: savgol_filter(value, window_length=11, polyorder=2) 
                if key != "t" else value 
                for key, value in data.items()
            }
            final_outfile = outfile.with_stem(outfile.stem + "_smooth")
        else:
            data_to_plot = data
            final_outfile = outfile.with_stem(outfile.stem + "_raw")

        fig, ax = plt.subplots(figsize=figsize)
        fig.set_tight_layout(True)

        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        ring_laser_1_color = colors[0]
        ext_laser_color = colors[2]

        scope.plot_signal(
            data_to_plot,
            y_axis=["ring_laser_1_mW"],
            x_axis="t",
            show=show,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            labels={"ring_laser_1_mW": "Ring laser 1"},
            ylabel="Power [mW]",
            # save_path=final_outfile,
            ax=ax,
            c=ring_laser_1_color,
        )

        scope.plot_signal(
            data_to_plot,
            y_axis=['ext_laser_mW'],
            x_axis="t",
            show=show,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            labels={"ext_laser_mW": "Ext. laser"},
            ylabel="Power [mW]",
            save_path=final_outfile,
            ax=ax,
            c=ext_laser_color,
        )


def plot_2_vs_t(datafile, outfile, show=False, xmin=None, xmax=None, ymin=None, ymax=None, figsize=(3.5,2.5)):

    data = parse_datafile(datafile)

    data = compensate_tbf_and_isolator_loss(data)

    outfile=Path(outfile)

    for smooth in (True, False):
        if smooth:
            data_to_plot = {
                key: savgol_filter(value, window_length=11, polyorder=2) 
                if key != "t" else value 
                for key, value in data.items()
            }
            final_outfile = outfile.with_stem(outfile.stem + "_smooth")
        else:
            data_to_plot = data
            final_outfile = outfile.with_stem(outfile.stem + "_raw")

        fig, ax = plt.subplots(figsize=figsize)
        fig.set_tight_layout(True)
        scope.plot_signal(
            data_to_plot,
            y_axis=["ring_laser_1_mW", "ring_laser_2_mW", 'ext_laser_mW'],
            x_axis="t",
            show=show,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            labels={"ring_laser_1_mW": "Ring laser 1","ring_laser_2_mW": "Ring laser 2", "ext_laser_mW": "Ext. laser"},
            ylabel="Power [mW]",
            save_path=final_outfile,
            ax=ax,
        )


def plot_1_vs_ext(
        datafile, 
        outfile, 
        show=False, 
        xmin=0, 
        xmax=np.inf, 
        ymin=None, 
        ymax=None, 
        label=None, 
        ring_1_time_compensation_ns=0, 
        Ptot_meas=None, 
        linfit_xy_intersect=None, 
        alpha=0.3, 
        figsize=(7,2.5)
    ):

    if not isinstance(datafile, (list, tuple, np.ndarray)):
        datafile = [datafile]

    num_signals = len(datafile)

    # handle missing input
    if not ring_1_time_compensation_ns:
        ring_1_time_compensation_ns = [0] * num_signals

    if not label:
        label = [None] * num_signals

    if not Ptot_meas:
        Ptot_meas = [None] * num_signals

    if not linfit_xy_intersect:
        linfit_xy_intersect = [None] * num_signals

    # if only 1 signal, convert inputs to list
    if not isinstance(ring_1_time_compensation_ns, (list, tuple, np.ndarray)):
        ring_1_time_compensation_ns = [ring_1_time_compensation_ns]

    if not isinstance(label, (list, tuple, np.ndarray)):
        label = [label]

    if not isinstance(Ptot_meas, (list, tuple, np.ndarray)):
        Ptot_meas = [Ptot_meas]

    if not isinstance(linfit_xy_intersect, (list, tuple, np.ndarray)):
        linfit_xy_intersect = [linfit_xy_intersect]

    assert(len(datafile) == len(ring_1_time_compensation_ns))
    assert(len(datafile) == len(label))
    assert(len(datafile) == len(Ptot_meas))
    assert(len(datafile) == len(linfit_xy_intersect))

    data = [ parse_datafile(df) for df in datafile ]
    data = [ compensate_tbf_and_isolator_loss(d)  for d in data ]
    data = [ compensate_arrival_time_diff(d, r_1_t_c, 0) for d, r_1_t_c in zip(data, ring_1_time_compensation_ns) ]

    outfile=Path(outfile)

    for smooth in (True, False):
        fig, ax = plt.subplots(figsize=figsize)
        fig.set_tight_layout(True)

        if smooth:
            data_to_plot = [
                {
                    key: savgol_filter(value, window_length=11, polyorder=2) 
                    if key != "t" else value 
                    for key, value in d.items()
                } 
                for d in data
            ]
            final_outfile = outfile.with_stem(outfile.stem + "_smooth")
        else:
            data_to_plot = data
            final_outfile = outfile.with_stem(outfile.stem + "_raw")

        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        for i, (d, l, Ptot, lf_xy) in enumerate(zip(data_to_plot, label, Ptot_meas, linfit_xy_intersect)):
            label_ring_1 = f"{l}" if l else None
            color = colors[i % len(colors)]
            light_color = tuple(c + (1 - c) * 0.5 for c in to_rgb(color))

            scope.plot_signal(
                d,
                y_axis=["ring_laser_1_mW"],
                x_axis="ext_laser_mW",
                show=False,
                xmin=xmin,
                xmax=xmax,
                ymin=ymin,
                ymax=ymax,
                labels={"ring_laser_1_mW": label_ring_1},
                ylabel="Ring laser 1 power [mW]",
                xlabel="Ext. laser power [mW]",
                # save_path=final_outfile,
                ax=ax,
                scatter=True,
                alpha=alpha,
                s=12,
                marker=".",
                facecolor=color,
            )

            if Ptot:
                ax.scatter(0, Ptot, marker='*', s=150, color=color)

            if lf_xy:
                x_intersect = lf_xy[0]
                y_intersect = lf_xy[1]
                ax.plot([0, x_intersect], [y_intersect, 0], '--', color=light_color)

        if any(Ptot_meas):
            ax.scatter([], [], marker='*', s=150, color='k', label="Measured Ptot1")

        if any(linfit_xy_intersect):
            ax.plot([], [], '--', color='k', label="Linear fit")

        for h in ax.legend().legend_handles:
            if isinstance(h, PathCollection):
                h.set_sizes([100])
                h.set_alpha(1.0)
            elif isinstance(h, Line2D):
                h.set_markersize(10)

        ax.figure.savefig(final_outfile)
    if show:
        plt.show()


def plot_2_vs_ext(datafile, outfile, show=False, xmin=None, xmax=None, ymin=None, ymax=None, label=None, ring_1_time_compensation_ns=0, ring_2_time_compensation_ns=0, alpha=0.3, figsize=(7, 4)):
    if not isinstance(datafile, (list, tuple, np.ndarray)):
        datafile = [datafile]

    num_signals = len(datafile)

    # handle missing input
    if not ring_1_time_compensation_ns:
        ring_1_time_compensation_ns = [0] * num_signals

    if not ring_2_time_compensation_ns:
        ring_2_time_compensation_ns = [0] * num_signals

    if not label:
        label = [None] * num_signals

    # if only 1 signal, convert inputs to list
    if not isinstance(ring_1_time_compensation_ns, (list, tuple, np.ndarray)):
        ring_1_time_compensation_ns = [ring_1_time_compensation_ns]

    if not isinstance(ring_2_time_compensation_ns, (list, tuple, np.ndarray)):
        ring_2_time_compensation_ns = [ring_2_time_compensation_ns]

    if not isinstance(label, (list, tuple, np.ndarray)):
        label = [label]

    # assert datafile, time compensations and labels have matching length

    assert(len(datafile) == len(ring_1_time_compensation_ns))
    assert(len(datafile) == len(ring_2_time_compensation_ns))
    assert(len(datafile) == len(label))

    # plot

    data = [ parse_datafile(df) for df in datafile ]
    data = [ compensate_tbf_and_isolator_loss(d)  for d in data ]
    data = [ compensate_arrival_time_diff(d, r_1_t_c, r_2_t_c) for d, r_1_t_c, r_2_t_c in zip(data, ring_1_time_compensation_ns, ring_2_time_compensation_ns) ]

    outfile=Path(outfile)

    for smooth in (True, False):
        fig, ax = plt.subplots(figsize=figsize)
        fig.set_tight_layout(True)
        if smooth:
            data_to_plot = [
                {
                    key: savgol_filter(value, window_length=11, polyorder=2) 
                    if key != "t" else value 
                    for key, value in d.items()
                } 
                for d in data
            ]
            final_outfile = outfile.with_stem(outfile.stem + "_smooth")
        else:
            data_to_plot = data
            final_outfile = outfile.with_stem(outfile.stem + "_raw")

        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        for i, (d, l) in enumerate(zip(data_to_plot, label)):
            if num_signals == 1:
                label_ring_1 = f"{l} — Ring laser 1" if l else "Ring laser 1"
                label_ring_2 = f"{l} — Ring laser 2" if l else "Ring laser 2"

                color_ring_1 = to_rgba(colors[0], alpha=alpha)
                color_ring_2 = to_rgba(colors[1], alpha=alpha)
            else:
                color = colors[i % len(colors)]
                light_color = tuple(c + (1 - c) * 0.5 for c in to_rgb(color))

                label_ring_1 = f"{l} — Ring laser 1" if l else None
                label_ring_2 = f"{l} — Ring laser 2" if l else None

                color_ring_1 = to_rgba(color, alpha=alpha)
                color_ring_2 = to_rgba(light_color, alpha=alpha)

            scope.plot_signal(
                d,
                y_axis=["ring_laser_1_mW"],
                x_axis="ext_laser_mW",
                show=False,
                xmin=xmin,
                xmax=xmax,
                ymin=ymin,
                ymax=ymax,
                labels={"ring_laser_1_mW": label_ring_1},
                ylabel="Ring laser power [mW]",
                xlabel="Ext. laser power [mW]",
                # save_path=final_outfile,
                ax=ax,
                scatter=True,
                s=12,
                facecolor=color_ring_1,
                marker=".",
            )

            scope.plot_signal(
                d,
                y_axis=["ring_laser_2_mW"],
                x_axis="ext_laser_mW",
                show=False,
                xmin=xmin,
                xmax=xmax,
                ymin=ymin,
                ymax=ymax,
                labels={"ring_laser_2_mW": label_ring_2},
                ylabel="Ring laser power [mW]",
                xlabel="Ext. laser power [mW]",
                # save_path=final_outfile,
                ax=ax,
                scatter=True,
                s=12,
                facecolor=color_ring_2,
                marker=".",
            )

        for h in ax.legend().legend_handles:
            h.set_sizes([100])
            h.set_alpha([1.0])

        ax.figure.savefig(final_outfile)
    if show:    
        plt.show()


def plot_1_T_vs_Ptot(
    Ptot_meas,
    linfit_xy_intersect,
    T_meas_dB,
    outfile, 
    show=False, 
    figsize=(3.5, 2.5),
):
    
    T_est_by_Ptot_dB_ = [
        T_est_by_Ptot_dB(Ptot, G_dB_vs_Pout_curve_params_1) 
        for Ptot in Ptot_meas
    ]

    T_est_by_slope_dB_ = [
        T_est_by_slope_dB(linfit_xy_intersect[0], linfit_xy_intersect[1])
        for linfit_xy_intersect in linfit_xy_intersect
    ]

    data_to_plot = {
        "T_est_by_Ptot_dB": np.array(T_est_by_Ptot_dB_),
        "T_est_by_slope_dB": np.array(T_est_by_slope_dB_),
        "T_meas_dB": np.array(T_meas_dB),
        "Ptot_meas": np.array(Ptot_meas),
    }

    fig, ax = plt.subplots(figsize=figsize)
    fig.set_tight_layout(True)

    scope.plot_signal(
        data_to_plot,
        # y_axis=[],
        x_axis="Ptot_meas",
        show=show,
        # xmin=xmin,
        # xmax=xmax,
        # ymin=ymin,
        # ymax=ymax,
        labels={
            "T_est_by_Ptot_dB": "Estimada por Ptot",
            "T_est_by_slope_dB": "Estimada por pendiente",
            "T_meas_dB": "Medida",
        },
        ylabel="T11 [dB]",
        xlabel="Ptot medida [mW]",
        save_path=outfile,
        ax=ax,
        marker='o'
    )


if __name__ == "__main__":

    ###################################
    #   RISE AND FALL: 1 ANILLO       #
    ###################################

    # if False:
    if True:
        plot_1_vs_t(
            datafile=Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on fall', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_1_fall"),
            show=False,
        )

        plot_1_vs_t(
            datafile=Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on fall', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_1_fall_zoom"),
            xmin=0.6e-6,
            xmax=1.25e-6,
            ymin=0.0,
            ymax=1.0,
            show=False,
        )

        plot_1_vs_t(
            datafile = Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_1_rise"),
            xmin=0.9e-6,
            xmax=1.25e-6,
            show=False,
        )

        plot_1_vs_t(
            datafile = Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_1_rise_zoom"),
            xmin=0.9e-6,
            xmax=1.25e-6,
            show=False,
            ymin=0,
            ymax=1,
        )

        # plot_1_vs_t_diff_yaxis(
        #     datafile = Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
        #     outfile=Path(r"informe\assets\plots\trans_1_rise_two_y_axis"),
        #     # xmin=0.9e-6,
        #     # xmax=1.2e-6,
        #     show=False,
        # )

        # plot_1_vs_t_diff_yaxis(
        #     datafile = Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
        #     outfile=Path(r"informe\assets\plots\trans_1_rise_two_y_axis_zoom"),
        #     xmin=0.9e-6,
        #     xmax=1.1e-6,
        #     show=False,
        # )

        # plot_1_vs_t_diff_yaxis(
        #     datafile = Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on fall', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
        #     outfile=Path(r"informe\assets\plots\trans_1_fall_two_y_axis"),
        #     # xmin=0.9e-6,
        #     # xmax=1.25e-6,
        #     show=False,
        # )

        # plot_1_vs_t_diff_yaxis(
        #     datafile = Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on fall', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
        #     outfile=Path(r"informe\assets\plots\trans_1_fall_two_y_axis_zoom"),
        #     xmin=0.6e-6,
        #     xmax=1.0e-6,
        #     show=False,
        # )

    ###################################
    #   RISE AND FALL: 2 ANILLOS      #
    ###################################

    # if False:
    if True:
        plot_2_vs_t(
            datafile = Path(r".\out\CASO_2_new\SingleRunParams(scope_capture_range='zoom on fall', sweep_waveform='square', sweep_time='100us')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_2_fall"),
            # xmin=0.9e-6,
            # xmax=1.25e-6,
            ymin=0,
            # ymax=1,
            show=False,
        )

        plot_2_vs_t(
            datafile = Path(r".\out\CASO_2_new\SingleRunParams(scope_capture_range='zoom on fall', sweep_waveform='square', sweep_time='100us')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_2_fall_zoom"),
            xmin=0.7e-6,
            xmax=3.0e-6,
            ymin=0,
            # ymax=0.5,
            show=False,
            figsize=(7, 2.5),
        )

        plot_2_vs_t(
            datafile = Path(r".\out\CASO_2_new\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='100us')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_2_rise"),
            # xmin=0.9e-6,
            # xmax=1.25e-6,
            ymin=0,
            # ymax=1,
            show=False,
        )

        plot_2_vs_t(
            datafile = Path(r".\out\CASO_2_new\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='100us')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_2_rise_zoom"),
            xmin=0.8e-6,
            xmax=2.0e-6,
            ymin=0,
            # ymax=0.5,
            show=False,
        )
        trans_2_setup_description = parse_setup_description_toml(r".\out\CASO_2_new\conditions.toml")
        trans_2_aux_capture_linsweep_scope = dict(np.load(Path(r".\out\CASO_2_new\step_transition_zoom_supplementary_capture_2026091021h20m20s.npz")))
        trans_2_aux_capture_linsweep = convert_scope_capture_to_power(trans_2_aux_capture_linsweep_scope, trans_2_setup_description)

        plot_2_vs_t(
            datafile = trans_2_aux_capture_linsweep,
            outfile=Path(r"informe\assets\plots\trans_2_vs_t_linesweep"),
            # xmin=0.2e-6,
            xmax=100e-6,
            ymin=0,
            # ymax=0.5,
            figsize=(7, 2.5),
            show=False,
        )

        plot_2_vs_t(
            datafile = trans_2_aux_capture_linsweep,
            outfile=Path(r"informe\assets\plots\trans_2_rise_vs_t_linesweep_zoom"),
            xmin=15e-6,
            xmax=30e-6,
            ymin=0,
            # ymax=0.5,
            show=False,
        )

        plot_2_vs_t(
            datafile = trans_2_aux_capture_linsweep,
            outfile=Path(r"informe\assets\plots\trans_2_fall_vs_t_linesweep_zoom"),
            xmin=60e-6,
            xmax=75e-6,
            ymin=0,
            # ymax=0.5,
            show=False,
        )

        plot_2_vs_ext(
            datafile = trans_2_aux_capture_linsweep,
            outfile=Path(r"informe\assets\plots\trans_2_vs_ext_linesweep"),
            # xmin=20e-6,
            # xmax=70e-6,
            ymin=0,
            # ymax=0.5,
            figsize=(7, 2.5),
            show=False,
        )


    ###################################
    #   ESTACIONARIO: 1 ANILLO        #
    ###################################

    ring_1_T_tbf_isolator_lin = np.pow(10, ring_1_T_tbf_isolator_dB/10)

    # if False:
    if True:
        plot_1_vs_ext(
            datafile=[
                Path(r".\out\CASO_3\SingleRunParams(scope_capture_range='2 periods (PC max)', sweep_waveform='triang', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=Path(r"informe\assets\plots\stat_1_basic_vs_ext"),
            Ptot_meas=2.65/ring_1_T_tbf_isolator_lin,
            linfit_xy_intersect=[(1.65, 2.65/ring_1_T_tbf_isolator_lin)],
            xmin=-0.10,
            xmax=1.85,
            ymin=-0.10,
            ymax=5.5,
            label=None,
            show=False,
            figsize=(7,2.5),
        )

        plot_1_vs_t(
            datafile=Path(r".\out\CASO_3\SingleRunParams(scope_capture_range='2 periods (PC max)', sweep_waveform='triang', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            outfile=Path(r"informe\assets\plots\stat_1_basic_vs_t"),
            # xmin=-0.10,
            # xmax=1.85,
            # ymin=-0.10,
            # ymax=2.8,
            show=False,
            figsize=(7,2.5),
        )

        Ptot_meas_stat_1_moving_PC=[
            2.65/ring_1_T_tbf_isolator_lin,
            2.49/ring_1_T_tbf_isolator_lin,
            2.44/ring_1_T_tbf_isolator_lin,
        ]
        linfit_xy_intersect_stat_1_moving_PC=[
            (1.65, 2.65/ring_1_T_tbf_isolator_lin),
            (0.915, 2.60/ring_1_T_tbf_isolator_lin),
            (0.42, 2.44/ring_1_T_tbf_isolator_lin),
        ]
        T_meas_dB_stat_1_moving_PC=[
            -9.99,
            -9.99,
            -9.99,
        ]
        label_stat_1_moving_PC=[
            f"Ptot1={Ptot:.2f} mW"
            for Ptot in Ptot_meas_stat_1_moving_PC
        ]

        plot_1_T_vs_Ptot(
            Ptot_meas_stat_1_moving_PC,
            linfit_xy_intersect_stat_1_moving_PC,
            T_meas_dB_stat_1_moving_PC,
            outfile="informe/assets/plots/stat_1_moving_PC_T_med_vs_est.png",
            figsize=(7, 3.5),
        )

        plot_1_vs_ext(
            datafile=[
                Path(r".\out\CASO_3\SingleRunParams(scope_capture_range='2 periods (PC max)', sweep_waveform='triang', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_3_moving_PC\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_3_moving_PC_2\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=Path(r"informe\assets\plots\stat_1_moving_PC"),
            Ptot_meas=Ptot_meas_stat_1_moving_PC,
            linfit_xy_intersect=linfit_xy_intersect_stat_1_moving_PC,
            xmin=-0.10,
            xmax=1.85,
            ymin=-0.10,
            ymax=5.5,
            label=label_stat_1_moving_PC,
            show=False,
        )

        Ptot_meas_stat_1_moving_att=[
            2.65/ring_1_T_tbf_isolator_lin,
            2.49/ring_1_T_tbf_isolator_lin,
            2.40/ring_1_T_tbf_isolator_lin,
        ]
        linfit_xy_intersect_stat_1_moving_att=[
            (1.65, 2.65/ring_1_T_tbf_isolator_lin),
            (0.425, 2.44/ring_1_T_tbf_isolator_lin),
            (0.29, 2.465/ring_1_T_tbf_isolator_lin),
        ]
        T_meas_dB_stat_1_moving_att=[
            -9.99,
            -11.12,
            -16.51,
        ] 
        label_stat_1_moving_att=[
            f"T={T:.2f} dB Ptot1={Ptot:.2f} mW"
            for T, Ptot in zip(T_meas_dB_stat_1_moving_att, Ptot_meas_stat_1_moving_att)
        ]

        plot_1_T_vs_Ptot(
            Ptot_meas_stat_1_moving_att,
            linfit_xy_intersect_stat_1_moving_att,
            T_meas_dB_stat_1_moving_att,
            outfile="informe/assets/plots/stat_1_moving_att_T_med_vs_est.png",
            figsize=(7, 3.5),
        )

        plot_1_vs_ext(
            datafile=[
                Path(r".\out\CASO_3\SingleRunParams(scope_capture_range='2 periods (PC max)', sweep_waveform='triang', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_3_move_att\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_3_move_att_2\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=Path(r"informe\assets\plots\stat_1_moving_att"),
            Ptot_meas=Ptot_meas_stat_1_moving_att,
            linfit_xy_intersect=linfit_xy_intersect_stat_1_moving_att,
            xmin=-0.10,
            xmax=1.85,
            ymin=-0.10,
            ymax=5.5,
            label=label_stat_1_moving_att,
            show=False,
        )
        
    ###################################
    #   ESTACIONARIO: 2 ANILLOS       #
    ###################################

    # if False:
    if True:
        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='100us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_senoid_diff_mod_freq",
            label=["100 us", "1 ms", "10 ms"],
            # ring_1_time_compensation_ns=[0]*3,
            # ring_2_time_compensation_ns=[0]*3,
            figsize=(7, 2.5),
            show=False,
        )

        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triang', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_1ms_diff_mod_shape",
            label=["senoid", "triangle"],
            # ring_1_time_compensation_ns=[0]*2,
            # ring_2_time_compensation_ns=[0]*2,
            show=False,
        )

        plot_2_vs_t(
            datafile=Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            outfile=r"informe\assets\plots\stat_2_1ms_diff_mod_shape_vs_t_sin",
            # label=["senoid", "triangle"],
            # ring_1_time_compensation_ns=[0]*2,
            # ring_2_time_compensation_ns=[0]*2,
            figsize=(7.5,2.5),
            show=False,
        )

        plot_2_vs_t(
            datafile=Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triang', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            outfile=r"informe\assets\plots\stat_2_1ms_diff_mod_shape_vs_t_triangle",
            # label=["senoid", "triangle"],
            # ring_1_time_compensation_ns=[0]*2,
            # ring_2_time_compensation_ns=[0]*2,
            figsize=(7.5,2.5),
            show=False,
        )

        T_caso_4 = {
            "T11": -9.14,
            "T12": -9.43,
            "T21": -15.17,
            "T22": -15.25,
        }
        Ptot_caso_4_pc_max = {
            "Ptot1": 3.3/ring_1_T_tbf_isolator_lin,
            "Ptot2": 1.2/ring_1_T_tbf_isolator_lin,
        }
        Ptot_caso_4_pc_1_moved = {
            "Ptot1": 2.8/ring_1_T_tbf_isolator_lin,
            "Ptot2": 1.2/ring_1_T_tbf_isolator_lin,
        }
        Ptot_caso_4_pc_2_moved = {
            "Ptot1": 3.3/ring_1_T_tbf_isolator_lin,
            "Ptot2": 0.6831/ring_1_T_tbf_isolator_lin,
        }
        Ptot_caso_4_pc_2_both_moved = {
            "Ptot1": 2.56/ring_1_T_tbf_isolator_lin,
            "Ptot2": 1.04/ring_1_T_tbf_isolator_lin,
        }
        Pext_trans_teoricas_caso_4_pc_2_moved = {
            "lower":  0.3804,
            "center": 0.3809,
            "upper":  0.3814,
        }
        Pext_trans_teoricas_caso_4_pc_max = {
            "lower": 0.3639,
            "center": 0.3648,
            "upper": 0.3657,
        }
        Pext_trans_teoricas_caso_4_pc_1_moved = {
            "lower":  0.3804,
            "center": 0.3809,
            "upper":  0.3814,
        }


        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_4_A_PC_MAX\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_1_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_2_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_BOTH_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_manual_T_config_PC_max",
            # label=["PC max", "PC1 moved", "PC2 moved", "Both PCs moved"],
            # ring_1_time_compensation_ns=[0]*2,
            # ring_2_time_compensation_ns=[0]*2,
            figsize=(7, 4),
            show=False,
        )

        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_4_A_PC_MAX\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_A_PC_1_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_A_PC_2_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_A_PC_BOTH_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_manual_T_config_moved_PC_all_cases",
            label=["PC max", "PC1 moved", "PC2 moved", "Both PCs moved"],
            # ring_1_time_compensation_ns=[0]*2,
            # ring_2_time_compensation_ns=[0]*2,
            figsize=(7, 4),
            show=False,
        )


        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_4_A_PC_MAX\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_A_PC_1_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_2_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_BOTH_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_manual_T_config_moved_PC1",
            label=[
                "PC max", 
                "PC1 moved", 
                # "PC2 moved", 
                # "Both PCs moved"
            ],
            # ring_1_time_compensation_ns=[0]*2,
            # ring_2_time_compensation_ns=[0]*2,
            figsize=(7, 4),
            show=False,
        )

        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_4_A_PC_MAX\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_1_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_A_PC_2_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_BOTH_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_manual_T_config_moved_PC2",
            label=[
                "PC max", 
                # "PC1 moved", 
                "PC2 moved", 
                # "Both PCs moved"
            ],
            # ring_1_time_compensation_ns=[0]*2,
            # ring_2_time_compensation_ns=[0]*2,
            figsize=(7, 4),
            show=False,
        )

        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_4_A_PC_MAX\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_1_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                # Path(r".\out\CASO_4_A_PC_2_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
                Path(r".\out\CASO_4_A_PC_BOTH_MOVED\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_manual_T_config_moved_PC1_and_PC2",
            label=[
                "PC max", 
                # "PC1 moved", 
                # "PC2 moved", 
                "Both PCs moved"
            ],
            # ring_1_time_compensation_ns=[0]*2,
            # ring_2_time_compensation_ns=[0]*2,
            figsize=(7, 4),
            show=False,
        )

        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_5_C_PC_MAX\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_PC_max_att_a_ojo",
            figsize=(7, 4),
            show=False,
        )

        plot_2_vs_ext(
            datafile=[
                Path(r".\out\CASO_5_B_PC_Y_ATT_A_OJO\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='triangle', sweep_time='500us')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ],
            outfile=r"informe\assets\plots\stat_2_att_y_PC_a_ojo",
            figsize=(7, 4),
            show=False,
        )
