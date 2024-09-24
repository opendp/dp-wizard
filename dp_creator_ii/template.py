from pathlib import Path
import re


class _Template:
    def __init__(self, path):
        self._path = path
        template_path = Path(__file__).parent / 'templates' / path
        self._template = template_path.read_text()

    def fill_expressions(self, map={}):
        for k, v in map.items():
            self._template = self._template.replace(k, v)
        return self

    def fill_values(self, map={}):
        for k, v in map.items():
            self._template = self._template.replace(k, repr(v))
        return self

    def fill_blocks(self, map={}):
        for k, v in map.items():
            k_re = re.escape(k)
            self._template = re.sub(
                rf'^(\s*){k_re}$',
                lambda match: '\n'.join(
                    match.group(1) + line for line in v.split('\n')),
                self._template,
                flags=re.MULTILINE)
        return self

    def __str__(self):
        unfilled = set(re.findall(r'[A-Z][A-Z_]+', self._template))
        if unfilled:
            raise Exception(
                f'Template {self._path} has unfilled slots: '
                f'{", ".join(sorted(unfilled))}\n\n{self._template}')
        return self._template


def _make_context_for_notebook(csv_path, unit, loss, weights):
    return str(_Template('context.py').fill_values({
        'CSV_PATH': csv_path,
        'UNIT': unit,
        'LOSS': loss,
        'WEIGHTS': weights
    }))


def _make_context_for_script(unit, loss, weights):
    return str(_Template('context.py').fill_expressions({
        'CSV_PATH': 'csv_path'
    }).fill_values({
        'UNIT': unit,
        'LOSS': loss,
        'WEIGHTS': weights
    }))


def _make_imports():
    return str(_Template('imports.py').fill_values())


def make_notebook(csv_path, unit, loss, weights):
    return str(_Template('notebook.py').fill_blocks({
        'IMPORTS_BLOCK': _make_imports(),
        'CONTEXT_BLOCK': _make_context_for_notebook(
            csv_path=csv_path,
            unit=unit,
            loss=loss,
            weights=weights
        )
    }))


def make_script(unit, loss, weights):
    return str(_Template('script.py').fill_blocks({
        'IMPORTS_BLOCK': _make_imports(),
        'CONTEXT_BLOCK': _make_context_for_script(
            unit=unit,
            loss=loss,
            weights=weights
        )
    }))
