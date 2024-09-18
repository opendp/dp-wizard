'''DP Creator II makes it easier to get started with Differential Privacy.'''

__version__ = "0.0.1"

def main():
    import shiny
    import os
    from pathlib import Path
    os.chdir(Path(__file__).parent) # run_app() depends on the CWD.
    shiny.run_app(launch_browser=True)