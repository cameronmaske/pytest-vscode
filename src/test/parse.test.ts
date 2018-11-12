import { parseOutput, parseCommand, shouldSuggest } from "../parse";
import { expect } from "chai";

const PYTEST_OUTPUT = `cache
    Return a cache object that can persist state between testing sessions.

------------------------------------------------------- fixtures defined from pytest_django.fixtures -------------------------------------------------------
db
    Require a django test database.

    This database will be setup with the default fixtures and will have
------- fixtures defined from tests.unit_tests.journal.test_permissions --------
fixture_1
    tests/unit_tests/journal/test_permissions.py:13: no docstring available
fixture_2
    This is a docstring
========================= no tests ran in 0.22 seconds =========================`;

test("parses pytest fixture ouput", function() {
  expect(parseOutput(PYTEST_OUTPUT)).to.deep.equal([
    {
      name: "cache",
      docstring:
        "Return a cache object that can persist state between testing sessions."
    },
    {
      name: "db",
      docstring: `Require a django test database.\n\nThis database will be setup with the default fixtures and will have`
    },
    {
      name: "fixture_1",
      docstring: null
    },
    {
      name: "fixture_2",
      docstring: "This is a docstring"
    }
  ]);
});

test("should suggest, inside brackets", () => {
  expect(shouldSuggest("def test_example()", 17)).to.equal(true);
});

test("should suggest, after first bracket", () => {
  expect(shouldSuggest("def test_example(", 17)).to.equal(true);
});

test("should not suggest, cursor before brackets", () => {
  expect(shouldSuggest("def test_example()", 12)).to.equal(false);
});

test("should not suggest, cursor after brackets", () => {
  expect(shouldSuggest("def test_example()", 18)).to.equal(false);
});

test("should not suggest, not test function", () => {
  expect(shouldSuggest("def example()", 12)).to.equal(false);
});

test("should generate commands", () => {
  const path = "pipenv run pytest";
  expect(parseCommand(path)).to.deep.equal({
    cmd: "pipenv",
    args: ["run", "pytest"]
  });
});
