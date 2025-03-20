import pytest
from dp_wizard.utils.code_template import Template


def test_param_conflict():
    with pytest.raises(Exception, match=r"mutually exclusive"):
        Template("context", template="Not allowed if path present")


def test_fill_expressions():
    template = Template(None, template="No one VERB the ADJ NOUN!")
    filled = template.fill_expressions(
        VERB="expects",
        ADJ="Spanish",
        NOUN="Inquisition",
    ).finish()
    assert filled == "No one expects the Spanish Inquisition!"


def test_fill_expressions_missing_slot_in_template():
    template = Template(None, template="No one ... the ADJ NOUN!")
    with pytest.raises(Exception, match=r"No 'VERB' slot to fill with 'expects'"):
        template.fill_expressions(
            VERB="expects",
            ADJ="Spanish",
            NOUN="Inquisition",
        ).finish()


def test_fill_expressions_extra_slot_in_template():
    template = Template(None, template="No one VERB ARTICLE ADJ NOUN!")
    with pytest.raises(Exception, match=r"'ARTICLE' slot not filled"):
        template.fill_expressions(
            VERB="expects",
            ADJ="Spanish",
            NOUN="Inquisition",
        ).finish()


def test_fill_values():
    template = Template(None, template="assert [STRING] * NUM == LIST")
    filled = template.fill_values(
        STRING="🙂",
        NUM=3,
        LIST=["🙂", "🙂", "🙂"],
    ).finish()
    assert filled == "assert ['🙂'] * 3 == ['🙂', '🙂', '🙂']"


def test_fill_values_missing_slot_in_template():
    template = Template(None, template="assert [STRING] * ... == LIST")
    with pytest.raises(Exception, match=r"No 'NUM' slot to fill with '3'"):
        template.fill_values(
            STRING="🙂",
            NUM=3,
            LIST=["🙂", "🙂", "🙂"],
        ).finish()


def test_fill_values_extra_slot_in_template():
    template = Template(None, template="CMD [STRING] * NUM == LIST")
    with pytest.raises(Exception, match=r"'CMD' slot not filled"):
        template.fill_values(
            STRING="🙂",
            NUM=3,
            LIST=["🙂", "🙂", "🙂"],
        ).finish()


def test_fill_blocks():
    # "OK" is less than three characters, so it is not a slot.
    template = Template(
        None,
        template="""# MixedCase is OK

FIRST

with fake:
    SECOND
    if True:
        THIRD
""",
    )
    template.fill_blocks(
        FIRST="\n".join(f"import {i}" for i in "abc"),
        SECOND="\n".join(f"f({i})" for i in "123"),
        THIRD="\n".join(f"{i}()" for i in "xyz"),
    )
    assert (
        template.finish()
        == """# MixedCase is OK

import a
import b
import c

with fake:
    f(1)
    f(2)
    f(3)
    if True:
        x()
        y()
        z()
"""
    )


def test_fill_blocks_missing_slot_in_template_alone():
    template = Template(None, template="No block slot")
    with pytest.raises(Exception, match=r"No 'SLOT' slot"):
        template.fill_blocks(SLOT="placeholder").finish()


def test_fill_blocks_missing_slot_in_template_not_alone():
    template = Template(None, template="No block SLOT")
    with pytest.raises(
        Exception, match=r"Block slots must be alone on line; No 'SLOT' slot"
    ):
        template.fill_blocks(SLOT="placeholder").finish()


def test_fill_blocks_extra_slot_in_template():
    template = Template(None, template="EXTRA\nSLOT")
    with pytest.raises(Exception, match=r"'EXTRA' slot not filled"):
        template.fill_blocks(SLOT="placeholder").finish()


def test_fill_blocks_not_string():
    template = Template(None, template="SOMETHING")
    with pytest.raises(
        Exception,
        match=r"For SOMETHING in template-instead-of-path, expected string, not 123",
    ):
        template.fill_blocks(SOMETHING=123).finish()
