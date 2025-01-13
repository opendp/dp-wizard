# DP Wizard

DP Wizard guides the user through the application of differential privacy.
After selecting a local CSV, users are prompted to describe to the anlysis they need.
Output options include:
- A Jupyter notebook which demonstrates how to use [OpenDP](https://docs.opendp.org/).
- A plain Python script.
- Text and CSV reports.

## Usage

```
usage: dp-wizard [-h] [--public_csv PUBLIC_CSV_PATH] [--private_csv PRIVATE_CSV_PATH] [--contrib CONTRIB] [--demo]

options:
  -h, --help            show this help message and exit
  --public_csv PUBLIC_CSV_PATH
                        Path to public CSV to be used for previews
  --private_csv PRIVATE_CSV_PATH
                        Path to private CSV: Apart from the headers, will not
                        be read until analysis is defined, and the
                        differentially private release is made.
  --contrib CONTRIB     How many rows can an individual contribute?
  --demo                Use generated fake CSV for a quick demo
```
