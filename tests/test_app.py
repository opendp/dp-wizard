from pathlib import Path
import re

from shiny.run import ShinyAppProc
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture


bp = "BREAKPOINT()".lower()
if bp in Path(__file__).read_text():
    raise Exception(  # pragma: no cover
        f"Instead of `{bp}`, use `page.pause()` in playwright tests. "
        "See https://playwright.dev/python/docs/debug"
        "#run-a-test-from-a-specific-breakpoint"
    )


demo_app = create_app_fixture(Path(__file__).parent / "fixtures/demo_app.py")
default_app = create_app_fixture(Path(__file__).parent / "fixtures/default_app.py")
tooltip = "#public_csv_path-label svg"
for_the_demo = "For the demo, we'll imagine"


def test_demo_app(page: Page, demo_app: ShinyAppProc):  # pragma: no cover
    page.goto(demo_app.url)
    expect(page).to_have_title("DP Wizard")
    expect(page.get_by_text(for_the_demo)).not_to_be_visible()
    page.locator(tooltip).hover()
    expect(page.get_by_text(for_the_demo)).to_be_visible()

    # -- Define analysis --
    page.get_by_role("button", name="Define analysis").click()
    expect(page.get_by_text("This simulation will assume")).to_be_visible()


def test_default_app_validations(
    page: Page, default_app: ShinyAppProc
):  # pragma: no cover
    pick_dataset_text = "How many rows of the CSV"
    perform_analysis_text = "Select columns to calculate statistics on"
    download_results_text = "You can now make a differentially private release"

    def expect_visible(text):
        expect(page.get_by_text(text)).to_be_visible()

    def expect_not_visible(text):
        expect(page.get_by_text(text)).not_to_be_visible()

    def expect_no_error():
        expect(page.locator(".shiny-output-error")).not_to_be_attached()

    # -- Select dataset --
    page.goto(default_app.url)
    expect(page).to_have_title("DP Wizard")
    expect(page.locator(tooltip)).to_have_count(0)
    expect_visible(pick_dataset_text)
    expect_not_visible(perform_analysis_text)
    expect_not_visible(download_results_text)
    page.get_by_label("Contributions").fill("42")
    page.get_by_text("Code sample: Unit of Privacy").click()
    expect_visible("contributions = 42")
    expect_no_error()

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
    page.get_by_label("Contributions").fill("0")
    expect_visible("Contributions must be 1 or greater")
    expect_visible("Choose CSV and Contributions before proceeding")

    page.get_by_label("Contributions").fill("42")
    expect_not_visible("Contributions must be 1 or greater")
    expect_not_visible("Choose CSV and Contributions before proceeding")

    expect_no_error()

    # -- Define analysis --
    define_analysis_button.click()
    expect_not_visible(pick_dataset_text)
    expect_visible(perform_analysis_text)
    expect_not_visible(download_results_text)
    # Epsilon slider:
    expect_visible("Epsilon: 1.0")
    page.locator(".irs-bar").click()
    expect_visible("Epsilon: 0.316")
    page.locator(".irs-bar").click()
    expect_visible("Epsilon: 0.158")
    # Simulation
    expect_visible("Because you've provided a public CSV")

    # Button disabled until column selected:
    download_results_button = page.get_by_role("button", name="Download Results")
    assert download_results_button.is_disabled()

    # Currently the only change when the estimated rows changes is the plot,
    # but we could have the confidence interval in the text...
    page.get_by_label("Estimated Rows").select_option("1000")

    # Pick grouping:
    page.locator(".selectize-input").nth(0).click()
    page.get_by_text("class year").nth(0).click()
    # Pick columns:
    page.locator(".selectize-input").nth(1).click()
    page.get_by_text("grade").nth(1).click()

    # Check that default is set correctly:
    # (Explicit "float()" because sometimes returns "10", sometimes "10.0".
    #  Weird, but not something to spend time on.)
    assert float(page.get_by_label("Upper").input_value()) == 10.0
    # Reset, and confirm:
    new_value = "20"
    page.get_by_label("Upper").fill(new_value)
    assert float(page.get_by_label("Upper").input_value()) == float(new_value)
    expect_visible("The 95% confidence interval is ±794")
    page.get_by_text("Data Table").click()
    expect_visible(f"({new_value}, inf]")  # Because values are well above the bins.

    # Add a second column:
    # page.get_by_label("blank").check()
    # TODO: Test is flaky?
    # expect(page.get_by_text("Weight")).to_have_count(2)
    # TODO: Setting more inputs without checking for updates
    # causes recalculations to pile up, and these cause timeouts on CI:
    # It is still rerendering the graph after hitting "Download Results".
    # https://github.com/opendp/dp-wizard/issues/116
    expect_no_error()

    # -- Feedback --
    page.get_by_text("Feedback").click()
    iframe = page.locator("#feedback-iframe")
    expect(iframe).to_be_visible()
    expect(iframe.content_frame.get_by_text("DP Wizard Feedback")).to_be_visible()
    # Text comes from iframe, so this does introduce a dependency on an outside service.

    # A separate test spends less time on parameter validation
    # and instead exercises all downloads.
    # Splitting the end-to-end tests minimizes the total time
    # to run tests in parallel.


def test_default_app_downloads(
    page: Page, default_app: ShinyAppProc
):  # pragma: no cover
    # -- Select dataset --
    page.goto(default_app.url)
    csv_path = Path(__file__).parent / "fixtures" / "fake.csv"
    page.get_by_label("Choose Public CSV").set_input_files(csv_path.resolve())

    # -- Define analysis --
    page.get_by_role("button", name="Define analysis").click()

    # Pick grouping:
    page.locator(".selectize-input").nth(0).click()
    page.get_by_text("class year").nth(0).click()
    # Pick columns:
    page.locator(".selectize-input").nth(1).click()
    page.get_by_text("grade").nth(1).click()

    # -- Download Results --
    page.get_by_role("button", name="Download Results").click()

    # Right now, the significant test start-up costs mean
    # it doesn't make sense to parameterize this test,
    # but that could change.
    matches = [
        re.search(r'button\("([^"]+)", "([^"]+)"', line)
        for line in (
            Path(__file__).parent.parent / "dp_wizard" / "app" / "results_panel.py"
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

        download = download_info.value
        content = download.path().read_bytes()
        assert content  # Could add assertions for different document types.
