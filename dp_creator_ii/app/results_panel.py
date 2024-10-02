from shiny import ui, render

from dp_creator_ii.template import make_notebook_py, make_script_py
from dp_creator_ii.converters import convert_py_to_nb


def results_ui():
    return ui.nav_panel(
        "Download results",
        "TODO: Download results",
        ui.download_button("download_script", "Download script"),
        ui.download_button("download_notebook_unexecuted", "Download notebook"),
        value="results_panel",
    )


def results_server(input, output, session):
    @render.download(
        filename="dp-creator-script.py",
        media_type="text/x-python",
    )
    async def download_script():
        script_py = make_script_py(
            unit=1,
            loss=1,
            weights=[1],
        )
        yield script_py

    @render.download(
        filename="dp-creator-notebook.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_unexecuted():
        notebook_py = make_notebook_py(
            csv_path="todo.csv",
            unit=1,
            loss=1,
            weights=[1],
        )
        notebook_nb = convert_py_to_nb(notebook_py)
        yield notebook_nb

    @render.download(
        filename="dp-creator-notebook-executed.ipynb",
        media_type="application/x-ipynb+json",
    )
    async def download_notebook_executed():
        notebook_py = make_notebook_py(
            csv_path="todo.csv",
            unit=1,
            loss=1,
            weights=[1],
        )
        notebook_nb = convert_py_to_nb(notebook_py, execute=True)
        yield notebook_nb
