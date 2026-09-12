"""File readers for ASC, XLS, XLSX and CSV data formats."""

import os
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET

import numpy as np


def read_file(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read a data file and return (x_data, [y_data_1, ...], [series_name_1, ...]).

    Args:
        path: Path to the data file (.asc, .xls, .xlsx or .csv).

    Returns:
        Tuple of (x_data, list of y_data arrays, list of series label strings).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is not supported.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".asc", ".xls", ".xlsx", ".csv"):
        raise ValueError(
            f"Unsupported file type: '{ext}'. Supported types: .asc, .xls, .xlsx, .csv"
        )

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if ext == ".asc":
        return _read_asc(path)
    elif ext == ".csv":
        return _read_csv(path)
    elif ext == ".xlsx":
        return _read_xlsx(path)
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


def _read_xlsx(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Read the first worksheet of an XLSX file."""
    try:
        import openpyxl
    except ImportError:
        return _read_xlsx_xml(path)

    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        worksheet = workbook.worksheets[0]
        rows = list(worksheet.iter_rows(values_only=True))
    finally:
        workbook.close()

    if len(rows) < 2:
        raise ValueError("XLSX file must have at least 2 rows and 2 columns")
    width = max((len(row) for row in rows), default=0)
    if width < 2:
        raise ValueError("XLSX file must have at least 2 rows and 2 columns")

    headers = list(rows[0]) + [None] * (width - len(rows[0]))
    y_labels = ["" if headers[c] is None else str(headers[c]) for c in range(1, width)]

    def as_float(value):
        if value is None or value == "":
            return np.nan
        return float(value)

    x_data = np.array([as_float(row[0] if row else None) for row in rows[1:]], dtype=float)
    y_series = [
        np.array(
            [as_float(row[col] if col < len(row) else None) for row in rows[1:]],
            dtype=float,
        )
        for col in range(1, width)
    ]
    return x_data, y_series, y_labels


def _read_xlsx_xml(path: str) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Minimal XLSX reader used when openpyxl is unavailable."""
    with zipfile.ZipFile(path) as archive:
        shared_strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root:
                shared_strings.append(
                    "".join(node.text or "" for node in item.iter() if node.tag.endswith("}t"))
                )

        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        first_sheet = next(node for node in workbook_root.iter() if node.tag.endswith("}sheet"))
        rel_id = next(value for key, value in first_sheet.attrib.items() if key.endswith("}id"))
        rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = next(node.attrib["Target"] for node in rels_root if node.attrib.get("Id") == rel_id)
        sheet_name = posixpath.normpath(posixpath.join("xl", target.lstrip("/")))
        sheet_root = ET.fromstring(archive.read(sheet_name))

    cell_ref_pattern = re.compile(r"([A-Za-z]+)([0-9]+)$")

    def column_index(reference):
        match = cell_ref_pattern.match(reference)
        if not match:
            return 0
        index = 0
        for char in match.group(1).upper():
            index = index * 26 + ord(char) - ord("A") + 1
        return index - 1

    rows = []
    for row_node in (node for node in sheet_root.iter() if node.tag.endswith("}row")):
        values = {}
        for cell in (node for node in row_node if node.tag.endswith("}c")):
            col = column_index(cell.attrib.get("r", ""))
            value_node = next((node for node in cell if node.tag.endswith("}v")), None)
            value = "" if value_node is None or value_node.text is None else value_node.text
            if cell.attrib.get("t") == "s" and value:
                value = shared_strings[int(value)]
            elif cell.attrib.get("t") == "inlineStr":
                value = "".join(node.text or "" for node in cell.iter() if node.tag.endswith("}t"))
            values[col] = value
        rows.append(values)

    width = max((max(row.keys(), default=-1) for row in rows), default=-1) + 1
    if len(rows) < 2 or width < 2:
        raise ValueError("XLSX file must have at least 2 rows and 2 columns")

    def get(row, col):
        return row.get(col, "")

    y_labels = [str(get(rows[0], col)) for col in range(1, width)]

    def as_float(value):
        return np.nan if value in (None, "") else float(value)

    x_data = np.array([as_float(get(row, 0)) for row in rows[1:]], dtype=float)
    y_series = [
        np.array([as_float(get(row, col)) for row in rows[1:]], dtype=float)
        for col in range(1, width)
    ]
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
