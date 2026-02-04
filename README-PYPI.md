# DP Wizard

[![pypi](https://img.shields.io/pypi/v/dp_wizard)](https://pypi.org/project/dp_wizard/)

DP Wizard makes it easier to get started with differential privacy,
the addition of calibrated noise to aggregate statistics to protect the privacy of individuals.
DP Wizard demonstrates how to calculate DP statistics or create a synthetic dataset from the data you provide.

If differential privacy is new to you, [these slides](https://opendp.github.io/dp-wizard/) provide some background, and explain how DP Wizard works.

Options for running DP Wizard:

- No install [online demo](https://mccalluc-dp-wizard.share.connect.posit.cloud/): Does not support data upload.
- Install from [Docker](https://hub.docker.com/repository/docker/mccalluc/dp-wizard/general): `docker run -p 8000:8000 mccalluc/dp-wizard`
- Install from [PyPI](https://pypi.org/project/dp-wizard/): `pip install 'dp-wizard[app]'; dp-wizard`
- Install from [source](https://github.com/opendp/dp-wizard): See developer instructions.

See the [FAQ](https://github.com/opendp/dp-wizard/blob/main/dp_wizard/FAQ.md) for more information.

## Screenshots

<!-- Run `scripts/screenshots.sh` to regenerate these screenshots. -->

Select Dataset:
![Screenshot with a "Data Source" panel on the left, and "Unit of Privacy" and "Product" on the right.](https://opendp.github.io/dp-wizard/screenshots/select-dataset.png)

Define Analysis:
![Screenshot with four panels: "Columns", "Grouping", "Privacy Budget", and "Simulation".](https://opendp.github.io/dp-wizard/screenshots/define-analysis.png)

Download Results:
![Screenshot with links to download analysis results".](https://opendp.github.io/dp-wizard/screenshots/download-results.png)

## Usage

DP Wizard requires Python 3.10 or later.
You can check your current version with `python --version`.
The exact upgrade process will depend on your environment and operating system.

Install with `pip install 'dp_wizard[pins]'` and you can start DP Wizard from the command line.

```
usage: dp-wizard [-h] [--sample] [--host HOST] [--port PORT] [--no_browser] [--reload]

DP Wizard makes it easier to get started with Differential Privacy.

options:
  -h, --help    show this help message and exit
  --sample      Generate a sample CSV: See how DP Wizard works without providing your own data
  --host HOST   Bind socket to this host
  --port PORT   Bind socket to this port. If 0, a random port will be used.
  --no_browser  By default, a browser is started; Enable this for no browser.
  --reload      Enable to watch source directory and reload on changes.

Unless you have set "--sample", you will specify a CSV inside the application.

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
