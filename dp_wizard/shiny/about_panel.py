import sys
from pathlib import Path
import subprocess
import urllib.parse

from htmltools import tags, HTML
from shiny import ui, reactive, Inputs, Outputs, Session

from dp_wizard.shiny.components.outputs import nav_button


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
    >>> query = urllib.parse.urlparse(_make_issue_url(info)).query
    >>> print(urllib.parse.unquote_plus(query))
    body=Please describe the problem.
    <BLANKLINE>
    <details>
    The information below will help us reproduce the issue.
    <BLANKLINE>
    ```
    A B C
    ```
    <BLANKLINE>
    </details>
    """
    markdown = f"""Please describe the problem.

<details>
The information below will help us reproduce the issue.

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
                DP Wizard guides you through the application of
                differential privacy. After selecting a local CSV,
                you'll be prompted to describe the analysis you need.
                Output options include:
                - A Jupyter notebook which demonstrates how to use
                the [OpenDP Library](https://docs.opendp.org/).
                - A plain Python script.
                - Text and CSV reports.
                """
            ),
            ui.accordion(
                ui.accordion_panel(
                    "File an Issue",
                    tags.div(
                        tags.textarea(
                            info,
                            readonly=True,
                            rows=10,
                            columns=60,
                            style="font-family: monospace;",
                        ),
                        ui.a(
                            "File issue",
                            href=issue_url,
                            target="_blank",
                            class_="btn btn-default",
                            style="width: 10em;",
                        ),
                        class_="bslib-gap-spacing html-fill-container",
                    ),
                ),
                ui.accordion_panel(
                    "Give Feedback",
                    ui.div(
                        HTML(
                            # Responses to this survey are at:
                            # https://docs.google.com/forms/d/1l7-RK1R1nRuhHr8pTck1D4RU8Bi6Ehr124bkYvH-96c/edit
                            """
                            <iframe
                                src="https://docs.google.com/forms/d/e/1FAIpQLScaGdKS-vj-RrM7SCV_lAwZmxQ2bOqFrAkyDp4djxTqkTkinA/viewform?embedded=true"
                                id="feedback-iframe"
                                width="640"
                                height="1003"
                                frameborder="0"
                                marginheight="0"
                                marginwidth="0"
                            >Loading…</iframe>
                            """
                        ),
                    ),
                ),
                open=False,
            ),
        ),
        nav_button("go_to_dataset", "Select dataset"),
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
