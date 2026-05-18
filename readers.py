"""File readers for ASC, XLS and CSV data formats."""

import os

import numpy as np


def read_file(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read a data file and return (x_data, [y_data_1, ...], [series_name_1, ...]).

    Args:
        path: Path to the data file (.asc, .xls or .csv).

    Returns:
        Tuple of (x_data, list of y_data arrays, list of series label strings).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is not supported.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".asc", ".xls", ".csv"):
        raise ValueError(
            f"Unsupported file type: '{ext}'. Supported types: .asc, .xls, .csv"
        )

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if ext == ".asc":
        return _read_asc(path)
    elif ext == ".csv":
        return _read_csv(path)
    else:
        return _read_xls(path)


def _read_asc(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read an ASC chromatogram file.

    Format: 3 header lines, then tab-separated x/y data pairs.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Extract y-unit from header line 3 (e.g., "ml\tmAU" -> "mAU")
    # Header is pairs: (x_unit, y_unit, x_unit, y_unit, ...); take y_unit of first pair
    y_label = "Signal"
    if len(lines) >= 3:
        header_parts = lines[2].strip().split("\t")
        non_empty = [p.strip() for p in header_parts if p.strip()]
        if len(non_empty) >= 2:
            y_label = non_empty[1]

    # Parse data: skip 3 header lines; usecols=(0,1) avoids trailing empty column
    data = np.loadtxt(path, skiprows=3, delimiter="\t", usecols=(0, 1))
    x_data = data[:, 0]
    y_data = data[:, 1]

    return x_data, [y_data], [y_label]


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
    y_labels = [headers[c] for c in range(1, sh.ncols)]

    # Read data columns (skip header row)
    x_data = np.array([sh.cell_value(r, 0) for r in range(1, sh.nrows)])

    y_series = []
    for col in range(1, sh.ncols):
        col_data = np.array([sh.cell_value(r, col) for r in range(1, sh.nrows)])
        # Replace empty cells (xlrd returns '') with NaN
        col_data = np.where(col_data == "", np.nan, col_data).astype(float)
        y_series.append(col_data)

    return x_data, y_series, y_labels


def _detect_encoding(path: str) -> str:
    """Detect file encoding from BOM."""
    with open(path, "rb") as f:
        bom = f.read(2)
    if bom == b"\xff\xfe":
        return "utf-16"
    return "utf-8-sig" if bom[:2] == b"\xef\xbb" else "utf-8"


def _read_csv(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read a CSV chromatogram file.

    Format: 3 header lines, then tab-separated data.
    Only the first two columns (x, y) are read.
    Supports UTF-16 (with BOM) and UTF-8 encodings.
    """
    encoding = _detect_encoding(path)

    with open(path, "r", encoding=encoding) as f:
        lines = f.readlines()

    # Extract y-unit from header line 3 (e.g., "ml\tmAU\t..." -> "mAU")
    y_label = "Signal"
    if len(lines) >= 3:
        header_parts = lines[2].strip().split("\t")
        non_empty = [p.strip() for p in header_parts if p.strip()]
        if len(non_empty) >= 2:
            y_label = non_empty[1]

    data = np.loadtxt(path, skiprows=3, delimiter="\t", usecols=(0, 1), encoding=encoding)
    x_data = data[:, 0]
    y_data = data[:, 1]

    return x_data, [y_data], [y_label]
