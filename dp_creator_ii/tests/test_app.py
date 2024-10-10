from pathlib import Path

from shiny.run import ShinyAppProc
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture


app = create_app_fixture("../app/__init__.py")


# TODO: Why is incomplete coverage reported here?
# https://github.com/opendp/dp-creator-ii/issues/18
def test_navigation(page: Page, app: ShinyAppProc):  # pragma: no cover
    pick_dataset_text = "TODO: Pick dataset"
    perform_analysis_text = "TODO: Define analysis"
    download_results_text = "TODO: Download results"

    def expect_visible(text):
        expect(page.get_by_text(text)).to_be_visible()

    def expect_not_visible(text):
        expect(page.get_by_text(text)).not_to_be_visible()

    def expect_no_error():
        expect(page.locator(".shiny-output-error")).not_to_be_attached()

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
    expect_visible("student_id")
    expect_no_error()

    page.get_by_role("button", name="Define analysis").click()
    expect_not_visible(pick_dataset_text)
    expect_visible(perform_analysis_text)
    expect_not_visible(download_results_text)
    expect_no_error()

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
