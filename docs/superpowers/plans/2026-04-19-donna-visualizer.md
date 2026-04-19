# Donna Data Visualizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Tkinter GUI app that reads XLS/ASC data files and renders 2D curve plots with customizable labels and PNG export.

**Architecture:** Modular design with 4 source files. `readers.py` handles file parsing (ASC via numpy, XLS via xlrd), `plotter.py` creates matplotlib figures, `gui.py` provides the Tkinter interface with embedded matplotlib canvas, `main.py` is the entry point. Data flows: File → readers → numpy arrays → plotter → Figure → gui canvas.

**Tech Stack:** Python 3.12, Tkinter, matplotlib 3.10, numpy 2.4, xlrd 2.0

---

### Task 1: Project Setup & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```txt
matplotlib>=3.10
numpy>=2.4
xlrd>=2.0
```

- [ ] **Step 2: Install dependencies**

Run: `D:/miniconda/envs/donna/python.exe -m pip install -r d:/university/anything/Donna/requirements.txt`

Expected: All packages installed successfully (matplotlib and numpy already present, xlrd newly installed).

- [ ] **Step 3: Create tests directory**

Create empty `tests/__init__.py` file.

- [ ] **Step 4: Verify environment**

Run: `D:/miniconda/envs/donna/python.exe -c "import matplotlib, numpy, xlrd; print('All deps OK')"`

Expected: `All deps OK`

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/__init__.py
git commit -m "chore: add project dependencies and test directory"
```

---

### Task 2: ASC File Reader

**Files:**
- Create: `readers.py`
- Create: `tests/test_readers.py`

- [ ] **Step 1: Write failing tests for ASC reading**

```python
# tests/test_readers.py
import numpy as np
import numpy.testing as npt
import os
import tempfile
import pytest
from readers import read_file


class TestReadAsc:
    """Tests for reading .asc files."""

    def test_read_asc_returns_correct_structure(self):
        """read_file for .asc returns (x_array, [y_array], [label])."""
        asc_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "202512211-RSV-17-rsv-22-hepes 10 150 7.5-s200.asc"
        )
        x, y_series, labels = read_file(asc_path)
        assert isinstance(x, np.ndarray)
        assert isinstance(y_series, list)
        assert len(y_series) >= 1
        assert isinstance(y_series[0], np.ndarray)
        assert isinstance(labels, list)
        assert len(labels) == len(y_series)

    def test_read_asc_data_shape(self):
        """ASC file x and y arrays have the same length."""
        asc_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "202512211-RSV-17-rsv-22-hepes 10 150 7.5-s200.asc"
        )
        x, y_series, labels = read_file(asc_path)
        assert x.ndim == 1
        assert y_series[0].ndim == 1
        assert len(x) == len(y_series[0])
        assert len(x) > 0

    def test_read_asc_first_values(self):
        """First data row of sample ASC file matches known values."""
        asc_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "202512211-RSV-17-rsv-22-hepes 10 150 7.5-s200.asc"
        )
        x, y_series, labels = read_file(asc_path)
        npt.assert_almost_equal(x[0], 0.0, decimal=3)
        npt.assert_almost_equal(y_series[0][0], -0.8936033, decimal=5)

    def test_read_asc_series_name(self):
        """ASC file label is extracted from header (e.g., 'mAU')."""
        asc_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "202512211-RSV-17-rsv-22-hepes 10 150 7.5-s200.asc"
        )
        _, _, labels = read_file(asc_path)
        assert len(labels) == 1
        assert "mAU" in labels[0]

    def test_read_unsupported_extension_raises(self):
        """read_file raises ValueError for unsupported file types."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            read_file("data.csv")

    def test_read_missing_file_raises(self):
        """read_file raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            read_file("nonexistent.asc")

    def test_read_asc_from_temp_file(self):
        """Parse a minimal ASC file created in a temp directory."""
        content = "Chrom.1\nUV\nml\tmAU\n0\t1.5\n1\t2.5\n2\t3.5\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".asc", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = f.name
        try:
            x, y_series, labels = read_file(tmp_path)
            npt.assert_array_equal(x, np.array([0.0, 1.0, 2.0]))
            npt.assert_array_almost_equal(y_series[0], np.array([1.5, 2.5, 3.5]))
            assert labels == ["mAU"]
        finally:
            os.unlink(tmp_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `D:/miniconda/envs/donna/python.exe -m pytest tests/test_readers.py -v`

Expected: FAIL — `ModuleNotFoundError: No module named 'readers'`

- [ ] **Step 3: Implement ASC reader**

```python
# readers.py
"""File readers for ASC and XLS data formats."""

import os

import numpy as np


