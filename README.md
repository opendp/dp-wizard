# DP Creator II

**Under Construction**

Building on what we've learned from [DP Creator](https://github.com/opendp/dpcreator), DP Creator II will offer:

- Easy installation with `pip install`
- Simplified single-user application design
- Streamlined workflow that doesn't assume familiarity with differential privacy
- Interactive visualization of privacy budget choices
- UI development in Python with [Shiny](https://shiny.posit.co/py/)
- Tracking of cumulative privacy consumption between sessions

## Development

Clone the repo and set up a virtual environment:
```
git clone https://github.com/opendp/dp-creator-ii.git
cd dp-creator-ii
python3 -m venv .venv
pip install -r requirements-dev.txt
```

Branch names should be of the form `NNNN-short-description`, where `NNNN` is the issue number being addressed.

Dependencies should be pinned for development, but not pinned when the package is installed.
New dev dependencies can be added to `requirements-dev.in`, and then run `pip-compile requirements-dev.in` to update `requirements-dev.in`
