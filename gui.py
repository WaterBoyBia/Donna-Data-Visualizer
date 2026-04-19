"""Tkinter GUI for Donna data visualizer."""

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
