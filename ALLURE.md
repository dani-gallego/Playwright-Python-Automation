# Allure reports

[run_tests.py](./run_tests.py) runs pytest, Behave, or both and generates HTML
**after execution completes**, including when tests fail. It preserves a failing
test exit code and returns a failure if report generation fails.

## Setup

Use the Python environment prepared in [README.md](./README.md). The Allure Report
CLI must be available as `allure` on PATH; the Python adapters alone do not
produce HTML. The runner checks for the CLI before launching tests.

## Execute and generate

From the project root:

```powershell
$env:HEADLESS = 'true'
$env:ACTION_DELAY = '0'
./.venv/Scripts/python.exe run_tests.py
```

| Command arguments after `run_tests.py` | What runs | Allure entries |
| --- | --- | ---: |
| No arguments, or `--runner all` | All pytest tests and Behave scenarios | Varies |
| `--runner pytest` | Quote, recovery, submission, and reporting checks | Varies |
| `--runner pytest -- -m smoke` | Only the pytest quote test | 1 |
| `--runner pytest -- -m smoke --test-case TC001` | The pytest quote test with the specified JSON record | 1 |
| `--runner behave` | Quote submission and recovery scenarios | 2 |
| `--runner behave -- --tags=@smoke` | Behave scenarios tagged smoke | 1 |

Pytest executes [QuoteCreate.py](./E2E_Test/QuoteCreate.py); Behave executes
[create_quote.feature](./Features/create_quote.feature), whose steps call the
same quote workflow. Both fill vehicle, insurant, and product data, select the
plan from `priceOption`, fill `quote`, submit once, and verify the success message
and its dismissal. Recovery scenarios fill without submitting. Pytest also
verifies retained input values and the selected plan. Running both frameworks
exercises the workflow twice. Reporting checks live in
[test_allure_runner.py](./E2E_Test/test_allure_runner.py) and also appear in Allure.

The `--` separator forwards options to the selected framework. Extra options
require `--runner pytest` or `--runner behave`. Pytest selects a record from
[CreateQuoteData.json](./Data/CreateQuoteData.json) using `--test-case` (default
`TC001`); Behave selects the ID in its feature's When step. Records are used
unchanged, and records rejected by the application fail their tests.

Framework processes use Python UTF-8 mode so Windows can print Unicode icons
included in Playwright assertion errors.

## Output

- `Reports/allure-report/` contains the latest invocation's HTML, starting at
  `index.html`. Each generation replaces this generated report.
- `Reports/allure-results/` retains raw results in a timestamped directory per
  invocation, with separate framework subdirectories. Only the latest
  invocation contributes to its HTML report.
- Screenshots and finalized traces are attached to tests, with standalone copies
  retained under `Reports/`.

View the report with `allure open Reports/allure-report`.

Direct pytest or Behave commands bypass HTML generation. For example,
`python -m pytest --alluredir Reports/allure-results/manual` collects raw data
only. Automatic HTML generation belongs in the wrapper because Behave's
formatter closes after its `after_all` hook.

[ProjectPaths.py](./Config/ProjectPaths.py) defines the shared project root, data,
logs, reports, raw Allure results, and HTML locations independently of the
terminal's working directory.
