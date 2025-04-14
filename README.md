# DP Wizard

[![pypi](https://img.shields.io/pypi/v/dp_wizard)](https://pypi.org/project/dp_wizard/)

Building on what we've learned from [DP Creator](https://github.com/opendp/dpcreator), DP Wizard offers:

- Easy installation with `pip install dp_wizard`
- Simplified single-user application design
- Streamlined workflow that doesn't assume familiarity with differential privacy
- Interactive visualization of privacy budget choices
- UI development in Python with [Shiny](https://shiny.posit.co/py/)

DP Wizard guides the user through the application of differential privacy.
After selecting a local CSV, users are prompted to describe the analysis they need.
Output options include:

- A Jupyter notebook which demonstrates how to use [OpenDP](https://docs.opendp.org/).
- A plain Python script.
- Text and CSV reports.

## Usage

DP Wizard requires Python 3.10 or later.
You can check your current version with `python --version`.
The exact upgrade process will depend on your environment and operating system.

```
usage: dp-wizard [-h] [--public_csv CSV] [--private_csv CSV] [--contrib CONTRIB] [--demo]

DP Wizard makes it easier to get started with Differential Privacy.

options:
  -h, --help         show this help message and exit
  --public_csv CSV   Path to public CSV
  --private_csv CSV  Path to private CSV
  --contrib CONTRIB  How many rows can an individual contribute?
  --demo             Use generated fake CSV for a quick demo

Use "--public_csv" if you have a public data set, and are curious how
DP can be applied: The preview visualizations will use your public data.

Use "--private_csv" if you only have a private data set, and want to
make a release from it: The preview visualizations will only use
simulated data, and apart from the headers, the private CSV is not
read until the release.

Use "--public_csv" and "--private_csv" together if you have two CSVs
with the same structure. Perhaps the public CSV is older and no longer
sensitive. Preview visualizations will be made with the public data,
but the release will be made with private data.
```


## Contributions

There are several ways to contribute. First, if you find DP Wizard useful, please [let us know](https://docs.google.com/forms/d/e/1FAIpQLScaGdKS-vj-RrM7SCV_lAwZmxQ2bOqFrAkyDp4djxTqkTkinA/viewform) and we'll spend more time on this project. If DP Wizard doesn't work for you, we also want to know that! Please [file an issue](https://github.com/opendp/dp-wizard/issues/new/choose) and we'll look into it.

We also welcome PRs, but if you have an idea for a new feature, it may be helpful to get in touch before you begin, to make sure your idea is in line with our vision:
- The DP Wizard codebase shouldn't actually contain any differential privacy algorithms. This project is a thin wrapper around the [OpenDP library](https://github.com/opendp/opendp/), and that's where new algorithms should be added.
- DP Wizard isn't trying to do everything: The OpenDP library is rich, and DP Wizard exposes only a fraction of that functionality so the user isn't overwhelmed by details.
- DP Wizard tries to model the correct application of differential privacy. For example, while comparing DP results and unnoised statistics can be useful for education, that's not something this application will offer.

With those caveats in mind, feel free to [file a feature request](https://github.com/opendp/dp-wizard/issues/new/choose), or chat with us at our [online office hour](https://harvard.zoom.us/j/98058847683), usually Tuesdays and Thursdays at 11am Eastern.

## Development

This is the first project we've developed with Python Shiny,
so let's remember [what we learned](WHAT-WE-LEARNED.md) along the way.

### Getting Started

DP-Wizard will run across multiple Python versions, but for the fewest surprises during development, it makes sense to use the oldest supported version in a virtual environment. On MacOS:
```shell
$ git clone https://github.com/opendp/dp-wizard.git
$ cd dp-wizard
$ brew install python@3.10
$ python3.10 -m venv .venv
$ source .venv/bin/activate
```

You can now install dependencies, and the application itself, and start a demo:
```shell
$ pip install -r requirements-dev.txt
$ pre-commit install
$ playwright install
$ pip install --editable .
$ dp-wizard --demo
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

### Release

- Make sure you're up to date, and have the git-ignored credentials file `.pypirc`.
- Make one last feature branch:
  - Run `changelog.py` to update the `CHANGELOG.md`.
  - Then bump `dp_wizard/VERSION`, and add the new number at the top of the `CHANGELOG.md`.
  - Push to github; open PR, with version number in name; merge PR.
- `flit publish --pypirc .pypirc`

### Conventions

Branch names should be of the form `NNNN-short-description`, where `NNNN` is the issue number being addressed.

Dependencies should be pinned for development, but not pinned when the package is installed.
New dev dependencies can be added to `requirements-dev.in`, and then run `pip-compile requirements-dev.in` to update `requirements-dev.txt`

A Github [project board](https://github.com/orgs/opendp/projects/10/views/2) provides an overview of the issues and PRs.
When PRs are [Ready for Review](https://github.com/orgs/opendp/projects/10/views/2?filterQuery=status%3A%22Ready+for+Review%22) they should be flagged as such so reviewers can find them.

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

## Other resources

2025-04-11: [Slides for 5 minute mini-talk on v0.3.0](https://docs.google.com/presentation/d/1g1c5ksG9sN8A_qWW9nFmFFZ6dSCkUAmL6_cUahi3VPA/edit#slide=id.g34c5f4bdc6a_0_0)

2024-12-13: [Blog post for initial release](https://opendp.org/blog/dp-wizard-easy-way-get-started-differential-privacy-and-opendp)
