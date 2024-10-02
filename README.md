# DP Creator II

**Under Construction**

Building on what we've learned from [DP Creator](https://github.com/opendp/dpcreator), DP Creator II will offer:

- Easy installation with `pip install`
- Simplified single-user application design
- Streamlined workflow that doesn't assume familiarity with differential privacy
- Interactive visualization of privacy budget choices
- UI development in Python with [Shiny](https://shiny.posit.co/py/)
- Tracking of cumulative privacy consumption between sessions

## Usage

```
usage: dp-creator-ii [-h] [--csv CSV_PATH] [--unit UNIT_OF_PRIVACY]

DP Creator II makes it easier to get started with Differential Privacy.

options:
  -h, --help            show this help message and exit
  --csv CSV_PATH        Path to CSV containing private data
  --unit UNIT_OF_PRIVACY
                        Unit of privacy: How many rows can an individual
                        contribute?
```


## Development

### Getting Started

To get started, clone the repo and install dev dependencies in a virtual environment:
```
git clone https://github.com/opendp/dp-creator-ii.git
cd dp-creator-ii
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
playwright install
```

Now install the application itself and run it:
```
flit install --symlink
dp-creator-ii
```
Your browser should open and connect you to the application.

### Testing

Tests should pass, and code coverage should be complete (except blocks we explicitly ignore):
```
coverage run -m pytest -v
coverage report
```

We're using [Playwright](https://playwright.dev/python/) for end-to-end tests. You can use it to [generate test code](https://playwright.dev/python/docs/codegen-intro) just by interacting with the app in a browser:
```
dp-creator-ii&
playwright codegen http://127.0.0.1:8000/
```

You can also [step through these tests](https://playwright.dev/python/docs/running-tests#debugging-tests) and see what the browser sees:
```
PWDEBUG=1 pytest
```

### Conventions

Branch names should be of the form `NNNN-short-description`, where `NNNN` is the issue number being addressed.

Dependencies should be pinned for development, but not pinned when the package is installed.
New dev dependencies can be added to `requirements-dev.in`, and then run `pip-compile requirements-dev.in` to update `requirements-dev.txt`
