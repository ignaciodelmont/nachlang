"""
Every example in docs/LANGUAGE.md is executed and checked against the output
the document shows for it, so the reference cannot drift from the compiler.

The convention is a fenced ```nachlang block followed directly by a fenced
```output block. A ```nachlang block without an ```output block after it is
illustrative only and is not run.
"""

import re
from pathlib import Path

import pytest

REFERENCE = Path(__file__).parent.parent / "docs" / "LANGUAGE.md"

FENCE = re.compile(r"```(\w+)\n(.*?)\n```", re.DOTALL)


def examples():
    blocks = FENCE.findall(REFERENCE.read_text(encoding="utf-8"))
    found = []
    for index, (language, body) in enumerate(blocks):
        if language != "nachlang":
            continue
        if index + 1 < len(blocks) and blocks[index + 1][0] == "output":
            expected = blocks[index + 1][1]
            found.append((body, expected.splitlines()))
    return found


EXAMPLES = examples()


def test_the_reference_has_examples():
    assert len(EXAMPLES) >= 20, "LANGUAGE.md should hold a good number of examples"


@pytest.mark.parametrize(
    "source,expected",
    EXAMPLES,
    ids=[source.strip().splitlines()[0][:40] for source, _ in EXAMPLES],
)
def test_example_prints_what_the_reference_says(nach, source, expected):
    assert nach.output(source) == expected
