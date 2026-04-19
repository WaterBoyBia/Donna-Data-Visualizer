# Donna — Table Data Visualization Tool Design

## Overview

A Tkinter GUI application that reads XLS and ASC data files and renders 2D curve plots using matplotlib. The first row of tabular data maps to the X-axis; subsequent rows become individual Y-axis curves. Users can customize axis labels and chart title.

## Requirements

1. Read `.asc` files (HPLC chromatogram format: 3 header lines, tab-separated x/y pairs)
2. Read `.xls` files (OLE-format Excel: row 1 = x-axis, rows 2+ = y-axis series)
3. Plot all Y-axis series as curves on a single chart
4. Customizable X-axis label, Y-axis label, and chart title via text inputs
5. Save chart as PNG
6. Run in the `donna` conda environment (Python 3.12, matplotlib 3.10, numpy 2.4)

## Architecture

```
Donna/
├── main.py              # Entry point
├── readers.py           # File reading (ASC, XLS)
├── plotter.py           # Matplotlib chart creation
├── gui.py               # Tkinter GUI
├── requirements.txt     # Dependencies
└── data/                # Sample data files
```

### Data Flow

File → `readers.read_file()` → `(x_array, [y_arrays], [labels])` → `plotter.create_plot()` → `matplotlib.figure.Figure` → `gui` renders via `FigureCanvasTkAgg`

## Module Specifications

### readers.py

**Public interface:**

```python
def read_file(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read a data file and return (x_data, [y_data_1, ...], [series_name_1, ...])."""
```

- Dispatches to `_read_asc()` or `_read_xls()` based on file extension (case-insensitive)
- Raises `ValueError` for unsupported extensions with a clear message
- Raises `FileNotFoundError` for missing files

**ASC parsing (`_read_asc`):**

- Skip 3 header lines (`Chrom.1`, `UV`, `ml\tmAU`)
- Parse with `np.loadtxt(path, skiprows=3, delimiter='\t')`
- Column 0 → x_data, Column 1 → single y_data series
- Series name: extract from header line 3 (e.g., `"ml\tmAU"` → use `"mAU"` as y-label hint)

**XLS parsing (`_read_xls`):**

- Use `xlrd.open_workbook(path)`, read first sheet
- Row 0: header row with column names (e.g., `['mL', 'UV1_280', 'UV2_260']`)
- Column 0: x-axis values → `np.ndarray`
- Columns 1+: each column is a y-axis series → `list[np.ndarray]`
- Series names: from header row, columns 1+ (e.g., `"UV1_280"`, `"UV2_260"`)
- Handle edge cases: empty cells treated as NaN

### plotter.py

**Public interface:**

```python
def create_plot(
    x: np.ndarray,
    y_series: list[np.ndarray],
    labels: list[str],
    x_label: str = "X",
    y_label: str = "Y",
    title: str = "Chart",
) -> matplotlib.figure.Figure:
    """Create a matplotlib Figure with all y series plotted against x."""
```

- Each y-series drawn as a separate line on the same Axes
- Legend displays series names
- Default line colors from matplotlib color cycle
- `fig.tight_layout()` for clean margins
- Returns the Figure object (GUI handles embedding)

### gui.py

**Main window layout:**

```
+---------------------------------------------------+
|  Donna - Data Visualizer                          |
+---------------------------------------------------+
| [Control Panel]  |  [Plot Area]                   |
|                  |                                 |
| File: [path]     |                                |
| [Browse...]      |     matplotlib canvas           |
|                  |     (embedded figure)            |
| X Label: [___]   |                                 |
| Y Label: [___]   |                                 |
| Title:   [___]   |                                 |
|                  |                                 |
| [Plot]  [Save]   |                                |
+---------------------------------------------------+
```

**Components:**

- File selection: `Button` + `Label` showing selected path, `filedialog.askopenfilename` with filter `*.asc *.xls`
- Label inputs: 3 `Entry` widgets for x-axis, y-axis, title (with default placeholder text)
- Plot button: calls `readers.read_file()` → `plotter.create_plot()` → updates canvas
- Save button: `filedialog.asksaveasfilename` with `.png` filter, calls `fig.savefig()`
- Canvas: `FigureCanvasTkAgg` embedded in the right panel, takes up most of the window
- Window size: 1000x600 minimum

**Error handling:**

- Invalid file: show `messagebox.showerror` with descriptive message
- Empty data: show warning message

### main.py

- Entry point: create Tk root, instantiate GUI, start `mainloop()`
- Set matplotlib backend to `TkAgg` before importing plotter

## Dependencies

```
matplotlib>=3.10
numpy>=2.4
xlrd>=2.0
```

## Installation & Running

```bash
conda activate donna
pip install xlrd
python main.py
```

matplotlib and numpy are already installed in the donna environment.

## Out of Scope

- Multi-file overlay/comparison
- Data editing or transformation
- Zoom/pan on plot (standard matplotlib toolbar can be enabled later)
- CSV or XLSX support (can be added as new reader functions)
- Batch processing
