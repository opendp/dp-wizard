import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

import opendp.prelude as dp
import pytest
import requests
from dp_wizard_templates.converters import convert_nb_to_html, convert_py_to_nb

from dp_wizard import opendp_version
from dp_wizard.types import AnalysisName, ColumnName, Product
from dp_wizard.utils.code_generators import (
    AnalysisPlan,
    AnalysisPlanColumn,
    make_column_config_block,
)
from dp_wizard.utils.code_generators.analyses import count, histogram, mean, median
from dp_wizard.utils.code_generators.notebook_generator import NotebookGenerator
from dp_wizard.utils.code_generators.script_generator import ScriptGenerator

python_paths = Path(__file__).parent.parent.parent.glob("dp_wizard/**/*.py")


@pytest.mark.parametrize("python_path", python_paths, ids=lambda path: path.name)
def test_no_unparameterized_docs_urls(python_path: Path):
    python_code = python_path.read_text()
    assert not re.search(r"docs\.opendp\.org/en/[^O{]", python_code)


def test_make_column_config_block_for_unrecognized():
    with pytest.raises(Exception, match=r"Unrecognized analysis"):
        make_column_config_block(
            name="HW GRADE",
            analysis_name=AnalysisName("Bad AnalysisType!"),
            lower_bound=0,
            upper_bound=100,
            bin_count=10,
        )


def test_make_column_config_block_for_count():
    assert (
        make_column_config_block(
            name="HW GRADE",
            analysis_name=count.name,
            lower_bound=0,
            upper_bound=0,
            bin_count=0,
        ).strip()
        == f"""# See the OpenDP docs for more on making private counts:
# https://docs.opendp.org/en/v{opendp_version}/getting-started/tabular-data/essential-statistics.html#Count

hw_grade_expr = pl.col('HW GRADE').cast(float).dp.count().alias("count")"""
    )


def test_make_column_config_block_for_mean():
    assert (
        make_column_config_block(
            name="HW GRADE",
            analysis_name=mean.name,
            lower_bound=0,
            upper_bound=100,
            bin_count=10,
        ).strip()
        == f"""# See the OpenDP Library docs for more on making private means:
# https://docs.opendp.org/en/v{opendp_version}/getting-started/tabular-data/essential-statistics.html#Mean

hw_grade_expr = pl.col('HW GRADE').cast(float).dp.mean((0, 100))"""
    )


def test_make_column_config_block_for_median():
    assert (
        make_column_config_block(
            name="HW GRADE",
            analysis_name=median.name,
            lower_bound=0,
            upper_bound=100,
            bin_count=20,
        ).strip()
        == f"""# See the OpenDP Library docs for more on making private medians and quantiles:
# https://docs.opendp.org/en/v{opendp_version}/getting-started/tabular-data/essential-statistics.html#Median

hw_grade_expr = (
    pl.col('HW GRADE')
    .cast(float)
    .dp.quantile(0.5, make_cut_points(0, 100, bin_count=20))
    # Or use "dp.median" which provides 0.5 implicitly.
)"""  # noqa: B950 (too long!)
    )


def test_make_column_config_block_for_histogram():
    assert (
        make_column_config_block(
            name="HW GRADE",
            analysis_name=histogram.name,
            lower_bound=0,
            upper_bound=100,
            bin_count=10,
        ).strip()
        == f"""# See the OpenDP Library docs for more on making private histograms:
# https://docs.opendp.org/en/v{opendp_version}/getting-started/examples/histograms.html

# Use the public information to make cut points for 'HW GRADE':
hw_grade_cut_points = make_cut_points(
    lower_bound=0,
    upper_bound=100,
    bin_count=10,
)

# Use these cut points to add a new binned column to the table:
hw_grade_bin_expr = (
    pl.col('HW GRADE')
    .cut(hw_grade_cut_points)  # Use "left_closed=True" to switch endpoint inclusion.
    .alias('hw_grade_bin')  # Give the new column a name.
    .cast(pl.String)
)"""
    )


abc_csv = "tests/fixtures/abc.csv"


def number_lines(text: str):
    return "\n".join(
        f"# {i}:\n{line}" if line and not i % 10 else line
        for (i, line) in enumerate(text.splitlines())
    )


