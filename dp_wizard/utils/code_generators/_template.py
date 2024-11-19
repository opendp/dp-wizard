import re
from pathlib import Path


class Template:
    def __init__(self, path, template=None):
        if path is not None:
            self._path = f"_{path}.py"
            template_path = Path(__file__).parent / "no-tests" / self._path
            self._template = template_path.read_text()
        if template is not None:
            if path is not None:
                raise Exception('"path" and "template" are mutually exclusive')
            self._path = "template-instead-of-path"
            self._template = template
        # We want a list of the initial slots, because substitutions
        # can produce sequences of upper case letters that could be mistaken for slots.
        self._initial_slots = self._find_slots()

    def _find_slots(self):
        # Slots:
        # - are all caps or underscores
        # - have word boundary on either side
        # - are at least three characters
        slot_re = r"\b[A-Z][A-Z_]{2,}\b"
        return set(re.findall(slot_re, self._template))

    def fill_expressions(self, **kwargs):
        for k, v in kwargs.items():
            k_re = re.escape(k)
            self._template, count = re.subn(rf"\b{k_re}\b", str(v), self._template)
            if count == 0:
                raise Exception(f"No slot for '{k}' in {self._path}")
        return self

    def fill_values(self, **kwargs):
        for k, v in kwargs.items():
            k_re = re.escape(k)
            self._template, count = re.subn(rf"\b{k_re}\b", repr(v), self._template)
            if count == 0:
                raise Exception(f"No slot for '{k}' in {self._path}")
        return self

    def fill_blocks(self, **kwargs):
        for k, v in kwargs.items():

            def match_indent(match):
                # This does what we want, but binding is confusing.
                return "\n".join(
                    match.group(1) + line for line in v.split("\n")  # noqa: B023
                )

            k_re = re.escape(k)
            self._template = re.sub(
                rf"^([ \t]*){k_re}$",
                match_indent,
                self._template,
                flags=re.MULTILINE,
            )
        return self

    def __str__(self):
        unfilled_slots = self._initial_slots & self._find_slots()
        if unfilled_slots:
            raise Exception(
                f"Template {self._path} has unfilled slots: "
                f'{", ".join(sorted(unfilled_slots))}\n\n{self._template}'
            )
        return self._template
