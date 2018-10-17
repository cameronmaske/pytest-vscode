import { parse, shouldSuggest } from "../parse";

test("parses pytest fixture ouput", function() {
  const output = `cache
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
  expect(parse(output)).toEqual([
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

test("should test - true", () => {
  expect(shouldSuggest("def test_example()", 17)).toBe(true);
});

test("should test - false", () => {
  expect(shouldSuggest("def example()", 12)).toBe(false);
});
