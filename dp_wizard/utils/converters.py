from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import json
import nbformat
import nbconvert
from warnings import warn
from logging import debug


def _is_kernel_installed() -> bool:
    argv = "jupyter kernelspec list".split(" ")
    result = subprocess.run(argv, check=True, text=True, capture_output=True)
    lines = result.stdout.splitlines()
    return any(line.strip().startswith("python3") for line in lines)


def convert_py_to_nb(python_str: str, execute: bool = False):
    """
    Given Python code as a string, returns a notebook as a string.
    Calls jupytext as a subprocess:
    Not ideal, but only the CLI is documented well.
    """
    with TemporaryDirectory() as temp_dir:
        if not _is_kernel_installed():
            subprocess.run(
                "python -m ipykernel install --name kernel_name --user".split(" "),
                check=True,
            )

        temp_dir_path = Path(temp_dir)
        py_path = temp_dir_path / "input.py"
        py_path.write_text(python_str)

        # for debugging:
        # Path("/tmp/script.py").write_text(python_str)

        argv = (
            "jupytext --from .py --to .ipynb --output -".split(" ")
            + (["--execute"] if execute else [])
            + [str(py_path.absolute())]  # Input
        )
        result = subprocess.run(argv, text=True, capture_output=True)
        if result.returncode != 0:
            warn(result.stderr)
            raise Exception(f"command failed: {' '.join(argv)}")
        return _clean_nb(result.stdout.strip())


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


def convert_nb_to_pdf(python_nb: str):
    # PDFExporter uses LaTeX as an intermediate representation.
    # WebPDFExporter uses HTML.
    return convert_nb(python_nb, nbconvert.WebPDFExporter)


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
