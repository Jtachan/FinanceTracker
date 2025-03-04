"""Entry points for the command line interface."""
import os.path
import subprocess

from finance_track.minimal_ui import CliFinanceTrack


def run_minimal_ui():
    CliFinanceTrack().run()


def run_bokeh_ui():
    app_module = os.path.abspath(os.path.join(os.path.dirname(__file__), "bokeh_app.py"))
    subprocess.run(f"bokeh serve --show {app_module}", check=False)
