import parso
import fnmatch
from typing import Tuple, Optional


def should_autocomplete(
    column: int, line: int, file_contents: str
) -> Tuple[bool, Optional[str]]:
    try:
        leaf = parso.parse(file_contents).get_leaf_for_position((line, column))
        if leaf is not None:
            if leaf.parent.type == "parameters":
                if leaf.parent.parent.type == "funcdef":
                    func_name = leaf.parent.parent.name.value
                    if (
                        leaf.parent.parent.parent.parent is not None
                        and leaf.parent.parent.parent.parent.type == "classdef"
                    ):
                        class_name = leaf.parent.parent.parent.parent.name.value
                        return True, f"{class_name}.{func_name}"
                    return True, func_name
    except ValueError:
        pass
    return False, None


def is_test_file(filename, file_globs=["test_*.py"]):
    if filename == "conftest.py":
        return True

    for glob in file_globs:
        if fnmatch.fnmatch(filename, glob):
            return True
    return False
