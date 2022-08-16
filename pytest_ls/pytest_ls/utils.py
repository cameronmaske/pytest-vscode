import fnmatch
from typing import Tuple
from pathlib import Path


def matches_glob(value, globs):
    for glob in globs:
        if fnmatch.fnmatch(value, glob):
            return True
    return False


def file_path_split(file_path) -> Tuple[str, str, str]:
    path = Path(file_path)
    return str(path.parent) + "/", path.stem, path.suffix
