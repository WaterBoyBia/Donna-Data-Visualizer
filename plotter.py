"""Matplotlib chart creation for Donna data visualizer."""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Configure font: Times New Roman primary, SimHei/SimSun fallback for Chinese
matplotlib.rcParams["font.family"] = ["Times New Roman", "SimHei", "SimSun"]
matplotlib.rcParams["axes.unicode_minus"] = False
matplotlib.rcParams["font.size"] = 20
matplotlib.rcParams["axes.linewidth"] = 1.5
matplotlib.rcParams["lines.linewidth"] = 2.0
matplotlib.rcParams["lines.antialiased"] = True

CURVE_COLORS = ["blue", "red"]


def create_plot(
    x: np.ndarray,
    y_series: list[np.ndarray],
    labels: list[str],
    x_label: str = "Elution volume (mL)",
    y_labels: list[str] | None = None,
    title: str = "",
    annotate_peaks: list[bool] | None = None,
) -> matplotlib.figure.Figure:
    """Create a matplotlib Figure with all y series plotted against x.

    Args:
        x: X-axis data array.
        y_series: List of Y-axis data arrays.
        labels: Series names for the legend.
        x_label: Label for the X-axis.
        y_labels: Per-series Y-axis labels. If None, defaults to ["Y"].
        title: Chart title.
        annotate_peaks: Per-series flags; True means annotate that curve's peak.
            None or all-False means no annotations.

    Returns:
        A matplotlib Figure containing the plot.
    """
    if annotate_peaks is None:
        annotate_peaks = [False] * len(y_series)
    if y_labels is None:
        y_labels = ["Absorbance at 280 nm (mAU)"]
    if len(y_labels) < 2 and len(y_series) >= 2:
        y_labels.append("Absorbance at 260 nm (mAU)")

    plt.close("all")
    fig, ax1 = plt.subplots()

    # All curves share the same y-axis (ax1)
    for i, (y_data, label, show_peak) in enumerate(zip(y_series, labels, annotate_peaks)):
        color = CURVE_COLORS[i] if i < len(CURVE_COLORS) else None
        ax1.plot(x, y_data, label=label, color=color)

    # Annotate peaks after all curves are drawn (so ylim is set correctly)
    for i, (y_data, label, show_peak) in enumerate(zip(y_series, labels, annotate_peaks)):
        if show_peak:
            peak_idx = np.nanargmax(y_data)
            peak_x = x[peak_idx]
            peak_y = y_data[peak_idx]
            ax1.annotate(
                f"{peak_x:.3f} ml",
                xy=(peak_x, peak_y),
                xytext=(0, 15),
                textcoords="offset points",
                fontsize=12,
                ha="center",
                va="bottom",
                color="black",
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
            )

    # Expand y-axis upper limit to keep peak annotations inside the frame
    if any(show for show in annotate_peaks):
        y_lo, y_hi = ax1.get_ylim()
        y_range = y_hi - y_lo if y_hi != y_lo else 1.0
        ax1.set_ylim(y_lo, y_hi + y_range * 0.12)

    # Left y-axis label colored by first series, ticks stay black
    left_color = CURVE_COLORS[0] if len(y_series) >= 1 else "black"
    left_ylabel = y_labels[0] if len(y_labels) >= 1 else "Y"
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(left_ylabel, color=left_color)
    ax1.tick_params(axis="y", labelcolor="black")
    ax1.set_xlim(0, 25)

    # Right y-axis: same scale, only label colored by second series
    if len(y_series) >= 2:
        ax2 = ax1.twinx()
        right_color = CURVE_COLORS[1] if len(CURVE_COLORS) >= 2 else "black"
        right_ylabel = y_labels[1] if len(y_labels) >= 2 else "Y"
        ax2.set_ylim(ax1.get_ylim())
        ax2.set_ylabel(right_ylabel, color=right_color)
        ax2.tick_params(axis="y", labelcolor="black")

    if title:
        ax1.set_title(title)
    ax1.legend(fontsize=10)

    fig.tight_layout()

    return fig
