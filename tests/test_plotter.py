import numpy as np
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.figure

from plotter import create_plot


class TestCreatePlot:
    """Tests for the create_plot function."""

    def test_returns_figure(self):
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]
        fig = create_plot(x, y_series, labels)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_single_series_creates_one_line(self):
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]
        fig = create_plot(x, y_series, labels)
        ax = fig.axes[0]
        assert len(ax.get_lines()) == 1

    def test_multiple_series_creates_multiple_lines(self):
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        labels = ["A", "B"]
        fig = create_plot(x, y_series, labels)
        # Two series use twin axes: one line per axis
        total_lines = sum(len(ax.get_lines()) for ax in fig.axes)
        assert total_lines == 2

    def test_single_series_hides_top_and_right_spines(self):
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]

        fig = create_plot(x, y_series, labels)

        assert len(fig.axes) == 1
        ax = fig.axes[0]
        assert not ax.spines["top"].get_visible()
        assert not ax.spines["right"].get_visible()

    def test_multiple_series_hides_only_top_spines(self):
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        labels = ["A", "B"]

        fig = create_plot(
            x,
            y_series,
            labels,
            y_labels=["Left signal", "Right signal"],
        )

        assert len(fig.axes) == 2
        ax1, ax2 = fig.axes
        assert not ax1.spines["top"].get_visible()
        assert not ax2.spines["top"].get_visible()
        assert ax2.spines["right"].get_visible()
        assert ax2.get_ylabel() == "Right signal"

    def test_axis_labels_set(self):
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]
        fig = create_plot(x, y_series, labels, x_label="mL", y_labels=["mAU"], title="Test")
        ax = fig.axes[0]
        assert ax.get_xlabel() == "mL"
        assert ax.get_ylabel() == "mAU"
        assert ax.get_title() == "Test"

    def test_default_labels(self):
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]
        fig = create_plot(x, y_series, labels)
        ax = fig.axes[0]
        assert ax.get_xlabel() == "Elution volume (mL)"
        assert ax.get_ylabel() == "Absorbance at 280 nm (mAU)"
        assert ax.get_title() == "Chart"

    def test_legend_has_series_names(self):
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        labels = ["Alpha", "Beta"]
        fig = create_plot(x, y_series, labels)
        ax = fig.axes[0]
        legend = ax.get_legend()
        assert legend is not None
        legend_texts = [t.get_text() for t in legend.get_texts()]
        assert "Alpha" in legend_texts
        assert "Beta" in legend_texts
