import polars as pl

from dp_wizard import package_root
from dp_wizard.types import ColumnName, Product
from dp_wizard.utils.code_generators import AnalysisPlan, AnalysisPlanColumn
from dp_wizard.utils.code_generators.analyses import histogram
from dp_wizard.utils.code_generators.notebook_generator import NotebookGenerator


def strip_doc_test(block: str) -> str:
    """
    >>> print(strip_doc_test('''
    ... no
    ... >>> if(yes):
    ... ...     print('yes')
    ... no
    ... '''))
    if(yes):
        print('yes')
    """
    return "\n".join(
        line[4:] for line in block.splitlines() if line.startswith((">>>", "..."))
    )


def test_doc_examples_up_to_date():
    index_md = package_root.parent / "docs/index.md"
    blocks = index_md.read_text().split("```\n")
    pip_install = "%pip install"
    while True:
        block = blocks.pop(0)
        if block.startswith(pip_install):
            break
    doc_test_blocks = [block for block in blocks if block.startswith(">>>")]
    assert doc_test_blocks

    doc_code = "\n".join(strip_doc_test(block) for block in doc_test_blocks)

    csv_path = "docs/fill-in-correct-path.csv"
    plan = AnalysisPlan(
        product=Product.STATISTICS,
        groups={},
        analysis_columns={
            ColumnName("grade"): [
                AnalysisPlanColumn(
                    statistic_name=histogram.name,
                    lower_bound=0.0,
                    upper_bound=100.0,
                    bin_count=10,
                    weight=2,
                )
            ],
        },
        schema_columns={ColumnName("grade"): pl.Float32()},
        contributions=1,
        contributions_entity="Individual",
        csv_path=csv_path,
        epsilon=1.0,
        max_rows=100_000,
    )
    expected_code = NotebookGenerator(plan, "Note goes here!").make_py(reformat=True)

    unexpected_lines = [
        line
        for line in doc_code.splitlines()
        # csv_path is absolute and it will have local information
        # that shouldn't be checked in.
        if line not in expected_code and csv_path not in line
    ]
    assert (
        not unexpected_lines
    ), f"These lines are missing from {index_md}:\n" + "\n".join(unexpected_lines)
