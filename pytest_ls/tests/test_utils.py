from pytest_ls.utils import file_path_split


def test_file_path_split():
    assert file_path_split("/abc/d/foo/test.py") == ("/abc/d/foo/", "test", ".py")
