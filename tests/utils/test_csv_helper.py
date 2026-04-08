import csv
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import polars as pl
import polars.testing as pl_testing
import pytest

from dp_wizard.utils.csv_helper import (
    CsvInfo,
    convert_text,
    get_csv_names_mismatch,
    get_csv_row_count,
)

csv_fixtures = [
    # No error! and type inference:
    (b"str,int\nX,1", "str,int", "int", None, False),
    #
    # NO WARNING (but might be better if there were...)
    #
    # more column headers than values below:
    (b"A,B,C,D\n1,2\n3,4", "A,B,C,D", "A,B", None, False),
    # fewer column headers than values below:
    (b"A,B\n1,2,3,4\n5,6,7,8", "A,B", "A,B", None, False),
    # totally empty:
    (b"", "", "", None, False),
    #
    # WARNINGS
    #
    # skip empty column header:
    (b",int\nX,1", "int", "int", "Only one column detected", False),
    # if a header is a number, might be missing header row:
    (b"A,1\nB,2", "A,1", "1", "Numeric column name", False),
    # padded values:
    (
        b" str , int \n X , 1 ",
        " str , int ",
        "",
        "Column name is padded",
        False,
    ),
    # actually pipe-delim:
    (b"str|int\nX|1", "str|int", "", "Only one column detected", False),
    # no numbers:
    (b"A,B,C\na,b,c", "A,B,C", "", "No numeric columns detected", False),
    # duplicate header gets suffix from polars:
    (
        b"dup,dup\nX,1",
        "dup,dup_duplicated_0",
        "dup_duplicated_0",
        "Column name modified",
        False,
    ),
    #
    # ERRORS
    #
    # empty header row:
    (b",\nX,1", "", "", "No column names detected", True),
]


@pytest.mark.parametrize(
    "suffix,content_bytes,all,numeric,message_substring,is_error",
    [(".csv", *fix) for fix in csv_fixtures]
    + [(".tsv", fix[0].replace(b",", b"\t"), *(fix[1:])) for fix in csv_fixtures]
    + [
        # Bad extension:
        (".txt", b"", "", "", "Expected .tsv or .tab, not", True),
        # CSV actually TSV:
        (".csv", b"str\tint\nX\t1", "", "", "Tab in column name", True),
        # CSV actually binary:
        (".csv", b"\xff\xff\n\x00\x00", "", "", "Bad column name", True),
        # TSV actually CSV:
        # TODO: Currently a warning, not an error.
        (
            ".tsv",
            b"str,int\nX,1",
            "str,int",
            "",
            "Only one column detected: 'str,int'",
            False,
        ),
        # TSV actually binary:
        (".tsv", b"\xff\xff\n\x00\x00", "", "", "invalid start byte", True),
    ],
)
def test_csv_info(suffix, content_bytes, all, numeric, message_substring, is_error):
    assert message_substring != ""  # programmer error!
    with TemporaryDirectory() as dir:
        path = Path(dir) / f"fake{suffix}"
        path.write_bytes(content_bytes)
        # CsvInfo may write a new, converted, CSV in the directory,
        # so we need a temp dir, and not just a temp file.
        csv_info = CsvInfo(path)
        assert all == ",".join(csv_info.get_all_column_names())
        assert numeric == ",".join(csv_info.get_numeric_column_names())
        if message_substring is None:
            assert not csv_info.get_messages()
        else:
            assert message_substring in "; ".join(csv_info.get_messages())
        assert csv_info.get_is_error() == is_error


def test_csv_info_none():
    csv_info = CsvInfo(None)
    assert csv_info.get_all_column_names() == []
    assert csv_info.get_numeric_column_names() == []
    assert csv_info.get_messages() == []


def test_csv_info_no_such_file():
    csv_info = CsvInfo(Path("no-such-file.csv"))
    assert csv_info.get_messages() == ["No such file: no-such-file.csv"]


def make_sparse_file(path: Path, size_in_mb: int):
    """
    >>> with NamedTemporaryFile() as tmp:
    ...     path = Path(tmp.name)
    ...     make_sparse_file(path, 1)
    ...     print('reported size:', path.stat().st_size)
    ...     print('blocks used:', path.stat().st_blocks)
    reported size: 1048576
    blocks used: 0
    """
    f = path.open("ab")
    f.truncate(size_in_mb * 1024 * 1024)
    f.close()


@pytest.mark.parametrize(
    "size_in_mb,is_error,message_0",
    [
        (1, False, "No numeric columns detected."),
        (11, False, "Files larger than 10M may be slow to process."),
        (
            101,
            True,
            "DP Wizard is an interactive tool, and 101M would be too slow. "
            "DP Wizard is limited to 100M, although "
            "the OpenDP Library itself doesn't have such a limit.",
        ),
    ],
)
def test_csv_info_large(size_in_mb, is_error, message_0):
    with TemporaryDirectory() as dir:
        path = Path(dir) / "fake.csv"
        make_sparse_file(path, size_in_mb)
        csv_info = CsvInfo(path)
        assert csv_info.get_is_error() == is_error
        assert csv_info.get_messages()[0] == message_0


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
    with NamedTemporaryFile(mode="w", suffix=".csv") as tmp:
        tmp.write(f"{column_name}\n{value}")
        tmp.flush()
        csv_info = CsvInfo(Path(tmp.name))
    assert csv_info.get_schema()[column_name] == datatype  # type: ignore

    expected = value_datatype.pop(0) if value_datatype else value  # type: ignore
    actual = convert_text(value, datatype)[0]  # type: ignore
    assert actual == expected


def test_get_csv_names_mismatch():
    with TemporaryDirectory() as tmp:
        a_path = Path(tmp) / "a.csv"
        a_path.write_text("a,b,c")
        b_path = Path(tmp) / "b.csv"
        b_path.write_text("b,c,d")
        just_a, just_b = get_csv_names_mismatch(a_path, b_path)
        assert just_a == {"a"}
        assert just_b == {"d"}


def test_get_csv_row_count():
    with TemporaryDirectory() as tmp:
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
    with NamedTemporaryFile(mode="w", newline="", encoding=write_encoding) as fp:
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
