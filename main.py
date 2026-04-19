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
