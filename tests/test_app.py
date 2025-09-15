import re
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

from dp_wizard.utils.code_generators.notebook_generator import PLACEHOLDER_CSV_NAME

bp = "BREAKPOINT()".lower()
if bp in Path(__file__).read_text():
    raise Exception(  # pragma: no cover
        f"Instead of `{bp}`, use `page.pause()` in playwright tests. "
        "See https://playwright.dev/python/docs/debug"
        "#run-a-test-from-a-specific-breakpoint"
    )

root_path = Path(__file__).parent.parent
sample_app = create_app_fixture(root_path / "dp_wizard/app_sample.py")
cloud_app = create_app_fixture(root_path / "dp_wizard/app_cloud.py")
local_app = create_app_fixture(root_path / "dp_wizard/app_local.py")
qa_app = create_app_fixture(root_path / "dp_wizard/app_qa.py")


def test_cloud_app(page: Page, cloud_app: ShinyAppProc):  # pragma: no cover
    page.goto(cloud_app.url)

    page.locator("#max_rows").fill("10000")
    expect(page).to_have_title("DP Wizard")
    expect(page.get_by_text("Choose Public CSV")).not_to_be_visible()
    page.get_by_label("CSV Column Names").fill("a_column")

    page.get_by_role("button", name="Define analysis").click()
    page.locator(".selectize-input").nth(0).click()
    page.get_by_text("1: a_column").click()
    page.get_by_label("Lower").fill("0")
    page.get_by_label("Upper").fill("10")

    page.get_by_role("button", name="Download Results").click()
    with page.expect_download() as download_info:
        page.get_by_role("link", name="Download Notebook (unexecuted").click()

    download_path = download_info.value.path()

    # Try to execute the downloaded file:
    # Based on https://nbconvert.readthedocs.io/en/latest/execute_api.html#example
    nb = nbformat.read(download_path.open(), as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb)

    # Clean up file in CWD that is created by notebook execution.
    Path(PLACEHOLDER_CSV_NAME).unlink()


def test_qa_app(page: Page, qa_app: ShinyAppProc):  # pragma: no cover
    page.goto(qa_app.url)

    page.locator("#max_rows").fill("10000")
    page.get_by_role("button", name="Define analysis").click()

    page.locator(".selectize-input").nth(0).click()
    page.get_by_text(": grade").click()
    page.get_by_label("Lower").fill("0")
    page.get_by_label("Upper").fill("10")

    page.get_by_role("button", name="Download Results").click()
    page.get_by_role("link", name="Download Notebook (.ipynb)").click()
    expect(page.get_by_text('raise Exception("qa_mode!")')).to_be_visible()


def test_sample_app(page: Page, sample_app: ShinyAppProc):  # pragma: no cover
    page.goto(sample_app.url)
    expect(page).to_have_title("DP Wizard")

    page.locator("#max_rows").fill("10000")

    # -- Define analysis --
    page.get_by_role("button", name="Define analysis").click()
    expect(page.get_by_text("dataset on the previous tab")).not_to_be_visible()
    expect(page.get_by_text("string values can be used for grouping")).to_be_visible()


