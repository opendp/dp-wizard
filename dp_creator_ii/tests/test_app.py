from shiny.run import ShinyAppProc
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture


app = create_app_fixture("../app.py")


# TODO: Why is incomplete coverage reported here?
def test_app(page: Page, app: ShinyAppProc):  # pragma: no cover
    pick_dataset_text = "TODO: Pick dataset"
    perform_analysis_text = "TODO: Perform analysis"
    download_results_text = "TODO: Download results"

    page.goto(app.url)
    expect(page).to_have_title("DP Creator II")
    expect(page.get_by_text(pick_dataset_text)).to_be_visible()
    expect(page.get_by_text(perform_analysis_text)).not_to_be_visible()
    expect(page.get_by_text(download_results_text)).not_to_be_visible()

    page.get_by_role("button", name="Perform analysis").click()
    expect(page.get_by_text(pick_dataset_text)).not_to_be_visible()
    expect(page.get_by_text(perform_analysis_text)).to_be_visible()
    expect(page.get_by_text(download_results_text)).not_to_be_visible()

    page.get_by_role("button", name="Download results").click()
    expect(page.get_by_text(pick_dataset_text)).not_to_be_visible()
    expect(page.get_by_text(perform_analysis_text)).not_to_be_visible()
    expect(page.get_by_text(download_results_text)).to_be_visible()
