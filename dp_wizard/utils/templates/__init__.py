"""
Strings of ALL CAPS are replaced in these templates.
Keeping them in a format which can actually be parsed as python
makes some things easier, but it is also reinventing the wheel.
We may revisit this.
"""

from pathlib import Path
import re
from dp_wizard.utils.csv_helper import name_to_identifier


class _Template:
    def __init__(self, path, template=None):
        if path is not None:
            self._path = f"_{path}.py"
            template_path = Path(__file__).parent / "no-tests" / self._path
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


def _make_margins_dict(bin_names):
    # TODO: Don't worry too much about the formatting here.
    # Plan to run the output through black for consistency.
    # https://github.com/opendp/dp-creator-ii/issues/50
    margins = (
        [
            """
        (): dp.polars.Margin(
            public_info="lengths",
        ),"""
        ]
        + [
            f"""
        ("{bin_name}",): dp.polars.Margin(
            public_info="keys",
        ),"""
            for bin_name in bin_names
        ]
    )

    margins_dict = "{" + "".join(margins) + "\n    }"
    return margins_dict


def _make_context_for_notebook(csv_path, contributions, epsilon, weights, column_names):
    privacy_unit_block = make_privacy_unit_block(contributions)
    privacy_loss_block = make_privacy_loss_block(epsilon)
    margins_dict = _make_margins_dict([f"{name}_bin" for name in column_names])
    columns = ", ".join([f"{name}_config" for name in column_names])
    return str(
        _Template("context")
        .fill_expressions(
            MARGINS_DICT=margins_dict,
            COLUMNS=columns,
        )
        .fill_values(
            CSV_PATH=csv_path,
            WEIGHTS=weights,
        )
        .fill_blocks(
            PRIVACY_UNIT_BLOCK=privacy_unit_block,
            PRIVACY_LOSS_BLOCK=privacy_loss_block,
        )
    )


def _make_context_for_script(contributions, epsilon, weights, column_names):
    privacy_unit_block = make_privacy_unit_block(contributions)
    privacy_loss_block = make_privacy_loss_block(epsilon)
    margins_dict = _make_margins_dict([f"{name}_bin" for name in column_names])
    columns = ",".join([f"{name}_config" for name in column_names])
    return str(
        _Template("context")
        .fill_expressions(
            CSV_PATH="csv_path",
            MARGINS_DICT=margins_dict,
            COLUMNS=columns,
        )
        .fill_values(
            WEIGHTS=weights,
        )
        .fill_blocks(
            PRIVACY_UNIT_BLOCK=privacy_unit_block,
            PRIVACY_LOSS_BLOCK=privacy_loss_block,
            MARGINS_DICT=margins_dict,
        )
    )


def _make_imports():
    return (
        str(_Template("imports").fill_values())
        + (Path(__file__).parent.parent / "shared.py").read_text()
    )


def _make_columns(columns):
    return "\n".join(
        make_column_config_block(
            name=name,
            lower_bound=col["lower_bound"],
            upper_bound=col["upper_bound"],
            bin_count=col["bin_count"],
        )
        for name, col in columns.items()
    )


def _make_query(column_name):
    indentifier = name_to_identifier(column_name)
    return str(
        _Template("query")
        .fill_values(
            BIN_NAME=f"{indentifier}_bin",
        )
        .fill_expressions(
            QUERY_NAME=f"{indentifier}_query",
            ACCURACY_NAME=f"{indentifier}_accuracy",
            HISTOGRAM_NAME=f"{indentifier}_histogram",
        )
    )


def _make_queries(column_names):
    return "confidence = 0.95\n\n" + "\n".join(
        _make_query(column_name) for column_name in column_names
    )


def make_notebook_py(csv_path, contributions, epsilon, columns):
    return str(
        _Template("notebook").fill_blocks(
            IMPORTS_BLOCK=_make_imports(),
            COLUMNS_BLOCK=_make_columns(columns),
            CONTEXT_BLOCK=_make_context_for_notebook(
                csv_path=csv_path,
                contributions=contributions,
                epsilon=epsilon,
                weights=[column["weight"] for column in columns.values()],
                column_names=[name_to_identifier(name) for name in columns.keys()],
            ),
            QUERIES_BLOCK=_make_queries(columns.keys()),
        )
    )


def make_script_py(contributions, epsilon, columns):
    return str(
        _Template("script").fill_blocks(
            IMPORTS_BLOCK=_make_imports(),
            COLUMNS_BLOCK=_make_columns(columns),
            CONTEXT_BLOCK=_make_context_for_script(
                # csv_path is a CLI parameter in the script
                contributions=contributions,
                epsilon=epsilon,
                weights=[column["weight"] for column in columns.values()],
                column_names=[name_to_identifier(name) for name in columns.keys()],
            ),
            QUERIES_BLOCK=_make_queries(columns.keys()),
        )
    )


def make_privacy_unit_block(contributions):
    return str(_Template("privacy_unit").fill_values(CONTRIBUTIONS=contributions))


def make_privacy_loss_block(epsilon):
    return str(_Template("privacy_loss").fill_values(EPSILON=epsilon))


def make_column_config_block(name, lower_bound, upper_bound, bin_count):
    """
    >>> print(make_column_config_block(
    ...     name="HW GRADE",
    ...     lower_bound=0,
    ...     upper_bound=100,
    ...     bin_count=10
    ... ))
    # From the public information, determine the bins for 'HW GRADE':
    hw_grade_cut_points = make_cut_points(
        lower_bound=0,
        upper_bound=100,
        bin_count=10,
    )
    <BLANKLINE>
    # Use these bins to define a Polars column:
    hw_grade_config = (
        pl.col('HW GRADE')
        .cut(hw_grade_cut_points)
        .alias('hw_grade_bin')  # Give the new column a name.
        .cast(pl.String)
    )
    <BLANKLINE>
    """
    snake_name = _snake_case(name)
    return str(
        _Template("column_config")
        .fill_expressions(
            CUT_LIST_NAME=f"{snake_name}_cut_points",
            POLARS_CONFIG_NAME=f"{snake_name}_config",
        )
        .fill_values(
            LOWER_BOUND=lower_bound,
            UPPER_BOUND=upper_bound,
            BIN_COUNT=bin_count,
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
