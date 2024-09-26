from shiny import App, ui, reactive, render

from dp_creator_ii import get_arg_parser
from dp_creator_ii.template import make_notebook_py, make_script_py
from dp_creator_ii.converters import convert_py_to_nb


def dataset_panel():
    return ui.nav_panel(
        "Select Dataset",
        "TODO: Pick dataset",
        ui.output_text("csv_path_text"),
        ui.output_text("unit_of_privacy_text"),
        ui.input_action_button("go_to_analysis", "Perform analysis"),
        value="dataset_panel",
    )


def analysis_panel():
    return ui.nav_panel(
        "Perform Analysis",
        "TODO: Define analysis",
        ui.input_action_button("go_to_results", "Download results"),
        value="analysis_panel",
    )


def results_panel():
    return ui.nav_panel(
        "Download Results",
        "TODO: Download Results",
        ui.download_button("download_script", "Download script"),
        # TODO: Notebook code is badly formatted
        # ui.download_button(
        #     "download_notebook_unexecuted", "Download notebook (unexecuted)"
        # ),
        # ui.download_button(
        #     "download_notebook_executed", "Download notebook (executed)"
        # )
        value="results_panel",
    )


app_ui = ui.page_bootstrap(
    ui.navset_tab(
        dataset_panel(),
        analysis_panel(),
        results_panel(),
        id="top_level_nav",
    ),
    title="DP Creator II",
)


def server(input, output, session):
    args = get_arg_parser().parse_args()

    csv_path = reactive.value(args.csv_path)
    unit_of_privacy = reactive.value(args.unit_of_privacy)

    @render.text
    def csv_path_text():
        return str(csv_path.get())

    @render.text
    def unit_of_privacy_text():
        return str(unit_of_privacy.get())

    @reactive.effect
    @reactive.event(input.go_to_analysis)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="analysis_panel")

    @reactive.effect
    @reactive.event(input.go_to_results)
    def go_to_results():
        ui.update_navs("top_level_nav", selected="results_panel")

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


app = App(app_ui, server)
