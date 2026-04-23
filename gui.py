"""Tkinter GUI for Donna data visualizer."""

import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from readers import read_file
from plotter import CURVE_COLORS, create_plot


class DonnaApp:
    """Main application window for Donna data visualizer."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Donna - Data Visualizer")
        self.root.minsize(1000, 600)

        self.current_figure: Figure | None = None
        self.annotate_vars: list[tk.BooleanVar] = []
        self._last_file_path: str = ""
        self._click_annotations: list = []
        self._canvas: FigureCanvasTkAgg | None = None
        self._x_data: np.ndarray | None = None
        self._y_series: list[np.ndarray] = []

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
        self.x_label_var = tk.StringVar(value="Elution volume (mL)")
        tk.Entry(left_frame, textvariable=self.x_label_var).pack(fill=tk.X, pady=(0, 10))

        # Y-axis labels (populated dynamically per series)
        tk.Label(left_frame, text="Y-axis labels:").pack(anchor=tk.W)
        self.y_labels_frame = tk.Frame(left_frame)
        self.y_labels_frame.pack(fill=tk.X, pady=(0, 10))
        self.y_label_vars: list[tk.StringVar] = []
        tk.Label(self.y_labels_frame, text="(加载文件后可编辑)", fg="gray").pack(anchor=tk.W)

        # Chart title
        tk.Label(left_frame, text="Chart title:").pack(anchor=tk.W)
        self.title_var = tk.StringVar(value="Chart")
        tk.Entry(left_frame, textvariable=self.title_var).pack(fill=tk.X, pady=(0, 10))

        # Annotate peaks option (populated dynamically after file load)
        tk.Label(left_frame, text="标注峰值:").pack(anchor=tk.W)
        self.annotate_frame = tk.Frame(left_frame)
        self.annotate_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(self.annotate_frame, text="(加载文件后可选)", fg="gray").pack(anchor=tk.W)

        # Show/hide curves option (populated dynamically after file load)
        tk.Label(left_frame, text="显示曲线:").pack(anchor=tk.W)
        self.show_frame = tk.Frame(left_frame)
        self.show_frame.pack(fill=tk.X, pady=(0, 5))
        self.show_vars: list[tk.BooleanVar] = []
        tk.Label(self.show_frame, text="(加载文件后可选)", fg="gray").pack(anchor=tk.W)

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

    def _update_annotate_checkboxes(self, labels: list[str]) -> None:
        """Rebuild per-series annotation checkboxes."""
        for widget in self.annotate_frame.winfo_children():
            widget.destroy()
        self.annotate_vars = []
        for label in labels:
            var = tk.BooleanVar(value=False)
            self.annotate_vars.append(var)
            tk.Checkbutton(
                self.annotate_frame, text=label, variable=var
            ).pack(anchor=tk.W)

    def _update_show_checkboxes(self, labels: list[str]) -> None:
        """Rebuild per-series show/hide checkboxes, default all checked."""
        for widget in self.show_frame.winfo_children():
            widget.destroy()
        self.show_vars = []
        for label in labels:
            var = tk.BooleanVar(value=True)
            self.show_vars.append(var)
            tk.Checkbutton(
                self.show_frame, text=label, variable=var
            ).pack(anchor=tk.W)

    DEFAULT_Y_LABELS = [
        "Absorbance at 280 nm (mAU)",
        "Absorbance at 260 nm (mAU)",
    ]

    def _update_y_label_entries(self, labels: list[str]) -> None:
        """Rebuild per-series Y-axis label entries."""
        for widget in self.y_labels_frame.winfo_children():
            widget.destroy()
        self.y_label_vars = []
        for i, label in enumerate(labels):
            color = CURVE_COLORS[i] if i < len(CURVE_COLORS) else "black"
            default = self.DEFAULT_Y_LABELS[i] if i < len(self.DEFAULT_Y_LABELS) else label
            row_frame = tk.Frame(self.y_labels_frame)
            row_frame.pack(fill=tk.X, pady=(0, 2))
            tk.Label(row_frame, text=f"{label}:", fg=color).pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            self.y_label_vars.append(var)
            tk.Entry(row_frame, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)

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

        x_label = self.x_label_var.get() or "Elution volume (mL)"
        title = self.title_var.get() or "Chart"

        # Only rebuild checkboxes and y-label entries when file changes
        if path != self._last_file_path:
            self._update_annotate_checkboxes(labels)
            self._update_y_label_entries(labels)
            self._update_show_checkboxes(labels)
            self._last_file_path = path

        # Filter series by show/hide checkboxes
        show_flags = [v.get() for v in self.show_vars] if self.show_vars else [True] * len(y_series)
        filtered_y = [y for y, s in zip(y_series, show_flags) if s]
        filtered_labels = [l for l, s in zip(labels, show_flags) if s]
        filtered_annotate_vars = [v for v, s in zip(self.annotate_vars, show_flags) if s]
        filtered_y_label_vars = [v for v, s in zip(self.y_label_vars, show_flags) if s]

        y_labels = [v.get() for v in filtered_y_label_vars] if filtered_y_label_vars else None

        annotate = [v.get() for v in filtered_annotate_vars]
        fig = create_plot(x, filtered_y, filtered_labels, x_label, y_labels=y_labels, title=title, annotate_peaks=annotate)
        self.current_figure = fig
        self._x_data = x
        self._y_series = filtered_y
        self._click_annotations = []

        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas = canvas

        # Enable click-to-annotate on curves
        canvas.mpl_connect("button_press_event", self._on_click_annotate)

    def _on_click_annotate(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        """Annotate the nearest data point when user clicks on the plot."""
        if event.inaxes is None or self.current_figure is None:
            return

        click_x, click_y = event.xdata, event.ydata
        if click_x is None or click_y is None:
            return

        # Find the nearest point across all curves
        best_dist = float("inf")
        best_x = 0.0
        best_y = 0.0

        for y_data in self._y_series:
            distances = np.sqrt((self._x_data - click_x) ** 2 + (y_data - click_y) ** 2)
            idx = int(np.nanargmin(distances))
            if distances[idx] < best_dist:
                best_dist = distances[idx]
                best_x = self._x_data[idx]
                best_y = y_data[idx]

        ax = self.current_figure.axes[0]
        ann = ax.annotate(
            f"{best_x:.3f} ml",
            xy=(best_x, best_y),
            xytext=(0, 15),
            textcoords="offset points",
            fontsize=12,
            ha="center",
            va="bottom",
            color="black",
            arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
        )
        self._click_annotations.append(ann)

        if self._canvas is not None:
            self._canvas.draw_idle()

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
