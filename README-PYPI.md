# DP Wizard

[![pypi](https://img.shields.io/pypi/v/dp_wizard)](https://pypi.org/project/dp_wizard/)

Building on what we've learned from [DP Creator](https://github.com/opendp/dpcreator), DP Wizard offers:

- Easy installation with `pip install dp_wizard[app]`
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
usage: dp-wizard [-h] [--demo | --no_uploads]

DP Wizard makes it easier to get started with Differential Privacy.

options:
  -h, --help    show this help message and exit
  --demo        Use generated fake CSV for a quick demo
  --no_uploads  Prompt for column names instead of CSV upload

Unless you have set "--demo" or "--no_uploads", you will specify a CSV
inside the application.

Provide a "Public CSV" if you have a public data set, and are curious how
DP can be applied: The preview visualizations will use your public data.

Provide a "Private CSV" if you only have a private data set, and want to
make a release from it: The preview visualizations will only use
simulated data, and apart from the headers, the private CSV is not
read until the release.

Provide both if you have two CSVs with the same structure.
Perhaps the public CSV is older and no longer sensitive. Preview
visualizations will be made with the public data, but the release will
be made with private data.
```
