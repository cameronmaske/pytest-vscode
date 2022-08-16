from pytest_ls.brain import Brain


def test_brain_init(root_path):
    brain = Brain(cwd=root_path)

    brain.init()

    assert [(func.name, func.module.__name__) for func in brain.list_tests()] == [
        ("test_bar", "workspace.test_classes"),
        ("test_autocomplete", "workspace.test_simple"),
        ("test_foo", "workspace.test_simple"),
        ("test_foo", "workspace.nested.test_nested"),
    ]

    assert [
        (func.__name__, func.__module__)
        for func in brain.list_fixtures(
            include_pytest=False, include_plugins=False, include_workspace=True
        )
    ] == [
        ("foo_in_conftest", "workspace.conftest"),
        ("foo_in_file", "workspace.test_simple"),
        ("fuzz_in_file", "workspace.test_simple"),
        ("a", "workspace.nested.test_nested"),
        ("c", "workspace.nested.test_nested"),
    ]

    assert brain.list_test_files() == [
        str(root_path / "conftest.py"),
        str(root_path / "nested/test_nested.py"),
        str(root_path / "test_classes.py"),
        str(root_path / "test_simple.py"),
    ]
