import pytest
import inspect
from pytest_ls.config import log
from pytest_ls.parser import should_autocomplete


class CollectionPlugin:
    def __init__(self):
        self.items = []
        self.session = None
        self.config = None

    def pytest_collection_modifyitems(self, session, config, items):
        self.items = items
        self.session = session
        self.config = config


class Brain:
    def __init__(self, cwd=None):
        self.cwd = cwd
        self._cache = {
            "tests": {},
            "fixtures": {"pytest": {}, "plugins": {}, "workspace": {}},
            "test_files": set(),
        }

    def init(self):
        plugin = CollectionPlugin()
        args = ["--fixtures", "--no-header", "--no-summary"]

        if self.cwd:
            args += [self.cwd]

        # TODO: Add a flag to optionally suppress pytest terminal output
        pytest.main(args, plugins=[plugin])
        log.info(f"Running pytest.main {args}")

        for item in plugin.items:
            self._cache["tests"][item] = True
            if hasattr(item, "path"):
                self._cache["test_files"].add(str(item.path))
            elif hasattr(item, "fspath"):
                self._cache["test_files"].add(str(item.fspath))

        # TODO: Parse this from `--fixtures`` instead? Internal API, might change between pytest versions.
        for _, fixturedefs in plugin.session._fixturemanager._arg2fixturedefs.items():
            if not fixturedefs:
                continue
            for fixture in fixturedefs:
                if fixture.func.__module__.startswith("_pytest."):
                    self._cache["fixtures"]["pytest"][fixture.func] = True
                elif fixture.func.__module__.endswith(".plugin"):
                    self._cache["fixtures"]["plugins"][fixture.func] = True
                else:
                    self._cache["fixtures"]["workspace"][fixture.func] = True
                    self._cache["test_files"].add(inspect.getfile(fixture.func))

    def list_test_files(self):
        return sorted(list(self._cache["test_files"]))

    def list_tests(self):
        return list(self._cache["tests"].keys())

    def list_fixtures(
        self, include_pytest=True, include_plugins=True, include_workspace=True
    ):
        fixtures = []
        if include_workspace:
            fixtures += list(self._cache["fixtures"]["workspace"].keys())
        if include_plugins:
            fixtures += list(self._cache["fixtures"]["plugins"].keys())
        if include_pytest:
            fixtures += list(self._cache["fixtures"]["pytest"].keys())
        return fixtures

    def _is_python_file(self, file_path):
        return file_path.endswith(".py")

    def _is_known_test_file(self, file_path):
        return file_path in self._cache["test_files"]

    def _is_test_file(self, file_path):
        return True

    def _should_suggest_completions_for_file(self, file_path):
        return self._is_python_file(file_path) and (
            self._is_known_test_file(file_path) or self._is_test_file(file_path)
        )

    def completions(self, *, column, line, file_contents, file_path):
        log.info(f"Requested completions for [{file_path} on ({line}, {column})]")
        if self._should_suggest_completions_for_file(file_path):
            log.info(f"Attempting completions for [{file_path}]")
            valid, func_name = should_autocomplete(
                line=line, column=column, file_contents=file_contents
            )
