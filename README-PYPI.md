# DP Wizard

[![pypi](https://img.shields.io/pypi/v/dp_wizard)](https://pypi.org/project/dp_wizard/)

DP Wizard makes it easier to get started with differential privacy.

You can run DP Wizard locally and upload your own CSV,
or use the [cloud deployment](https://mccalluc-dp-wizard.share.connect.posit.cloud/) and only provide column names to protect your private data.
In either case, you'll be prompted to describe your privacy budget and the analysis you need, including:

- Grouping
- DP means, medians, and histograms

With that information, DP Wizard provides

- A Jupyter notebook which demonstrates how to use the [OpenDP Library](https://docs.opendp.org/).
- A plain Python script.
- Text and CSV reports.

## Usage

DP Wizard requires Python 3.10 or later.
You can check your current version with `python --version`.
The exact upgrade process will depend on your environment and operating system.

Install with `pip install dp_wizard[app]` and you can start DP Wizard from the command line.

```
usage: dp-wizard [-h] [--demo | --cloud]

DP Wizard makes it easier to get started with Differential Privacy.

options:
  -h, --help  show this help message and exit
  --demo      Use generated fake CSV for a quick demo
  --cloud     Prompt for column names instead of CSV upload

Unless you have set "--demo" or "--cloud", you will specify a CSV
inside the application.

Provide a "Private CSV" if you only have a private data set, and want to
make a release from it: The preview visualizations will only use
simulated data, and apart from the headers, the private CSV is not
read until the release.

Provide a "Public CSV" if you have a public data set, and are curious how
DP can be applied: The preview visualizations will use your public data.

Provide both if you have two CSVs with the same structure.
Perhaps the public CSV is older and no longer sensitive. Preview
visualizations will be made with the public data, but the release will
be made with private data.
```
