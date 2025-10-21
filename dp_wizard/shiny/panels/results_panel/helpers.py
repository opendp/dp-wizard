import re

from faicons import icon_svg
from shiny import types, ui

wait_message = "Please wait."


def button(
    name: str, ext: str, icon: str, primary=False, disabled=False
):  # pragma: no cover
    clean_name = re.sub(r"\W+", " ", name).strip().replace(" ", "_").lower()
    kwargs = {
        "id": f"download_{clean_name}",
        "label": f"Download {name} ({ext})",
        "icon": icon_svg(icon, margin_right="0.5em"),
        "width": "20em",
        "class_": "btn-primary" if primary else None,
    }
    if disabled:
        # Would prefer just to use ui.download_button,
        # but it doesn't have a "disabled" option.
        return ui.input_action_button(
            disabled=True,
            **kwargs,
        )
    return ui.download_button(**kwargs)


def _strip_ansi(e) -> str:
    """
    >>> e = Exception('\x1b[0;31mValueError\x1b[0m: ...')
    >>> _strip_ansi(e)
    'ValueError: ...'
    """
    # From https://stackoverflow.com/a/14693789
    import re

    return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", str(e))


def make_download_or_modal_error(download_generator):  # pragma: no cover
    try:
        with ui.Progress() as progress:
            progress.set(message=wait_message)
            return download_generator()
    except Exception as e:
        message = _strip_ansi(e)
        modal = ui.modal(
            ui.pre(message),
            title="Error generating code",
            size="xl",
            easy_close=True,
        )
        ui.modal_show(modal)
        raise types.SilentException("code generation")
