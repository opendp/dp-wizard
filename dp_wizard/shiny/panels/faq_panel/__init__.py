import subprocess
import sys
import urllib.parse

from htmltools import tags
from shiny import Inputs, Outputs, Session, reactive, ui

from dp_wizard import __version__, package_root
from dp_wizard.shiny.components.outputs import nav_button


def _run(cmd) -> str:
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


def _get_info() -> str:
    git_status = _run("git status")
    pip_freeze = _run("pip freeze")
    return f"""
DP Wizard v{__version__}
python: {sys.version}
arguments: {' '.join(sys.argv[1:])}
git status:
{git_status}
pip freeze:
{pip_freeze}
    """


def _make_issue_url(info) -> str:
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
        "FAQ",
        ui.card(
            ui.markdown((package_root / "FAQ.md").read_text())
            + "If you are on Github, the form below captures environment information "
            "and pre-fills a Github issue:",
            ui.accordion(
                ui.accordion_panel(
                    "Pre-fill Issue",
                    tags.div(
                        tags.textarea(
                            info,
                            readonly=True,
                            rows=10,
                            columns=60,
                            style="font-family: monospace;",
                        ),
                        ui.a(
                            "Pre-fill Issue",
                            href=issue_url,
                            target="_blank",
                            class_="btn btn-default",
                            style="width: 10em;",
                        ),
                        class_="bslib-gap-spacing html-fill-container",
                    ),
                ),
                open=False,
            ),
        ),
        nav_button("go_to_dataset", "Select Dataset"),
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