def read_file(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read a data file and return (x_data, [y_data_1, ...], [series_name_1, ...]).

    Args:
        path: Path to the data file (.asc or .xls).

    Returns:
        Tuple of (x_data, list of y_data arrays, list of series label strings).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is not supported.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext == ".asc":
        return _read_asc(path)
    elif ext == ".xls":
        return _read_xls(path)
    else:
        raise ValueError(
            f"Unsupported file type: '{ext}'. Supported types: .asc, .xls"
        )


def _read_asc(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read an ASC chromatogram file.

    Format: 3 header lines, then tab-separated x/y data pairs.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Extract y-unit from header line 3 (e.g., "ml\tmAU" → "mAU")
    y_label = "Signal"
    if len(lines) >= 3:
        header_parts = lines[2].strip().split("\t")
        if len(header_parts) >= 2:
            y_label = header_parts[1].strip()

    # Parse data: skip 3 header lines
    data = np.loadtxt(path, skiprows=3, delimiter="\t")
    x_data = data[:, 0]
    y_data = data[:, 1]

    return x_data, [y_data], [y_label]


def _read_xls(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read an XLS file (to be implemented in Task 3)."""
    raise NotImplementedError("XLS reading not yet implemented")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `D:/miniconda/envs/donna/python.exe -m pytest tests/test_readers.py -v`

Expected: All `TestReadAsc` tests PASS.

- [ ] **Step 5: Commit**

```bash
git add readers.py tests/test_readers.py
git commit -m "feat: add ASC file reader with tests"
```

---

### Task 3: XLS File Reader

**Files:**
- Modify: `readers.py` (replace `_read_xls` stub)
- Modify: `tests/test_readers.py` (add XLS tests)

- [ ] **Step 1: Write failing tests for XLS reading**

```python
# Append to tests/test_readers.py

class TestReadXls:
    """Tests for reading .xls files."""

    def test_read_xls_returns_correct_structure(self):
        """read_file for .xls returns (x_array, [y_arrays], [labels])."""
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        x, y_series, labels = read_file(xls_path)
        assert isinstance(x, np.ndarray)
        assert isinstance(y_series, list)
        assert len(y_series) >= 1
        assert isinstance(y_series[0], np.ndarray)
        assert isinstance(labels, list)
        assert len(labels) == len(y_series)

    def test_read_xls_data_shape(self):
        """XLS file x and each y array have the same length."""
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        x, y_series, labels = read_file(xls_path)
        for y in y_series:
            assert len(x) == len(y)

    def test_read_xls_multiple_series(self):
        """XLS file with 3 columns produces 2 y-series (col 0 = x)."""
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        x, y_series, labels = read_file(xls_path)
        assert len(y_series) == 2
        assert len(labels) == 2

    def test_read_xls_series_names_from_header(self):
        """Series names come from the header row of the XLS file."""
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        _, _, labels = read_file(xls_path)
        assert "UV1_280" in labels[0]
        assert "UV2_260" in labels[1]

    def test_read_xls_first_values(self):
        """First data values match known XLS file content."""
        xls_path = os.path.join(
            os.path.dirname(__file__), "..", "data",
            "20260327-NDN-RSV-22-HEPES.xls"
        )
        x, y_series, labels = read_file(xls_path)
        npt.assert_almost_equal(x[0], -2.775, decimal=3)
        npt.assert_almost_equal(y_series[0][0], 54.197, decimal=2)
        npt.assert_almost_equal(y_series[1][0], 28.14, decimal=2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `D:/miniconda/envs/donna/python.exe -m pytest tests/test_readers.py::TestReadXls -v`

Expected: FAIL — `NotImplementedError: XLS reading not yet implemented`

- [ ] **Step 3: Implement XLS reader**

Replace the `_read_xls` stub in `readers.py` with:

```python
def _read_xls(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read an XLS file.

    Format: Row 0 = headers, column 0 = x-data, columns 1+ = y-data series.
    """
    import xlrd

    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_index(0)

    if sh.nrows < 2 or sh.ncols < 2:
        raise ValueError("XLS file must have at least 2 rows and 2 columns")

    # Read header row for series labels
    headers = [sh.cell_value(0, c) for c in range(sh.ncols)]
    x_label = headers[0]
    y_labels = [headers[c] for c in range(1, sh.ncols)]

    # Read data columns (skip header row)
    num_data_rows = sh.nrows - 1
    x_data = np.array([sh.cell_value(r, 0) for r in range(1, sh.nrows)])

    y_series = []
    for col in range(1, sh.ncols):
        col_data = np.array([sh.cell_value(r, col) for r in range(1, sh.nrows)])
        # Replace empty cells (xlrd returns '') with NaN
        col_data = np.where(
            col_data == "", np.nan, col_data
        ).astype(float)
        y_series.append(col_data)

    return x_data, y_series, y_labels
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `D:/miniconda/envs/donna/python.exe -m pytest tests/test_readers.py -v`

Expected: All `TestReadXls` and `TestReadAsc` tests PASS.

- [ ] **Step 5: Commit**

```bash
git add readers.py tests/test_readers.py
git commit -m "feat: add XLS file reader with tests"
```

---

### Task 4: Plotter Module

**Files:**
- Create: `plotter.py`
- Create: `tests/test_plotter.py`

- [ ] **Step 1: Write failing tests for plotter**

```python
# tests/test_plotter.py
import numpy as np
import pytest
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for tests
import matplotlib.figure

from plotter import create_plot


class TestCreatePlot:
    """Tests for the create_plot function."""

    def test_returns_figure(self):
        """create_plot returns a matplotlib Figure."""
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]
        fig = create_plot(x, y_series, labels)
        assert isinstance(fig, matplotlib.figure.Figure)

    def test_single_series_creates_one_line(self):
        """Single y-series produces one line on the axes."""
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]
        fig = create_plot(x, y_series, labels)
        ax = fig.axes[0]
        assert len(ax.get_lines()) == 1

    def test_multiple_series_creates_multiple_lines(self):
        """Multiple y-series produce multiple lines."""
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3]), np.array([4, 5, 6])]
        labels = ["A", "B"]
        fig = create_plot(x, y_series, labels)
        ax = fig.axes[0]
        assert len(ax.get_lines()) == 2

    def test_axis_labels_set(self):
        """X-axis, y-axis, and title labels are set correctly."""
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]
        fig = create_plot(x, y_series, labels, x_label="mL", y_label="mAU", title="Test")
        ax = fig.axes[0]
        assert ax.get_xlabel() == "mL"
        assert ax.get_ylabel() == "mAU"
        assert ax.get_title() == "Test"

    def test_default_labels(self):
        """Default labels are used when none specified."""
        x = np.array([0, 1, 2])
        y_series = [np.array([1, 2, 3])]
        labels = ["Signal"]
        fig = create_plot(x, y_series, labels)
        ax = fig.axes[0]
        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == "Y"
        assert ax.get_title() == "Chart"

    def test_legend_has_series_names(self):
        """Legend labels match the provided series names."""
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `D:/miniconda/envs/donna/python.exe -m pytest tests/test_plotter.py -v`

Expected: FAIL — `ModuleNotFoundError: No module named 'plotter'`

- [ ] **Step 3: Implement plotter**

```python
# plotter.py
"""Matplotlib chart creation for Donna data visualizer."""

import matplotlib.figure
import numpy as np


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
    fig, ax = matplotlib.pyplot.subplots()

    for y_data, label in zip(y_series, labels):
        ax.plot(x, y_data, label=label)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()

    return fig
```

- [ ] **Step 4: Run tests to verify they fail (import issue)**

Run: `D:/miniconda/envs/donna/python.exe -m pytest tests/test_plotter.py -v`

The test will fail because `matplotlib.pyplot.subplots()` creates a figure attached to pyplot state, but `Agg` backend needs `matplotlib.pyplot` imported. Fix by using `matplotlib.pyplot`:

Replace the implementation with:

```python
# plotter.py
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `D:/miniconda/envs/donna/python.exe -m pytest tests/test_plotter.py -v`

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add plotter.py tests/test_plotter.py
git commit -m "feat: add plotter module with tests"
```

---

### Task 5: Tkinter GUI

**Files:**
- Create: `gui.py`

No automated tests for GUI (Tkinter is hard to test programmatically). Manual verification only.

- [ ] **Step 1: Implement the GUI**

```python
# gui.py
"""Tkinter GUI for Donna data visualizer."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from readers import read_file
from plotter import create_plot


class DonnaApp:
    """Main application window for Donna data visualizer."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Donna - Data Visualizer")
        self.root.minsize(1000, 600)

        self.current_figure: Figure | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the GUI layout."""
        # Left panel: controls
        left_frame = tk.Frame(self.root, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # File selection
        tk.Label(left_frame, text="File:").pack(anchor=tk.W)
        file_frame = tk.Frame(left_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        self.file_path_var = tk.StringVar()
        self.file_label = tk.Label(
            file_frame, textvariable=self.file_path_var,
            width=30, anchor=tk.W, relief=tk.SUNKEN
        )
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(file_frame, text="Browse...", command=self._browse_file).pack(side=tk.RIGHT)

        # X-axis label
        tk.Label(left_frame, text="X-axis label:").pack(anchor=tk.W)
        self.x_label_var = tk.StringVar(value="X")
        tk.Entry(left_frame, textvariable=self.x_label_var).pack(fill=tk.X, pady=(0, 10))

        # Y-axis label
        tk.Label(left_frame, text="Y-axis label:").pack(anchor=tk.W)
        self.y_label_var = tk.StringVar(value="Y")
        tk.Entry(left_frame, textvariable=self.y_label_var).pack(fill=tk.X, pady=(0, 10))

        # Chart title
        tk.Label(left_frame, text="Chart title:").pack(anchor=tk.W)
        self.title_var = tk.StringVar(value="Chart")
        tk.Entry(left_frame, textvariable=self.title_var).pack(fill=tk.X, pady=(0, 10))

        # Buttons
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Button(button_frame, text="Plot", command=self._plot, width=10).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Save PNG", command=self._save, width=10).pack(side=tk.LEFT, padx=(10, 0))

        # Right panel: matplotlib canvas
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._show_placeholder()

    def _show_placeholder(self) -> None:
        """Show a placeholder message on the canvas area."""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        tk.Label(
            self.canvas_frame, text="Select a file and click Plot",
            font=("Arial", 14), fg="gray"
        ).pack(expand=True)

    def _browse_file(self) -> None:
        """Open file dialog to select a data file."""
        filetypes = [
            ("Data files", "*.asc *.xls"),
            ("ASC files", "*.asc"),
            ("XLS files", "*.xls"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.file_path_var.set(path)

    def _plot(self) -> None:
        """Read the selected file and display the plot."""
        path = self.file_path_var.get()
        if not path:
            messagebox.showwarning("No file", "Please select a data file first.")
            return

        try:
            x, y_series, labels = read_file(path)
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("File error", str(e))
            return
        except Exception as e:
            messagebox.showerror("Read error", f"Failed to read file:\n{e}")
            return

        if len(x) == 0:
            messagebox.showwarning("Empty data", "The file contains no data.")
            return

        x_label = self.x_label_var.get() or "X"
        y_label = self.y_label_var.get() or "Y"
        title = self.title_var.get() or "Chart"

        fig = create_plot(x, y_series, labels, x_label, y_label, title)
        self.current_figure = fig

        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _save(self) -> None:
        """Save the current plot as a PNG file."""
        if self.current_figure is None:
            messagebox.showwarning("No plot", "Please create a plot first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
        )
        if path:
            self.current_figure.savefig(path, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Saved", f"Chart saved to:\n{path}")
```

- [ ] **Step 2: Commit**

```bash
git add gui.py
git commit -m "feat: add Tkinter GUI with file browsing, label inputs, and save"
```

---

### Task 6: Entry Point

**Files:**
- Create: `main.py`

- [ ] **Step 1: Implement main.py**

```python
# main.py
"""Entry point for Donna data visualizer."""

import tkinter as tk

import matplotlib
matplotlib.use("TkAgg")

from gui import DonnaApp


def main() -> None:
    """Launch the Donna data visualizer application."""
    root = tk.Tk()
    _ = DonnaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the application manually**

Run: `D:/miniconda/envs/donna/python.exe d:/university/anything/Donna/main.py`

Expected: Window opens with left control panel (file browser, label entries, Plot/Save buttons) and right placeholder area.

- [ ] **Step 3: Manual test — load ASC file**

1. Click "Browse...", select an ASC file from `data/`
2. Click "Plot"
3. Verify: chart appears with curve, axis labels show "X" and "Y"

- [ ] **Step 4: Manual test — load XLS file**

1. Click "Browse...", select an XLS file from `data/`
2. Click "Plot"
3. Verify: chart appears with multiple curves and legend

- [ ] **Step 5: Manual test — customize labels**

1. With a plot displayed, change X-axis label to "mL", Y-axis to "mAU", Title to "Test"
2. Click "Plot"
3. Verify: labels update on the chart

- [ ] **Step 6: Manual test — save PNG**

1. Click "Save PNG"
2. Choose a save location
3. Verify: PNG file is created with the chart

- [ ] **Step 7: Commit**

```bash
git add main.py
git commit -m "feat: add application entry point"
```

---

### Task 7: Run All Tests & Final Verification

**Files:**
- All project files

- [ ] **Step 1: Run the full test suite**

Run: `D:/miniconda/envs/donna/python.exe -m pytest tests/ -v`

Expected: All tests PASS.

- [ ] **Step 2: Run the application end-to-end**

Run: `D:/miniconda/envs/donna/python.exe d:/university/anything/Donna/main.py`

Verify:
- ASC file loads and plots correctly
- XLS file loads and plots correctly
- Custom labels work
- PNG save works
- Error handling (no file selected, invalid file) shows appropriate messages

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "chore: final verification and cleanup"
```
