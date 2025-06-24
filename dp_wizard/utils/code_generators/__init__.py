from typing import NamedTuple, Optional
import re


from dp_wizard.utils.code_template import Template


class AnalysisPlanColumn(NamedTuple):
    analysis_type: str
    lower_bound: float
    upper_bound: float
    bin_count: int
    weight: int


class AnalysisPlan(NamedTuple):
    csv_path: Optional[str]
    contributions: int
    epsilon: float
    groups: list[str]
    columns: dict[str, list[AnalysisPlanColumn]]

    def __str__(self):
        return ", ".join(f"{k} {v[0].analysis_type}" for k, v in self.columns.items())


# Public functions used to generate code snippets in the UI;
# These do not require an entire analysis plan, so they stand on their own.


def make_privacy_unit_block(contributions: int):
    return (
        Template("privacy_unit", __file__)
        .fill_values(CONTRIBUTIONS=contributions)
        .finish()
    )


def make_privacy_loss_block(epsilon: float):
    return Template("privacy_loss", __file__).fill_values(EPSILON=epsilon).finish()


def make_column_config_block(
    name: str,
    analysis_type: str,
    lower_bound: float,
    upper_bound: float,
    bin_count: int,
):
    from dp_wizard.utils.code_generators.analyses import get_analysis_by_name

    return get_analysis_by_name(analysis_type).make_column_config_block(
        column_name=name,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        bin_count=bin_count,
    )


def snake_case(name: str):
    """
    >>> snake_case("HW GRADE")
    'hw_grade'
    >>> snake_case("123")
    '_123'
    """
    snake = re.sub(r"\W+", "_", name.lower())
    # TODO: More validation in UI so we don't get zero-length strings.
    if snake == "" or not re.match(r"[a-z]", snake[0]):
        snake = f"_{snake}"
    return snake
