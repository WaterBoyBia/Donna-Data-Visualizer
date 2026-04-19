"""Matplotlib chart creation for Donna data visualizer."""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def create_plot(
    x: np.ndarray,
    y_series: list[np.ndarray],
    labels: list[str],
    x_label: str = "X",
    y_label: str = "Y",
    title: str = "Chart",
) -> matplotlib.figure.Figure:
    """Create a matplotlib Figure with all y series plotted against x.

    Args:
        x: X-axis data array.
        y_series: List of Y-axis data arrays.
        labels: Series names for the legend.
        x_label: Label for the X-axis.
        y_label: Label for the Y-axis.
        title: Chart title.

    Returns:
        A matplotlib Figure containing the plot.
    """
    fig, ax = plt.subplots()

    for y_data, label in zip(y_series, labels):
        ax.plot(x, y_data, label=label)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()

    return fig
