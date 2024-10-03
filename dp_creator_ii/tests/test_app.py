from shiny.run import ShinyAppProc
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture


app = create_app_fixture("../app/__init__.py")


def expect_visible(page, text):
    expect(page.get_by_text(text)).to_be_visible()


def expect_not_visible(page, text):
    expect(page.get_by_text(text)).not_to_be_visible()


# TODO: Why is incomplete coverage reported here?
# https://github.com/opendp/dp-creator-ii/issues/18
def test_navigation(page: Page, app: ShinyAppProc):  # pragma: no cover
    pick_dataset_text = "TODO: Pick dataset"
    perform_analysis_text = "TODO: Define analysis"
    download_results_text = "TODO: Download results"

    page.goto(app.url)
    expect(page).to_have_title("DP Creator II")
    expect_visible(page, pick_dataset_text)
    expect_not_visible(page, perform_analysis_text)
    expect_not_visible(page, download_results_text)

    page.get_by_role("button", name="Define analysis").click()
    expect_not_visible(page, pick_dataset_text)
    expect_visible(page, perform_analysis_text)
    expect_not_visible(page, download_results_text)

    page.get_by_role("button", name="Download results").click()
    expect_not_visible(page, pick_dataset_text)
    expect_not_visible(page, perform_analysis_text)
    expect_visible(page, download_results_text)

    with page.expect_download() as download_info:
        page.get_by_text("Download script").click()
    download = download_info.value
    script = download.path().read_text()
    assert "privacy_unit = dp.unit_of(contributions=1)" in script


def test_pick_dataset(page: Page, app: ShinyAppProc):  # pragma: no cover
    page.goto(app.url)
    page.get_by_label("Contributions").fill("42")
    page.get_by_text("Code sample").click()
    expect_visible(page, "dp.unit_of(contributions=42)")
