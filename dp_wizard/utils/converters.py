from pathlib import Path
from tempfile import TemporaryDirectory
from dataclasses import dataclass
from sys import executable
import subprocess
import json
import nbformat
import nbconvert
import jupytext


def _is_kernel_installed() -> bool:
    try:
        # This method isn't well documented, so it may be fragile.
        jupytext.kernels.kernelspec_from_language("python")  # type: ignore
        return True
    except ValueError:  # pragma: no cover
        return False


@dataclass(frozen=True)
class ConversionException(Exception):
    command: str
    stderr: str

    def __str__(self):
        return f"Script to notebook conversion failed: {self.command}\n{self.stderr})"


def convert_py_to_nb(python_str: str, title: str, execute: bool = False):
    """
    Given Python code as a string, returns a notebook as a string.
    Calls jupytext as a subprocess:
    Not ideal, but only the CLI is documented well.
    """
    with TemporaryDirectory() as temp_dir:
        if not _is_kernel_installed():
            subprocess.run(  # pragma: no cover
                [executable]
                + "-m ipykernel install --name kernel_name --user".split(" "),
                check=True,
            )

        temp_dir_path = Path(temp_dir)
        py_path = temp_dir_path / "input.py"
        py_path.write_text(python_str)

        argv = [executable] + "-m jupytext --from .py --to .ipynb --output -".split(" ")
        if execute:
            argv.append("--execute")
        argv.append(str(py_path.absolute()))  # type: ignore
        result = subprocess.run(argv, text=True, capture_output=True)
    if result.returncode != 0:
        # If there is an error, we want a copy of the file that will stay around,
        # outside the "with TemporaryDirectory()" block.
        # The command we show in the error message isn't exactly what was run,
        # but it should reproduce the error.
        debug_path = Path("/tmp/script.py")
        debug_path.write_text(python_str)
        argv.pop()
        argv.append(str(debug_path))  # type: ignore
        raise ConversionException(command=" ".join(argv), stderr=result.stderr)
    nb_dict = json.loads(result.stdout.strip())
    nb_dict["metadata"]["title"] = title
    return _clean_nb(json.dumps(nb_dict))


def _clean_nb(nb_json: str):
    """
    Given a notebook as a string of JSON, remove the coda and pip output.
    (The code produces reports that we do need,
    but the code isn't actually interesting to end users.)
    """
    nb = json.loads(nb_json)
    new_cells = []
    for cell in nb["cells"]:
        if "pip install" in cell["source"][0]:
            cell["outputs"] = []
        if "# Coda\n" in cell["source"]:
            break
        new_cells.append(cell)
    nb["cells"] = new_cells
    return json.dumps(nb, indent=1)


def convert_nb_to_html(python_nb: str):
    return convert_nb(python_nb, nbconvert.HTMLExporter)


def convert_nb(python_nb: str, exporter_constructor):
    notebook = nbformat.reads(python_nb, as_version=4)
    exporter = exporter_constructor(
        template_name="lab",
        # The "classic" template's CSS forces large code cells on to
        # the next page rather than breaking, so use "lab" instead.
        #
        # If you want to tweak the CSS, enable this block and make changes
        # in nbconvert_templates/custom:
        #
        # template_name="custom",
        # extra_template_basedirs=[
        #     str((Path(__file__).parent / "nbconvert_templates").absolute())
        # ],
    )
    (body, _resources) = exporter.from_notebook_node(notebook)
    return body