histogram_plan_column = AnalysisPlanColumn(
    analysis_name=histogram.name,
    lower_bound=5,
    upper_bound=15,
    bin_count=20,
    weight=4,
)
mean_plan_column = AnalysisPlanColumn(
    analysis_name=mean.name,
    lower_bound=5,
    upper_bound=15,
    bin_count=0,  # Unused
    weight=4,
)
median_plan_column = AnalysisPlanColumn(
    analysis_name=median.name,
    lower_bound=5,
    upper_bound=15,
    bin_count=10,
    weight=4,
)
count_plan_column = AnalysisPlanColumn(
    analysis_name=count.name,
    lower_bound=0,  # Unused
    upper_bound=0,  # Unused
    bin_count=0,  # Unused
    weight=4,
)


def id_for_plan(plan: AnalysisPlan):
    columns = ", ".join(f"{v[0].analysis_name} of {k}" for k, v in plan.columns.items())
    description = (
        f"{plan.product} for {columns}; "
        f"grouped by ({', '.join(plan.groups) or 'nothing'})"
    )
    return re.sub(r"\W+", "_", description)  # For selection with "pytest -k substring"


plans = [
    AnalysisPlan(
        product=product,
        groups=groups,
        columns=columns,
        contributions=contributions,
        contributions_entity="Family",
        csv_path=abc_csv,
        epsilon=1,
        max_rows=100_000,
    )
    for product in Product
    for contributions in [1, 10]
    for groups in [[], ["A"]]
    for columns in [
        # Single:
        {ColumnName("B"): [histogram_plan_column]},
        {ColumnName("B"): [mean_plan_column]},
        {ColumnName("B"): [median_plan_column]},
        {ColumnName("B"): [count_plan_column]},
        # Multiple:
        {
            ColumnName("B"): [histogram_plan_column],
            ColumnName("C"): [mean_plan_column],
            ColumnName("D"): [median_plan_column],
            ColumnName("E"): [count_plan_column],
        },
    ]
]


expected_urls = [
    "https://docs.opendp.org/",
    "https://github.com/opendp/dp-wizard",
    "https://docs.opendp.org/en/v0.14.1/api/python/opendp.extras.mbi.html#opendp.extras.mbi.ContingencyTable.synthesize",
    "https://docs.opendp.org/en/v0.14.1/api/python/opendp.extras.mbi.html#opendp.extras.mbi.ContingencyTable.project_melted",
]


@pytest.mark.parametrize("url", [url.split("#")[0] for url in expected_urls])
def test_urls_work(url):
    # TODO: Check if anchors are present.
    # https://github.com/opendp/dp-wizard/issues/627
    response = requests.head(url)
    assert response.status_code == 200


@pytest.mark.parametrize("plan", plans, ids=id_for_plan)
def test_make_notebook(plan):
    notebook_py = NotebookGenerator(plan).make_py()
    print(number_lines(notebook_py))
    globals = {}
    exec(notebook_py, globals)

    # Close plots to avoid this warning:
    # > RuntimeWarning: More than 20 figures have been opened.
    # > Figures created through the pyplot interface (`matplotlib.pyplot.figure`)
    # > are retained until explicitly closed and may consume too much memory.
    import matplotlib.pyplot as plt

    plt.close("all")

    match plan.product:
        case Product.SYNTHETIC_DATA:
            context_global = "synth_context"
        case Product.STATISTICS:
            context_global = "stats_context"
        case _:  # pragma: no cover
            raise ValueError(plan.product)
    assert isinstance(globals[context_global], dp.Context)

    notebook_nb = convert_py_to_nb(notebook_py, "Title placeholder")
    notebook_html = convert_nb_to_html(notebook_nb)
    # Parsing HTML with an RE is usually not the right solution,
    # but since these are generated from the markdown,
    # BeautifulSoup seems like overkill.
    urls = set(re.findall(r'<a[^>]+href="(http[^"]+)[^>]+>', notebook_html))
    assert urls <= set(expected_urls)


@pytest.mark.parametrize("plan", plans, ids=id_for_plan)
def test_make_script(plan):
    script = ScriptGenerator(plan).make_py()

    # Make sure jupytext formatting doesn't bleed into the script.
    # https://jupytext.readthedocs.io/en/latest/formats-scripts.html#the-light-format
    assert "# -" not in script
    assert "# +" not in script

    with NamedTemporaryFile(mode="w") as fp:
        fp.write(script)
        fp.flush()

        result = subprocess.run(
            ["python", fp.name, "--csv", abc_csv], capture_output=True
        )
        assert result.returncode == 0
