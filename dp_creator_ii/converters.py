from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess


def convert_py_to_nb(python_str):
    '''
    Given Python code as a string, returns a notebook as a string.
    Calls jupytext as a subprocess:
    Not ideal, but only the CLI is documented well.
    '''
    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        py_path = temp_dir_path / 'input.py'
        py_path.write_text(python_str)
        nb_path = temp_dir_path / 'output.ipynb'
        subprocess.run(
            ['jupytext',
             '--to', 'ipynb',  # Target format
             '--output', nb_path.absolute(),  # Output
             py_path.absolute()],  # Input
            check=True)
        return nb_path.read_text()
