"""Entry points for the command line interface."""

from finance_track.minimal_ui import CliFinanceTrack


def run_minimal_ui():
    CliFinanceTrack().run()
