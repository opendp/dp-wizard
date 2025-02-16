from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import json
import nbformat
import nbconvert
from warnings import warn


def convert_py_to_nb(python_str: str, execute: bool = False):
    """
    Given Python code as a string, returns a notebook as a string.
    Calls jupytext as a subprocess:
    Not ideal, but only the CLI is documented well.
    """
    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        py_path = temp_dir_path / "input.py"
        py_path.write_text(python_str)

        # for debugging:
        # Path("/tmp/script.py").write_text(python_str)

        argv = (
            [
                "jupytext",
                "--from",
                ".py",
                "--to",
                ".ipynb",
                "--output",
                "-",
            ]
            + (["--execute"] if execute else [])
            + [str(py_path.absolute())]  # Input
        )
        cmd = " ".join(argv)  # for error reporting
        try:
            result = subprocess.run(argv, check=True, text=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            warn(f'STDERR from "{cmd}":\n{e.stderr}')
            if not execute:
                # Might reach here if jupytext is not installed.
                # Error quickly instead of trying to recover.
                raise  # pragma: no cover
            # Install kernel if missing
            # TODO: Is there a better way to do this?
            subprocess.run(
                "python -m ipykernel install --name kernel_name --user".split(" "),
                check=True,
            )
            result = subprocess.run(argv, check=True, text=True, capture_output=True)

        if result.stderr:
            warn(f'STDERR from "{cmd}":\n{result.stderr}')  # pragma: no cover
        return _strip_nb_coda(result.stdout.strip())


def _strip_nb_coda(nb_json: str):
    """
    Given a notebook as a string of JSON, remove the coda.
    (These produce reports that we do need,
    but the code isn't actually interesting to end users.)
    """
    nb = json.loads(nb_json)
    new_cells = []
    for cell in nb["cells"]:
        if "# Coda\n" in cell["source"]:
            break
        new_cells.append(cell)
    nb["cells"] = new_cells
    return json.dumps(nb, indent=1)


def convert_nb_to_html(python_nb: str):
    notebook = nbformat.reads(python_nb, as_version=4)
    exporter = nbconvert.HTMLExporter(template_name="classic")
    (body, _resources) = exporter.from_notebook_node(notebook)
    return body


def convert_nb_to_pdf(python_nb: str):
    notebook = nbformat.reads(python_nb, as_version=4)
    # PDFExporter uses LaTeX as an intermediate representation.
    # WebPDFExporter uses HTML.
    exporter = nbconvert.WebPDFExporter(template_name="classic")
    (body, _resources) = exporter.from_notebook_node(notebook)
    return body
