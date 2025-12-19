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
        columns={
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
        contributions=1,
        contributions_entity="Individual",
        csv_path=csv_path,
        epsilon=1.0,
        max_rows=100_000,
    )
    expected_code = NotebookGenerator(plan, "Note goes here!").make_py(reformat=True)

    if any(
        # csv_path is expanded to an absolute path, so ignore it:
        line not in expected_code and csv_path not in line
        for line in doc_code.splitlines()
    ):
        # It's fine for the docs to be a subset of the generated code,
        # but if a line is missing, the "pytest -vv" diff
        # will give us context to fix it.
        assert expected_code == doc_code  # pragma: no cover
