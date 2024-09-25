from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess


def convert_py_to_nb(python_str, execute=False):
    """
    Given Python code as a string, returns a notebook as a string.
    Calls jupytext as a subprocess:
    Not ideal, but only the CLI is documented well.
    """
    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        py_path = temp_dir_path / "input.py"
        py_path.write_text(python_str)
        nb_path = temp_dir_path / "output.ipynb"
        argv = (
            [
                "jupytext",
                "--to",
                "ipynb",  # Target format
                "--output",
                nb_path.absolute(),  # Output
            ]
            + (["--execute"] if execute else [])
            + [py_path.absolute()]  # Input
        )
        try:
            subprocess.run(argv, check=True)
        except subprocess.CalledProcessError:  # pragma: no cover
            if not execute:
                raise
            # Install kernel if missing
            # TODO: Is there a better way to do this?
            subprocess.run(
                "python -m ipykernel install --name kernel_name --user".split(" "),
                check=True,
            )
            subprocess.run(argv, check=True)

        return nb_path.read_text()
