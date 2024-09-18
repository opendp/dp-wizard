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

### Getting Started

To get started, clone the repo and install dev dependencies:
```
git clone https://github.com/opendp/dp-creator-ii.git
cd dp-creator-ii
python3 -m venv .venv
pip install -r requirements-dev.txt
```

Now install the application itself locally and run it:
```
flit install --symlink
dp-creator-ii
```
You should see a webserver start, along with a prompt to connect to http://127.0.0.1:8000/.

### Conventions

Branch names should be of the form `NNNN-short-description`, where `NNNN` is the issue number being addressed.

Dependencies should be pinned for development, but not pinned when the package is installed.
New dev dependencies can be added to `requirements-dev.in`, and then run `pip-compile requirements-dev.in` to update `requirements-dev.in`
