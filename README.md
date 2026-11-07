# QA Report Bot

![CI](https://github.com/rudrasurti/qa-report-bot/actions/workflows/ci.yml/badge.svg)

A GitHub Action that reads JUnit XML test results and posts a short report on every pull request: passed, failed, skipped, **flaky** tests and run time. It updates one comment instead of adding a new one on every push, and also writes the report to the job summary.

Works with any tool that writes JUnit XML: Robot Framework (`--xunit`), Playwright (`junit` reporter), pytest (`--junitxml`), TestNG, Jest and more.

## Example comment

> ### UI tests
> **❌ 1 test(s) failed**
>
> | Total | Passed | Failed | Skipped | Flaky | Time |
> |---|---|---|---|---|---|
> | 3 | 2 | 1 | 0 | 1 | 4.4s |
>
> ⚠️ **Flaky tests** (failed, then passed on retry): `cart::add item`

## Usage

```yaml
permissions:
  contents: read
  pull-requests: write

steps:
  - uses: actions/checkout@v4
  - run: npx playwright test --reporter=junit
    env:
      PLAYWRIGHT_JUNIT_OUTPUT_NAME: results/junit.xml
  - uses: rudrasurti/qa-report-bot@main
    if: always()
    with:
      junit-path: results/*.xml
      title: UI tests
      fail-on-failure: "true"
```

| Input | Default | Description |
|---|---|---|
| `junit-path` | required | Glob for JUnit XML files |
| `title` | `Test results` | Report heading |
| `github-token` | `github.token` | Token used to comment |
| `fail-on-failure` | `false` | Fail the step when tests failed |

Output: `failed`, the number of failed tests.

## How flaky detection works

When the same test appears more than once in a run (the retry pattern), and its last result is a pass after an earlier failure, it is listed as flaky. Flaky tests count as passed but are called out so the team can fix them.

## Development

```bash
pip install pytest
python -m pytest -q tests
python3 report.py --junit "tests/fixtures/*.xml"
```

CI runs the unit tests, then runs the action itself on sample passing and failing results.

---

**Rudra Surti** · Senior SDET · [Website](https://rudrasurti.github.io) · [LinkedIn](https://www.linkedin.com/in/rudra-surti/)
