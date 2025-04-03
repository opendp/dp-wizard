import sys
from pathlib import Path
import subprocess
import urllib.parse

from htmltools import tags
from shiny import ui, reactive, Inputs, Outputs, Session


def _run(cmd):
    """
    >>> _run("echo hello")
    '    hello'
    """
    # Do not check exit status:
    # If there is a problem, we don't want to worry about it.
    return "\n".join(
        f"    {line}"
        for line in subprocess.run(cmd.split(" "), capture_output=True)
        .stdout.decode()
        .splitlines()
    )


def _get_info():
    version = (Path(__file__).parent.parent / "VERSION").read_text().strip()
    git_status = _run("git status")
    pip_freeze = _run("pip freeze")
    return f"""
DP Wizard v{version}
python: {sys.version}
arguments: {' '.join(sys.argv[1:])}
git status:
{git_status}
pip freeze:
{pip_freeze}
    """


def _make_issue_url(info):
    """
    >>> info = 'A B C'
    >>> print(urllib.parse.unquote_plus(_make_issue_url(info)[-70:]))
    <details>
    <BLANKLINE>
    ```
    A B C
    ```
    <BLANKLINE>
    </details>
    """
    markdown = f"""Please describe the problem.

<details>

```
{info}
```

</details>"""
    encoded = urllib.parse.quote_plus(markdown)
    return f"https://github.com/opendp/dp-wizard/issues/new?body={encoded}"


def about_ui():
    info = _get_info()
    issue_url = _make_issue_url(info)

    return ui.nav_panel(
        "About",
        ui.card(
            ui.card_header("About DP Wizard"),
            ui.markdown(
                """
                DP Wizard guides the user through the application of
                differential privacy. After selecting a local CSV,
                users are prompted to describe the analysis they need.
                Output options include:
                - A Jupyter notebook which demonstrates how to use
                [OpenDP](https://docs.opendp.org/).
                - A plain Python script.
                - Text and CSV reports.
                """
            ),
            tags.textarea(
                info,
                readonly=True,
                rows=10,
                style="font-family: monospace;",
            ),
            ui.a(
                "File issue",
                href=issue_url,
                target="_blank",
                class_="btn btn-default action-button",
                style="width: 10em;",
            ),
        ),
        ui.input_action_button("go_to_dataset", "Select dataset"),
        value="about_panel",
    )


def about_server(
    input: Inputs,
    output: Outputs,
    session: Session,
):  # pragma: no cover
    @reactive.effect
    @reactive.event(input.go_to_dataset)
    def go_to_analysis():
        ui.update_navs("top_level_nav", selected="dataset_panel")
