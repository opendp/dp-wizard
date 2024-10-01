import csv
import polars as pl
import polars.testing
import tempfile
import pytest


@pytest.mark.parametrize("encoding", ["latin1", "utf8"])
def test_csv_loading(encoding):
    with tempfile.NamedTemporaryFile(
        delete_on_close=False, mode="w", newline="", encoding=encoding
    ) as fp:
        old_lf = pl.DataFrame({"NAME": ["André"], "AGE": [42]}).lazy()

        writer = csv.writer(fp)
        writer.writerow(["NAME", "AGE"])
        for row in old_lf.collect().rows():
            writer.writerow(row)
        fp.close()

        new_lf = pl.scan_csv(fp.name, encoding="utf8-lossy")
        if encoding == "utf8":
            polars.testing.assert_frame_equal(old_lf, new_lf)
        if encoding != "utf8":
            polars.testing.assert_frame_not_equal(old_lf, new_lf)
            assert new_lf.collect().rows()[0] == ("Andr�", 42)
            # If the file even has non-utf8 characters,
            # they are probably not the only thing that distinguishes
            # two strings that we want to group on.
            # Besides grouping, we don't do much with strings,
            # so this feels safe.
