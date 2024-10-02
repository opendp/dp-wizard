from shiny.run import ShinyAppProc
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture


app = create_app_fixture("../app/__init__.py")


# TODO: Why is incomplete coverage reported here?
# https://github.com/opendp/dp-creator-ii/issues/18
def test_app(page: Page, app: ShinyAppProc):  # pragma: no cover
    pick_dataset_text = "TODO: Pick dataset"
    perform_analysis_text = "TODO: Define analysis"
    download_results_text = "TODO: Download results"

    def expect_visible(text):
        expect(page.get_by_text(text)).to_be_visible()

    def expect_not_visible(text):
        expect(page.get_by_text(text)).not_to_be_visible()

    page.goto(app.url)
    expect(page).to_have_title("DP Creator II")
    expect_visible(pick_dataset_text)
    expect_not_visible(perform_analysis_text)
    expect_not_visible(download_results_text)

    page.get_by_role("button", name="Define analysis").click()
    expect_not_visible(pick_dataset_text)
    expect_visible(perform_analysis_text)
    expect_not_visible(download_results_text)

    page.get_by_role("button", name="Download results").click()
    expect_not_visible(pick_dataset_text)
    expect_not_visible(perform_analysis_text)
    expect_visible(download_results_text)

    with page.expect_download() as download_info:
        page.get_by_text("Download script").click()
    download = download_info.value
    script = download.path().read_text()
    assert "privacy_unit=dp.unit_of(contributions=1)" in script