def test_local_app_validations(page: Page, local_app: ShinyAppProc):  # pragma: no cover
    pick_dataset_text = "How many rows of the CSV"
    perform_analysis_text = "Select columns to calculate statistics on"
    download_results_text = "You can now make a differentially private release"

    # -- Select dataset --
    page.goto(local_app.url)
    expect(page).to_have_title("DP Wizard")
    page.locator("#max_rows").fill("10000")
    expect(page.get_by_text(pick_dataset_text)).to_be_visible()
    expect(page.get_by_text(perform_analysis_text)).not_to_be_visible()
    expect(page.get_by_text(download_results_text)).not_to_be_visible()
    page.locator("#contributions").fill("123")
    page.get_by_text("Code sample: Unit of Privacy").click()
    expect(page.get_by_text("123")).to_have_class("hljs-number")
    expect(page.locator(".shiny-output-error")).not_to_be_attached()

    # Button disabled until upload:
    define_analysis_button = page.get_by_role("button", name="Define analysis")
    assert define_analysis_button.is_disabled()

    # Now upload:
    csv_path = Path(__file__).parent / "fixtures" / "fake.csv"
    page.get_by_label("Choose Public CSV").set_input_files(csv_path.resolve())

    # Check validation of contributions:
    # Playwright itself won't let us fill non-numbers in this field.
    # "assert define_analysis_button.is_enabled()" has spurious errors.
    # https://github.com/opendp/dp-wizard/issues/221
    page.locator("#contributions").fill("0")
    expect(page.get_by_text("Contributions must be 1 or greater")).to_be_visible()
    expected_error = (
        "Specify CSV, unit of privacy, and maximum row count before proceeding."
    )
    expect(page.get_by_text(expected_error)).to_be_visible()

    page.locator("#contributions").fill("2")
    expect(page.get_by_text("Contributions must be 1 or greater")).not_to_be_visible()
    expect(page.get_by_text(expected_error)).not_to_be_visible()

    expect(page.locator(".shiny-output-error")).not_to_be_attached()

    # -- Define analysis --
    define_analysis_button.click()
    expect(page.get_by_text(pick_dataset_text)).not_to_be_visible()
    expect(page.get_by_text(perform_analysis_text)).to_be_visible()
    expect(page.get_by_text(download_results_text)).not_to_be_visible()
    # Epsilon slider:
    expect(page.get_by_text("Epsilon: 1.0")).to_be_visible()
    page.locator(".irs-bar").click()
    expect(page.get_by_text("Epsilon: 0.3")).to_be_visible()
    page.locator(".irs-bar").click()
    expect(page.get_by_text("Epsilon: 0.2")).to_be_visible()
    # Simulation
    expect(page.get_by_text("Because you've provided a public CSV")).to_be_visible()

    # Button disabled until column selected:
    download_results_button = page.get_by_role("button", name="Download Results")
    assert download_results_button.is_disabled()

    # Currently the only change when the estimated rows changes is the plot,
    # but we could have the confidence interval in the text...
    page.get_by_label("Estimated Rows").select_option("1000")

    # Pick columns:
    page.locator(".selectize-input").nth(0).click()
    page.get_by_text(": grade").click()
    # Pick grouping:
    page.locator(".selectize-input").nth(1).click()
    page.get_by_text(": class year").nth(2).click()

    # Check that default is set correctly:
    # (Explicit "float()" because sometimes returns "10", sometimes "10.0".
    #  Weird, but not something to spend time on.)
    assert page.get_by_label("Upper").input_value() == ""

    # Input validation:
    page.get_by_label("Number of Bins").fill("-1")
    expect(page.get_by_text("Number should be a positive integer.")).to_be_visible()
    # Changing epsilon should not reset column details:
    page.locator(".irs-bar").click()
    expect(page.get_by_text("Number should be a positive integer.")).to_be_visible()
    page.get_by_label("Number of Bins").fill("10")

    page.get_by_label("Upper").fill("")
    expect(page.get_by_text("Upper bound is required")).to_be_visible()
    page.get_by_label("Upper").fill("nan")
    expect(page.get_by_text("Upper bound should be a number")).to_be_visible()
    page.get_by_label("Lower").fill("0")
    page.get_by_label("Upper").fill("-1")
    expect(
        page.get_by_text("Lower bound should be less than upper bound")
    ).to_be_visible()

    new_value = "20"
    page.get_by_label("Upper").fill(new_value)
    assert float(page.get_by_label("Upper").input_value()) == float(new_value)
    expect(page.get_by_text("The 95% confidence interval is ±60.4")).to_be_visible()
    page.get_by_text("Data Table").click()
    expect(
        page.get_by_text(f"({new_value}, inf]")
    ).to_be_visible()  # Because values are well above the bins.

    # Add a second column:
    page.locator(".selectize-input").nth(0).click()
    page.get_by_text(": hw-number").first.click()
    # Previous setting should not be cleared.
    expect(page.get_by_role("textbox", name="Upper Bound")).to_have_value("20")
    expect(page.locator(".shiny-output-error")).not_to_be_attached()

    # A separate test spends less time on parameter validation
    # and instead exercises all downloads.
    # Splitting the end-to-end tests minimizes the total time
    # to run tests in parallel.


