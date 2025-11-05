import re
from typing import NamedTuple

from faicons import icon_svg
from shiny import ui


class DownloadOption(NamedTuple):
    name: str
    ext: str
    icon: str
    description_md: str

    @property
    def clean_description_md(self) -> str:
        return re.sub(r"\s+", " ", self.description_md.strip())  # pragma: no cover


_download_options = {
    option.name: option
    # Find more icons on Font Awesome: https://fontawesome.com/search?ic=free
    for option in [
        DownloadOption(
            "README",
            ".txt",
            "file",
            "A short description of the analysis, and a table of contents.",
        ),
        DownloadOption(
            "Package",
            ".zip",
            "folder-open",
            "A zip file with results and code for a reproducible analysis.",
        ),
        DownloadOption(
            "Notebook",
            ".ipynb",
            "book",
            """
            An executed Jupyter notebook which references your CSV
            and shows the result of a differentially private analysis.
            """,
        ),
        DownloadOption(
            "HTML",
            ".html",
            "file-code",
            "The same content, but exported as HTML.",
        ),
        DownloadOption(
            "Report",
            ".txt",
            "file-lines",
            """
            A report which includes your parameter choices and the results.
            Intended to be human-readable, but it does use YAML,
            so it can be parsed by other programs.
            """,
        ),
        DownloadOption(
            "Table",
            ".csv",
            "file-csv",
            "The same information, but condensed into a CSV.",
        ),
        DownloadOption(
            "Notebook (unexecuted)",
            ".ipynb",
            "book",
            """
            An unexecuted Jupyter notebook which shows the steps
            in a differentially private analysis.
            It can also be updated with the path
            to a private CSV and executed locally.
            """,
        ),
        DownloadOption(
            "HTML (unexecuted)",
            ".html",
            "file-code",
            "The same content, but exported as HTML.",
        ),
        DownloadOption(
            "Script",
            ".py",
            "python",
            """
            The same code as the notebooks, but extracted into
            a Python script which can be run from the command line.
            """,
        ),
        DownloadOption(
            "Notebook Source",
            ".py",
            "python",
            """
            Python source code converted by jupytext into notebook.
            Primarily of interest to DP Wizard developers.
            """,
        ),
    ]
}


def table_of_contents_md():
    """
    >>> print(table_of_contents_md())
    - README (.txt): A short description of the analysis, and a table of contents.
    ...
    - Table (.csv): The same information, but condensed into a CSV.
    """
    included_names = ["README", "Notebook", "HTML", "Script", "Report", "Table"]
    included_options = [_download_options[name] for name in included_names]
    return "\n".join(
        f"- {opt.name} ({opt.ext}): {opt.clean_description_md}"
        for opt in included_options
    )


def download_button(
    opt_name: str,
    primary=False,
    disabled=False,
):  # pragma: no cover
    return _download_button_or_link(
        opt_name,
        primary=primary,
        disabled=disabled,
        button=True,
    )


def download_link(
    opt_name: str,
    primary=False,
    disabled=False,
):  # pragma: no cover
    return _download_button_or_link(
        opt_name,
        primary=primary,
        disabled=disabled,
        button=False,
    )


def _download_button_or_link(
    opt_name: str,
    primary: bool,
    disabled: bool,
    button: bool,
):  # pragma: no cover
    opt = _download_options[opt_name]
    clean_name = re.sub(r"\W+", " ", opt.name).strip().replace(" ", "_").lower()
    kwargs = {
        "id": f"download_{clean_name}_{'button' if button else 'link'}",
        "label": f"{'Download ' if button else ''}{opt.name} ({opt.ext})",
        "icon": icon_svg(opt.icon, margin_right="0.5em"),
        "width": "22em",
        "class_": "btn-primary" if primary else None,
    }
    if disabled:
        # Would prefer just to use ui.download_button,
        # but it doesn't have a "disabled" option.
        ui_button_or_link = ui.input_action_button if button else ui.input_action_link
        kwargs["disabled"] = True
    else:
        ui_button_or_link = ui.download_button if button else ui.download_link
    return [
        ui_button_or_link(**kwargs),
        ui.markdown(opt.description_md),
    ]
