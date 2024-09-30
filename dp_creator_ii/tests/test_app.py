from shiny.run import ShinyAppProc
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture


app = create_app_fixture("../app/__init__.py")


# TODO: Why is incomplete coverage reported here?
def test_app(page: Page, app: ShinyAppProc):  # pragma: no cover
    page.goto(app.url)
    expect(page).to_have_title("DP Creator II")
    expect(page.locator("body")).to_contain_text("TODO: Pick dataset")
