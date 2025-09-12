import re
from typing import NamedTuple, Optional

from dp_wizard_templates.code_template import Template

from dp_wizard import opendp_version, registry_url
from dp_wizard.types import AnalysisName, ColumnName


class AnalysisPlanColumn(NamedTuple):
    analysis_name: AnalysisName
    lower_bound: float
    upper_bound: float
    bin_count: int
    weight: int


class AnalysisPlan(NamedTuple):
    """
    >>> plan = AnalysisPlan(
    ...     is_synthetic_data=False,
    ...     csv_path='optional.csv',
    ...     contributions=10,
    ...     epsilon=2.0,
    ...     max_rows=1000,
    ...     groups=['grouping_col'],
    ...     columns={
    ...         'data_col': [AnalysisPlanColumn('Histogram', 0, 100, 10, 1)]
    ...     })
    >>> print(plan)
    DP Statistics for `data_col`
    >>> print(plan.to_stem())
    dp_statistics_for_data_col
    """

    is_synthetic_data: bool
    csv_path: Optional[str]
    contributions: int
    epsilon: float
    max_rows: int
    groups: list[ColumnName]
    columns: dict[ColumnName, list[AnalysisPlanColumn]]

    def __str__(self):
        main = "DP Synthetic Data" if self.is_synthetic_data else "DP Statistics"

        columns = ", ".join(f"`{k}`" for k in self.columns.keys())
        return f"{main} for {columns}"

    def to_stem(self):
        return re.sub(r"\W+", " ", str(self)).strip().replace(" ", "_").lower()


# Public functions used to generate code snippets in the UI;
# These do not require an entire analysis plan, so they stand on their own.


def make_privacy_unit_block(contributions: int):
    import opendp.prelude as dp

    def template(CONTRIBUTIONS):
        contributions = CONTRIBUTIONS
        privacy_unit = dp.unit_of(contributions=contributions)  # noqa: F841

    return Template(template).fill_values(CONTRIBUTIONS=contributions).finish()


def make_pure_privacy_loss_block(epsilon: float, max_rows: int):
    """
    Comments in the generated code reference synthetic data generation (cuts dict),
    so don't use this in stats code!
    """
    # TODO: Clean up the copy-paste between these two functions,
    # Maybe add a "pure" boolean kwarg?
    import opendp.prelude as dp

    def template(EPSILON, MAX_ROWS):
        privacy_loss = dp.loss_of(  # noqa: F841
            # Your privacy budget is captured in the "epsilon" parameter.
            # Larger values increase the risk that personal data could be reconstructed,
            # so choose the smallest value that gives you the needed accuracy.
            # You can also compare your budget to other projects:
            # REGISTRY_URL
            epsilon=EPSILON,
            # If your columns did match your cuts dict,
            # you would also need to provide a very small "delta" value.
            # https://docs.opendp.org/en/OPENDP_VERSION/getting-started/tabular-data/grouping.html#Stable-Keys
            # delta=1 / max(1e7, MAX_ROWS),
        )

    return (
        Template(template)
        .fill_expressions(
            OPENDP_VERSION=opendp_version,
            REGISTRY_URL=registry_url,
        )
        .fill_values(
            EPSILON=epsilon,
            MAX_ROWS=max_rows,
        )
        .finish()
    )


def make_approx_privacy_loss_block(epsilon: float, max_rows: int):
    import opendp.prelude as dp

    def template(EPSILON, MAX_ROWS):
        privacy_loss = dp.loss_of(  # noqa: F841
            # Your privacy budget is captured in the "epsilon" parameter.
            # Larger values increase the risk that personal data could be reconstructed,
            # so choose the smallest value that gives you the needed accuracy.
            # You can also compare your budget to other projects:
            # REGISTRY_URL
            epsilon=EPSILON,
            # There are many models of differential privacy. For flexibility,
            # we are using a model which tolerates a small probability (delta)
            # that data may be released in the clear. Delta should always be small,
            # but if the dataset is particularly large,
            # delta should be at least as small as 1/(row count).
            # https://docs.opendp.org/en/OPENDP_VERSION/getting-started/tabular-data/grouping.html#Stable-Keys
            delta=1 / max(1e7, MAX_ROWS),
        )

    return (
        Template(template)
        .fill_expressions(
            OPENDP_VERSION=opendp_version,
            REGISTRY_URL=registry_url,
        )
        .fill_values(
            EPSILON=epsilon,
            MAX_ROWS=max_rows,
        )
        .finish()
    )


def make_column_config_block(
    name: str,
    analysis_name: AnalysisName,
    lower_bound: float,
    upper_bound: float,
    bin_count: int,
):
    from dp_wizard.utils.code_generators.analyses import get_analysis_by_name

    return get_analysis_by_name(analysis_name).make_column_config_block(
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
