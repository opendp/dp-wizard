#!/bin/bash

# Test is parameterized: We only need one pass, so download the README.
SCREENSHOTS=1 pytest -k 'test_local_app_downloads and README' -vv
