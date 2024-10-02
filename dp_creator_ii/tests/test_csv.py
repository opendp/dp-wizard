import csv
import polars as pl
import polars.testing
import tempfile
import pytest


@pytest.mark.parametrize("encoding", ["latin1", "utf8"])
def test_csv_loading(encoding):
    """
    This isn't really a test of our code: rather, it demonstrates the pattern
    we plan to follow. (Though if we do decide to require the encoding from
    the user, or use chardet to sniff the encoding, that should be tested here.)
    """
    with tempfile.NamedTemporaryFile(mode="w", newline="", encoding=encoding) as fp:
        old_lf = pl.DataFrame({"NAME": ["André"], "AGE": [42]}).lazy()

        writer = csv.writer(fp)
        writer.writerow(["NAME", "AGE"])
        for row in old_lf.collect().rows():
            writer.writerow(row)
        fp.flush()

        # w/o "ignore_errors=True" it fails outright.
        # We could ignore_errors:
        new_default_lf = pl.scan_csv(fp.name, ignore_errors=True)
        if encoding == "utf8":
            polars.testing.assert_frame_equal(old_lf, new_default_lf)
        if encoding != "utf8":
            polars.testing.assert_frame_not_equal(old_lf, new_default_lf)
            assert new_default_lf.collect().rows()[0] == (None, 42)

        # But we retain more information with utf8-lossy:
        new_lossy_lf = pl.scan_csv(fp.name, encoding="utf8-lossy")
        if encoding == "utf8":
            polars.testing.assert_frame_equal(old_lf, new_lossy_lf)
        if encoding != "utf8":
            polars.testing.assert_frame_not_equal(old_lf, new_lossy_lf)
            assert new_lossy_lf.collect().rows()[0] == ("Andr�", 42)
            # If the file even has non-utf8 characters,
            # they are probably not the only thing that distinguishes
            # two strings that we want to group on.
            # Besides grouping, we don't do much with strings,
            # so this feels safe.
