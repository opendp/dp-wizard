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
