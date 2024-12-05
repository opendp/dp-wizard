# DP Wizard

**Under Construction**

Building on what we've learned from [DP Creator](https://github.com/opendp/dpcreator), DP Wizard will offer:

- Easy installation with `pip install`
- Simplified single-user application design
- Streamlined workflow that doesn't assume familiarity with differential privacy
- Interactive visualization of privacy budget choices
- UI development in Python with [Shiny](https://shiny.posit.co/py/)

We plan to implement a [proof of concept](https://docs.google.com/document/d/1dteip598-jYj6KFuoYRyrZDPUuwDl9fHgxARiSieVGw/edit) over a couple months, and then get feedback from users before deciding on next steps.

## Usage

```
usage: dp-wizard [-h] [--csv CSV_PATH] [--contrib CONTRIB] [--demo]

options:
  -h, --help         show this help message and exit
  --csv CSV_PATH     Path to CSV containing private data
  --contrib CONTRIB  How many rows can an individual contribute?
  --demo             Use generated fake CSV for a quick demo
```


## Development

This is the first project we've developed with Python Shiny,
so let's remember [what we learned](WHAT-WE-LEARNED.md) along the way.

### Getting Started

To get started, clone the repo and install dev dependencies in a virtual environment:
```shell
$ git clone https://github.com/opendp/dp-wizard.git
$ cd dp-wizard
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements-dev.txt
$ pre-commit install
$ playwright install
```

Now install the application itself and run it:
```shell
$ flit install --symlink
$ dp-wizard
```
Your browser should open and connect you to the application.

### Testing

Tests should pass, and code coverage should be complete (except blocks we explicitly ignore):
```shell
$ ./ci.sh
```

We're using [Playwright](https://playwright.dev/python/) for end-to-end tests. You can use it to [generate test code](https://playwright.dev/python/docs/codegen-intro) just by interacting with the app in a browser:
```shell
$ dp-wizard # The server will continue to run, so open a new terminal to continue.
$ playwright codegen http://127.0.0.1:8000/
```

You can also [step through these tests](https://playwright.dev/python/docs/running-tests#debugging-tests) and see what the browser sees:
```shell
$ PWDEBUG=1 pytest -k test_app
```

If Playwright fails in CI, we can still see what went wrong:
- Scroll to the end of the CI log, to `actions/upload-artifact`.
- Download the zipped artifact locally.
- Inside the zipped artifact will be _another_ zip: `trace.zip`.
- Don't unzip it! Instead, open it with [trace.playwright.dev](https://trace.playwright.dev/).

### Conventions

Branch names should be of the form `NNNN-short-description`, where `NNNN` is the issue number being addressed.

Dependencies should be pinned for development, but not pinned when the package is installed.
New dev dependencies can be added to `requirements-dev.in`, and then run `pip-compile requirements-dev.in` to update `requirements-dev.txt`

A Github [project board](https://github.com/orgs/opendp/projects/10/views/2) provides an overview of the issues and PRs.

```mermaid
graph TD
    subgraph Pending
        %% We only get one auto-add workflow with the free plan.
        %% https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/adding-items-automatically
        Issue-New
        PR-New-or-Changes
    end
    %% subgraph In Progress
        %% How should this be used?
        %% Can it be automated
    %% end
    subgraph Ready for Review
        PR-for-Review
    end
    subgraph In Review
        PR-in-Review --> PR-Approved
    end
    subgraph Done
        Issue-Closed
        PR-Merged
        PR-Closed
    end
    PR-New-or-Changes -->|manual| PR-for-Review
    PR-for-Review -->|manual| PR-in-Review
    Issue-New -->|auto| Issue-Closed
    PR-New-or-Changes -->|auto| PR-Closed
    PR-for-Review -->|auto| PR-Closed
    PR-in-Review -->|auto| PR-Closed
    PR-for-Review -->|manual| PR-New-or-Changes
    PR-in-Review -->|auto| PR-New-or-Changes
    PR-Approved -->|auto| PR-Merged
```
- For `manual` transitions, the status of the issue or PR will need to be updated by hand, either on the issue, or by dragging between columns on the board.
- For `auto` transitions, some other action (for example, approving a PR) should trigger a [workflow](https://github.com/orgs/opendp/projects/10/workflows).
- These are the only the states that matter. Whether PR is a draft or has assignees does not matter.
- If we need anything more than this, we should consider a paid plan, so that we have access to more workflows.
