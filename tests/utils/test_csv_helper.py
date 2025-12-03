import csv
import tempfile
from pathlib import Path

import polars as pl
import polars.testing as pl_testing
import pytest

from dp_wizard.utils.csv_helper import (
    convert_text,
    get_csv_names_mismatch,
    get_csv_row_count,
    read_polars_schema,
)


@pytest.mark.parametrize(  # type: ignore
    "value_datatype",
    [
        ["abc", pl.String],
        ["-0", pl.Int64, 0],
        ["123", pl.Int64, 123],
        ["   123", pl.String, "123"],
        ["123   ", pl.String, "123"],
        ["123.456", pl.Float64, 123.456],
        ["1e2", pl.Float64, 100.0],
        ["tRuE", pl.Boolean, True],
        ["01-01-2001", pl.String],
        ["01:00", pl.String],
    ],
    ids=str,
)
def test_datatype_inference(value_datatype):  # type: ignore
    value: str = value_datatype.pop(0)  # type: ignore
    datatype = value_datatype.pop(0)  # type: ignore
    column_name = "col"
    schema = read_polars_schema(f"{column_name}\n{value}".encode())
    assert schema[column_name] == datatype  # type: ignore

    expected = value_datatype.pop(0) if value_datatype else value  # type: ignore
    actual = convert_text(value, datatype)[0]  # type: ignore
    assert actual == expected


def test_get_csv_names_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        a_path = Path(tmp) / "a.csv"
        a_path.write_text("a,b,c")
        b_path = Path(tmp) / "b.csv"
        b_path.write_text("b,c,d")
        just_a, just_b = get_csv_names_mismatch(a_path, b_path)
        assert just_a == {"a"}
        assert just_b == {"d"}


def test_get_csv_row_count():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "a.csv"
        path.write_text("a,b,c\n1,2,3")
        assert get_csv_row_count(path) == 1


# We will not reference the encoding when reading:
# We need to be robust against any input.
#
# TODO: Reenable "utf-8-sig" test.
# Was hitting weird error:
# https://github.com/opendp/opendp/issues/2298
@pytest.mark.parametrize("write_encoding", ["latin1", "utf8"])
def test_csv_loading(write_encoding):
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", encoding=write_encoding
    ) as fp:
        data = {"NAME": ["André"], "AGE": [42]}
        write_lf = pl.DataFrame(data).lazy()

        writer = csv.writer(fp)
        writer.writerow(data.keys())
        for row in write_lf.collect().rows():
            writer.writerow(row)
        fp.flush()

        # NOT WHAT WE'RE DOING!
        # w/o "ignore_errors=True" it fails outright for latin1.
        read_lf = pl.scan_csv(fp.name)
        if write_encoding == "latin1":
            with pytest.raises(pl.exceptions.ComputeError):
                read_lf.collect()

        # ALSO NOT WHAT WE'RE DOING!
        # w/ "ignore_errors=True" but w/o "utf8-lossy" it also fails.
        read_lf = pl.scan_csv(fp.name, ignore_errors=True)
        if write_encoding == "latin1":
            with pytest.raises(pl.exceptions.ComputeError):
                read_lf.collect()

        # THIS IS THE RIGHT PATTERN!
        # Not perfect, but "utf8-lossy" retains as much info as possible.
        # "ignore_errors" true will skip values that don't match inferred type.
        read_lf = pl.scan_csv(fp.name, encoding="utf8-lossy", ignore_errors=True)
        if write_encoding == "latin1":
            # Not equal, but the only differce is the "�".
            pl_testing.assert_frame_not_equal(write_lf, read_lf)
            assert read_lf.collect().rows()[0] == ("Andr�", 42)
        else:
            pl_testing.assert_frame_equal(write_lf, read_lf)
