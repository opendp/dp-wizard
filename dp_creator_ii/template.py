from pathlib import Path
import re


class _Template:
    def __init__(self, path, template=None):
        if path is not None:
            self._path = path
            template_path = Path(__file__).parent / "templates" / path
            self._template = template_path.read_text()
        if template is not None:
            if path is not None:  # pragma: no cover
                raise Exception('"path" and "template" are mutually exclusive')
            self._path = "template-instead-of-path"
            self._template = template

    def fill_expressions(self, **kwargs):
        for k, v in kwargs.items():
            self._template = self._template.replace(k, v)
        return self

    def fill_values(self, **kwargs):
        for k, v in kwargs.items():
            self._template = self._template.replace(k, repr(v))
        return self

    def fill_blocks(self, **kwargs):
        for k, v in kwargs.items():

            def match_indent(match):
                # This does what we want, but binding is confusing.
                return "\n".join(
                    match.group(1) + line for line in v.split("\n")  # noqa: B023
                )

            k_re = re.escape(k)
            self._template = re.sub(
                rf"^([ \t]*){k_re}$",
                match_indent,
                self._template,
                flags=re.MULTILINE,
            )
        return self

    def __str__(self):
        # Slots:
        # - are all caps or underscores
        # - have word boundary on either side
        # - are at least three characters
        slot_re = r"\b[A-Z][A-Z_]{2,}\b"
        unfilled = set(re.findall(slot_re, self._template))
        if unfilled:
            raise Exception(
                f"Template {self._path} has unfilled slots: "
                f'{", ".join(sorted(unfilled))}\n\n{self._template}'
            )
        return self._template


def _make_context_for_notebook(csv_path, contributions, loss, weights):
    privacy_unit_block = make_privacy_unit_block(contributions)
    return str(
        _Template("context.py")
        .fill_values(
            CSV_PATH=csv_path,
            LOSS=loss,
            WEIGHTS=weights,
        )
        .fill_blocks(
            PRIVACY_UNIT_BLOCK=privacy_unit_block,
        )
    )


def _make_context_for_script(contributions, loss, weights):
    privacy_unit_block = make_privacy_unit_block(contributions)
    return str(
        _Template("context.py")
        .fill_expressions(
            CSV_PATH="csv_path",
        )
        .fill_values(
            LOSS=loss,
            WEIGHTS=weights,
        )
        .fill_blocks(
            PRIVACY_UNIT_BLOCK=privacy_unit_block,
        )
    )


def _make_imports():
    return str(_Template("imports.py").fill_values())


def make_notebook_py(csv_path, contributions, loss, weights):
    return str(
        _Template("notebook.py").fill_blocks(
            IMPORTS_BLOCK=_make_imports(),
            CONTEXT_BLOCK=_make_context_for_notebook(
                csv_path=csv_path,
                contributions=contributions,
                loss=loss,
                weights=weights,
            ),
        )
    )


def make_script_py(contributions, loss, weights):
    return str(
        _Template("script.py").fill_blocks(
            IMPORTS_BLOCK=_make_imports(),
            CONTEXT_BLOCK=_make_context_for_script(
                contributions=contributions,
                loss=loss,
                weights=weights,
            ),
        )
    )


def make_privacy_unit_block(contributions):
    return str(_Template("privacy_unit.py").fill_values(CONTRIBUTIONS=contributions))
