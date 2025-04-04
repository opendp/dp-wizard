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


def _make_issue_body(info):
    return f"""Please describe the problem.

<details>

```
{info}
```

</details>"""


def about_ui():
    info = _get_info()

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
            # Textarea just for display: Not actually part of form.
            tags.textarea(
                info,
                readonly=True,
                rows=10,
                style="font-family: monospace;",
            ),
            tags.form(
                # Hidden input with markdown wrapping the same info:
                tags.input(
                    name="body",
                    value=_make_issue_body(info),
                    type="hidden",
                ),
                tags.input(
                    value="Report Issue",
                    type="submit",
                    class_="btn btn-default action-button",
                    id="issue-submit",
                ),
                method="get",
                action="https://github.com/opendp/dp-wizard/issues/new",
                target="_blank",
                id="issue-form",
            ),
            # Shiny captures form events by default.
            # JS suggested by https://github.com/posit-dev/py-shiny/issues/1770
            tags.script(
                """
                document.getElementById('issue-submit').addEventListener('click', function(event) {
                    document.getElementById('issue-form').submit();
                });
            """
            ),
        ),
        ui.input_action_button("go_to_dataset", "Select Dataset"),
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
