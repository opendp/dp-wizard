from pathlib import Path


class _Template:
    def __init__(self, path):
        template_path = Path(__file__).parent / 'templates' / path
        self.template = template_path.read_text()

    def fill_values(self, map={}):
        filled = self.template
        for k, v in map.items():
            filled = filled.replace(k, repr(v))
        return filled

    def fill_code(self, map={}):
        filled = self.template
        for k, v in map.items():
            # TODO: preserve indentation
            filled = filled.replace(k, v)
        return filled


def _make_context(csv_path, unit, loss, weights):
    return _Template('context.py').fill_values({
        'CSV_PATH': csv_path,
        'UNIT': unit,
        'LOSS': loss,
        'WEIGHTS': weights
    })


def _make_imports():
    return _Template('imports.py').fill_values()


def _make_code(template, csv_path, unit, loss, weights):
    return _Template(template).fill_code({
        'IMPORTS_CODE': _make_imports(),
        'CONTEXT_CODE': _make_context(
            csv_path=csv_path,
            unit=unit,
            loss=loss,
            weights=weights
        )
    })


def make_script(csv_path, unit, loss, weights):  # pragma: no cover
    return _make_code(
        'script.py',
        csv_path=csv_path,
        unit=unit,
        loss=loss,
        weights=weights
    )


def make_notebook(csv_path, unit, loss, weights):
    return _make_code(
        'notebook.py',
        csv_path=csv_path,
        unit=unit,
        loss=loss,
        weights=weights
    )