def test_local_app_downloads(page: Page, local_app: ShinyAppProc):  # pragma: no cover

    dataset_release_warning = "changes to the dataset will constitute a new release"
    analysis_release_warning = "changes to the analysis will constitute a new release"
    analysis_requirements_warning = "select your dataset on the previous tab"
    results_requirements_warning = "define your analysis on the previous tab"

    page.goto(local_app.url)
    page.locator("#max_rows").fill("10000")
    expect(page.get_by_text(dataset_release_warning)).not_to_be_visible()
    page.get_by_role("tab", name="Define Analysis").click()
    expect(page.get_by_text(analysis_requirements_warning)).to_be_visible()
    page.get_by_role("tab", name="Download Results").click()
    expect(page.get_by_text(results_requirements_warning)).to_be_visible()
    page.get_by_role("tab", name="Select Dataset").click()

    # -- Select dataset --
    csv_path = Path(__file__).parent / "fixtures" / "fake.csv"
    page.get_by_label("Choose Public CSV").set_input_files(csv_path.resolve())

    # -- Define analysis --
    page.get_by_role("button", name="Define analysis").click()
    expect(page.get_by_text(analysis_release_warning)).not_to_be_visible()
    expect(page.get_by_text(analysis_requirements_warning)).not_to_be_visible()

    # Pick columns:
    page.locator(".selectize-input").nth(0).click()
    page.get_by_text(": grade").nth(0).click()
    # Pick grouping:
    page.locator(".selectize-input").nth(1).click()
    page.get_by_text("class year").nth(2).click()
    # Fill inputs:
    page.get_by_label("Lower").fill("0")
    page.get_by_label("Upper").fill("10")

    # -- Download Results --
    expect(page.get_by_text(results_requirements_warning)).not_to_be_visible()
    page.get_by_role("button", name="Download Results").click()

    # Right now, the significant test start-up costs mean
    # it doesn't make sense to parameterize this test,
    # but that could change.
    matches = [
        re.search(r'button\("([^"]+)", "([^"]+)"', line)
        for line in (
            Path(__file__).parent.parent / "dp_wizard" / "shiny" / "results_panel.py"
        )
        .read_text()
        .splitlines()
    ]

    # Expand all accordions:
    page.get_by_text("Reports", exact=True).click()
    page.get_by_text("Unexecuted Notebooks", exact=True).click()
    page.get_by_text("Scripts", exact=True).click()

    for match in matches:
        if not match:
            continue
        name = match.group(1)
        ext = match.group(2)
        link_text = f"Download {name} ({ext})"
        with page.expect_download() as download_info:
            page.get_by_text(link_text).click()

        download_name = download_info.value.suggested_filename
        assert download_name.startswith(
            "dp_statistics_for_grade_grouped_by_class_year.",
        )
        assert download_name.endswith(ext)

        download_path = download_info.value.path()
        content = download_path.read_bytes()
        assert content  # Could add assertions for different document types.

    # -- Define Analysis --
    page.get_by_role("tab", name="Define Analysis").click()
    expect(page.get_by_text(analysis_release_warning)).to_be_visible()

    # -- Select Dataset --
    page.get_by_role("tab", name="Select Dataset").click()
    expect(page.get_by_text(dataset_release_warning)).to_be_visible()
