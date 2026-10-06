import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from catalog.labels import label


def test_label():
    assert label("a") == "a"


if __name__ == "__main__":
    test_label()
