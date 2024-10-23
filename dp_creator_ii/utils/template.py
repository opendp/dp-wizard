from pathlib import Path
import re


class _Template:
    def __init__(self, path, template=None):
        if path is not None:
            self._path = path
            template_path = Path(__file__).parent / "templates" / path
            self._template = template_path.read_text()
        if template is not None:
            if path is not None:
                raise Exception('"path" and "template" are mutually exclusive')
            self._path = "template-instead-of-path"
            self._template = template
        self._initial_slots = self._find_slots()

    def _find_slots(self):
        # Slots:
        # - are all caps or underscores
        # - have word boundary on either side
        # - are at least three characters
        slot_re = r"\b[A-Z][A-Z_]{2,}\b"
        return set(re.findall(slot_re, self._template))

    def fill_expressions(self, **kwargs):
        for k, v in kwargs.items():
            k_re = re.escape(k)
            self._template = re.sub(rf"\b{k_re}\b", str(v), self._template)
        return self

    def fill_values(self, **kwargs):
        for k, v in kwargs.items():
            k_re = re.escape(k)
            self._template = re.sub(rf"\b{k_re}\b", repr(v), self._template)
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
        unfilled_slots = self._initial_slots & self._find_slots()
        if unfilled_slots:
            raise Exception(
                f"Template {self._path} has unfilled slots: "
                f'{", ".join(sorted(unfilled_slots))}\n\n{self._template}'
            )
        return self._template


def _make_context_for_notebook(csv_path, contributions, loss, weights):
    privacy_unit_block = make_privacy_unit_block(contributions)
    return str(
        _Template("_context.py")
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
        _Template("_context.py")
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
    return str(_Template("_imports.py").fill_values())


def make_notebook_py(csv_path, contributions, loss, weights):
    return str(
        _Template("_notebook.py").fill_blocks(
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
        _Template("_script.py").fill_blocks(
            IMPORTS_BLOCK=_make_imports(),
            CONTEXT_BLOCK=_make_context_for_script(
                contributions=contributions,
                loss=loss,
                weights=weights,
            ),
        )
    )


def make_privacy_unit_block(contributions):
    return str(_Template("_privacy_unit.py").fill_values(CONTRIBUTIONS=contributions))


def make_column_config_block(name, min_value, max_value, bin_count):
    """
    >>> print(make_column_config_block(
    ...     name="HW GRADE",
    ...     min_value=0,
    ...     max_value=100,
    ...     bin_count=10
    ... ))
    # From the public information, determine the bins:
    hw_grade_bins_list = list(
        range(
            0,
            100,
            int((100 - 0 + 1) / 10),
        )
    )
    <BLANKLINE>
    # Use these bins to define a Polars column:
    hw_grade_config = (
        pl.col('HW GRADE')
        .cut(hw_grade_bins_list)
        .alias('hw_grade_bin')  # Give the new column a name.
        .cast(pl.String)
    )
    <BLANKLINE>
    """
    snake_name = _snake_case(name)
    return str(
        _Template("_column_config.py")
        .fill_expressions(
            BINS_LIST_NAME=f"{snake_name}_bins_list",
            POLARS_CONFIG_NAME=f"{snake_name}_config",
        )
        .fill_values(
            MIN=min_value,
            MAX=max_value,
            BINS=bin_count,
            COLUMN_NAME=name,
            BIN_COLUMN_NAME=f"{snake_name}_bin",
        )
    )


def _snake_case(name: str):
    """
    >>> _snake_case("HW GRADE")
    'hw_grade'
    """
    return re.sub(r"\W+", "_", name.lower())
