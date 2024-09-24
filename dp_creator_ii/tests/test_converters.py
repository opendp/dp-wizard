import re
from pathlib import Path
from dp_creator_ii.converters import convert_py_to_nb


def test_convert_py_to_nb():
    fixtures_path = Path('dp_creator_ii/tests/fixtures')
    python_str = (fixtures_path / 'fake.py').read_text()
    actual_nb_str = convert_py_to_nb(python_str)
    expected_nb_str = (fixtures_path / 'fake.ipynb').read_text()

    def norm_nb(nb_str):
        normed_nb_str = re.sub(r'"id": "[^"]+"', '"id": "12345678"', nb_str)
        return normed_nb_str

    normed_actual_nb_str = norm_nb(actual_nb_str)
    normed_expected_nb_str = norm_nb(expected_nb_str)
    assert normed_actual_nb_str == normed_expected_nb_str
