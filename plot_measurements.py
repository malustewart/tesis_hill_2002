from pathlib import Path
import numpy as np
from scope import scope
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba, to_rgb

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


def plot_1_vs_t(datafile, outfile, show=False, xmin=0, xmax=np.inf, ymin=None, ymax=None):

    data = dict(np.load(datafile))

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
            final_outfile = outfile

        scope.plot_signal(
            data_to_plot,
            y_axis=['ext_laser_mW', "ring_laser_1_mW"],
            x_axis="t",
            show=show,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            labels={"ring_laser_1_mW": "Ring laser 1", "ext_laser_mW": "Ext. laser"},
            ylabel="Power [mW]",
            save_path=final_outfile,
        )


def plot_2_vs_t(datafile, outfile, show=False, xmin=0, xmax=np.inf, ymin=None, ymax=None):

    data = dict(np.load(datafile))

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
            final_outfile = outfile


        scope.plot_signal(
            data_to_plot,
            y_axis=['ext_laser_mW', "ring_laser_1_mW", "ring_laser_2_mW"],
            x_axis="t",
            show=show,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            labels={"ring_laser_1_mW": "Ring laser 1","ring_laser_2_mW": "Ring laser 2", "ext_laser_mW": "Ext. laser"},
            ylabel="Power [mW]",
            save_path=final_outfile,
        )


def plot_stat_1_vs_ext(datafile, outfile, show=False, xmin=0, xmax=np.inf, ymin=None, ymax=None, ring_1_time_compensation_ns=0):

    data = dict(np.load(datafile))
    data = compensate_arrival_time_diff(data, ring_1_time_compensation_ns, 0)

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
            final_outfile = outfile

        scope.plot_signal(
            data_to_plot,
            y_axis=["ring_laser_1_mW"],
            x_axis="ext_laser_mW",
            show=show,
            xmin=xmin,
            xmax=xmax,
            ymin=ymin,
            ymax=ymax,
            labels={"ring_laser_1_mW": ""},
            ylabel="Ring laser 1 power [mW]",
            xlabel="Ext. laser power [mW]",
            save_path=final_outfile,
        )


def plot_1_vs_ext(datafile, outfile, show=False, xmin=0, xmax=np.inf, ymin=None, ymax=None, label=None, ring_1_time_compensation_ns=0, alpha=0.3):

    if not isinstance(datafile, (list, tuple, np.ndarray)):
        datafile = [datafile]

    num_signals = len(datafile)

    # handle missing input
    if not ring_1_time_compensation_ns:
        ring_1_time_compensation_ns = [0] * num_signals

    if not label:
        label = [None] * num_signals

    # if only 1 signal, convert inputs to list
    if not isinstance(ring_1_time_compensation_ns, (list, tuple, np.ndarray)):
        ring_1_time_compensation_ns = [ring_1_time_compensation_ns]

    if not isinstance(label, (list, tuple, np.ndarray)):
        label = [label]

    assert(len(datafile) == len(ring_1_time_compensation_ns))
    assert(len(datafile) == len(label))

    data = [ dict(np.load(df)) for df in datafile ]
    data = [ compensate_arrival_time_diff(d, r_1_t_c, 0) for d, r_1_t_c in zip(data, ring_1_time_compensation_ns) ]

    outfile=Path(outfile)

    for smooth in (True, False):
        fig = plt.figure()
        ax = fig.gca()

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
            final_outfile = outfile

        for d, l in zip(data_to_plot, label):
            label_ring_1 = f"{l}" if l else None

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
                marker="."
            )

        for h in ax.legend().legend_handles:
            h.set_sizes([100])
            h.set_alpha([1.0])

        ax.figure.savefig(final_outfile)
    if show:
        plt.show()


def plot_2_vs_ext(datafile, outfile, show=False, xmin=0, xmax=np.inf, ymin=None, ymax=None, label=None, ring_1_time_compensation_ns=0, ring_2_time_compensation_ns=0, alpha=0.1):
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

    data = [ dict(np.load(df)) for df in datafile ]
    data = [ compensate_arrival_time_diff(d, r_1_t_c, r_2_t_c) for d, r_1_t_c, r_2_t_c in zip(data, ring_1_time_compensation_ns, ring_2_time_compensation_ns) ]

    outfile=Path(outfile)

    for smooth in (True, False):
        fig = plt.figure()
        ax = fig.gca()
        
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
            final_outfile = outfile

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


if __name__ == "__main__":

    ###################################
    #   RISE AND FALL: 1 ANILLO       #
    ###################################

    if False:
        plot_1_vs_t(
            datafile=Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on fall', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_1_fall_no_comp"),
            show=False,
        )

        plot_1_vs_t(
            datafile = Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_1_rise_no_comp"),
            xmin=0.9e-6,
            xmax=1.25e-6,
            show=False,
        )

        plot_1_vs_t(
            datafile = Path(r".\out\CASO_1\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_1_rise_no_comp_zoom"),
            xmin=0.9e-6,
            xmax=1.25e-6,
            show=False,
            ymin=0,
            ymax=1,
        )

    ###################################
    #   RISE AND FALL: 2 ANILLOS      #
    ###################################

    if False:
        plot_2_vs_t(
            datafile = Path(r".\out\CASO_2\SingleRunParams(scope_capture_range='zoom on fall', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_2_fall_no_comp"),
            # xmin=0.9e-6,
            # xmax=1.25e-6,
            # ymin=0,
            # ymax=1,
            show=False,
        )

        plot_2_vs_t(
            datafile = Path(r".\out\CASO_2\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_2_rise_no_comp"),
            # xmin=0.9e-6,
            # xmax=1.25e-6,
            # ymin=0,
            # ymax=1,
            show=False,
        )

        plot_2_vs_t(
            datafile = Path(r".\out\CASO_2\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_2_rise_no_comp_zoom_ring_1"),
            xmin=0.12e-6,
            xmax=0.35e-6,
            ymin=0,
            ymax=0.5,
            show=False,
        )

        plot_2_vs_t(
            datafile = Path(r".\out\CASO_2\SingleRunParams(scope_capture_range='zoom on rise', sweep_waveform='square', sweep_time='10ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"), 
            outfile=Path(r"informe\assets\plots\trans_2_rise_no_comp_zoom_ring_2"),
            xmin=0.12e-6,
            xmax=0.35e-6,
            ymin=2.25,
            ymax=2.4,
            show=False,
        )

    ###################################
    #   ESTACIONARIO: 1 ANILLO        #
    ###################################

    if False:
        plot_stat_1_vs_ext(
            datafile=Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            outfile="borrar_1_comp_0",
            show=False,
        )

        plot_1_vs_ext(
            datafile=[Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz")] * 2,
            outfile="borrar_overlap",
            label=["0 ns comp", "5000 ns comp"],
            ring_1_time_compensation_ns=[0, 5000],
            show=False,
        )


    plot_stat_1_vs_ext(
        datafile=Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
        outfile="borrar_1_func_original",
        show=False,
    )

    plot_1_vs_ext(
        datafile=
            [
                Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            ] * 3,
        outfile="borrar_1_func_overlap",
        ring_1_time_compensation_ns = [0,10000, 20000],
        show=False,
    )


    ###################################
    #   ESTACIONARIO: 2 ANILLOS       #
    ###################################

    if False:
        plot_2_vs_ext(
            datafile=Path(r".\out\CASO_4_medicion_1\SingleRunParams(scope_capture_range='2 periods', sweep_waveform='senoid', sweep_time='1ms')\artifacts\scope_processed_no_arrival_time_compensation.npz"),
            outfile="borrar_2",
            alpha=1.0,
            show=False,
        )

