from pathlib import Path

from shiny.run import ShinyAppProc
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture


app = create_app_fixture("../dp_creator_ii/app/__init__.py")


# TODO: Why is incomplete coverage reported here?
# https://github.com/opendp/dp-creator-ii/issues/18
def test_app(page: Page, app: ShinyAppProc):  # pragma: no cover
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
    page.goto(app.url)
    expect(page).to_have_title("DP Creator II")
    expect_visible(pick_dataset_text)
    expect_not_visible(perform_analysis_text)
    expect_not_visible(download_results_text)
    page.get_by_label("Contributions").fill("42")
    page.get_by_text("Code sample").click()
    expect_visible("dp.unit_of(contributions=42)")
    expect_no_error()

    csv_path = Path(__file__).parent / "fixtures" / "fake.csv"
    page.get_by_label("Choose CSV file").set_input_files(csv_path.resolve())
    expect_no_error()

    # -- Define analysis --
    page.get_by_role("button", name="Define analysis").click()
    expect_not_visible(pick_dataset_text)
    expect_visible(perform_analysis_text)
    expect_not_visible(download_results_text)
    # Columns:
    expect_visible("student_id")
    expect_visible("class_year")
    expect_visible("hw_number")
    expect_visible("grade")
    # Set column details:
    page.get_by_label("grade").check()
    page.get_by_label("Min").click()
    page.get_by_label("Min").fill("0")
    page.get_by_label("Max").click()
    page.get_by_label("Max").fill("100")
    page.get_by_label("Bins").click()
    page.get_by_label("Bins").fill("20")
    page.get_by_label("Weight").select_option("8")
    # Epsilon slider:
    expect_visible("0.1")
    expect_visible("10.0")
    expect_visible("Epsilon: 1.0")
    page.locator(".irs-bar").click()
    expect_visible("Epsilon: 0.316")
    page.locator(".irs-bar").click()
    expect_visible("Epsilon: 0.158")
    expect_no_error()

    # -- Download results --
    page.get_by_role("button", name="Download results").click()
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
