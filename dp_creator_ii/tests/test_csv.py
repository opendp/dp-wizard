import csv
import polars as pl
import polars.testing
import tempfile
import pytest


@pytest.mark.parametrize("encoding", ["latin1", "utf8"])
def test_csv_loading(encoding):
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", newline="", encoding=encoding
    ) as fp:
        # By default, would delete file on "close()";
        # With "delete=False", clean up when exiting "with" instead.
        old_lf = pl.DataFrame({"NAME": ["André"], "AGE": [42]}).lazy()

        writer = csv.writer(
            fp,
        )
        writer.writerow(["NAME", "AGE"])
        for row in old_lf.collect().rows():
            writer.writerow(row)
        fp.close()

        new_lf = pl.scan_csv(fp.name)
        polars.testing.assert_frame_equal(old_lf, new_lf)
