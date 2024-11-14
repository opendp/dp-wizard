from pathlib import Path

from shiny.run import ShinyAppProc
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture


demo_app = create_app_fixture(Path(__file__).parent / "fixtures/demo_app.py")
default_app = create_app_fixture(Path(__file__).parent / "fixtures/default_app.py")
tooltip = "#choose_csv_demo_tooltip_ui svg"
for_the_demo = "For the demo, we'll imagine"
simulation = "This simulation assumes a normal distribution"


# TODO: Why is incomplete coverage reported here?
# https://github.com/opendp/dp-wizard/issues/18
def test_demo_app(page: Page, demo_app: ShinyAppProc):  # pragma: no cover
    page.goto(demo_app.url)
    expect(page).to_have_title("DP Wizard")
    expect(page.get_by_text(for_the_demo)).not_to_be_visible()
    page.locator(tooltip).hover()
    expect(page.get_by_text(for_the_demo)).to_be_visible()


def test_default_app(page: Page, default_app: ShinyAppProc):  # pragma: no cover
    pick_dataset_text = "How many rows of the CSV"
    perform_analysis_text = "Select numeric columns of interest"
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
    expect_visible("dp.unit_of(contributions=42)")
    expect_no_error()

    # Button disabled until upload:
    define_analysis_button = page.get_by_role("button", name="Define analysis")
    assert define_analysis_button.is_disabled()

    # Now upload:
    csv_path = Path(__file__).parent / "fixtures" / "fake.csv"
    page.get_by_label("Choose CSV file").set_input_files(csv_path.resolve())
    expect_no_error()

    # -- Define analysis --
    define_analysis_button.click()
    expect_not_visible(pick_dataset_text)
    expect_visible(perform_analysis_text)
    expect_not_visible(download_results_text)
    # Columns:
    expect_visible("1: [blank]")  # Empty column!
    expect_visible("2: class year")
    expect_visible("3: class year_duplicated_0")  # Duplicated column!
    expect_visible("4: hw number")
    expect_visible("5: hw-number")  # Distinguished by non-word character!
    expect_visible("6: grade")
    # Epsilon slider:
    # (Note: Slider tests failed on CI when run after column details,
    # although it worked locally. This works in either environment.
    # Maybe a race condition?)
    expect_visible("0.1")
    expect_visible("10.0")
    expect_visible("Epsilon: 1.0")
    page.locator(".irs-bar").click()
    expect_visible("Epsilon: 0.316")
    page.locator(".irs-bar").click()
    expect_visible("Epsilon: 0.158")

    # Button disabled until column selected:
    download_results_button = page.get_by_role("button", name="Download results")
    assert download_results_button.is_disabled()

    # Set column details:
    page.get_by_label("grade").check()
    expect_visible(simulation)
    # Check that default is set correctly:
    assert page.get_by_label("Upper").input_value() == "10"
    # Reset, and confirm:
    new_value = "20"
    page.get_by_label("Upper").fill(new_value)
    # Uncheck the column:
    page.get_by_label("grade").uncheck()
    expect_not_visible(simulation)
    # Recheck the column:
    page.get_by_label("grade").check()
    expect_visible(simulation)
    assert page.get_by_label("Upper").input_value() == new_value
    # TODO: Setting more inputs without checking for updates
    # cause recalculations to pile up, and these cause timeouts on CI:
    # It is still rerendering the graph after hitting "Download results".
    # https://github.com/opendp/dp-wizard/issues/116
    expect_no_error()

    # -- Download results --
    download_results_button.click()
    expect_not_visible(pick_dataset_text)
    expect_not_visible(perform_analysis_text)
    expect_visible(download_results_text)
    expect_no_error()

    with page.expect_download() as download_info:
        page.get_by_text("Download script").click()
    expect_no_error()

    download = download_info.value
    script = download.path().read_text()
    assert "privacy_unit = dp.unit_of(contributions=42)" in script
