# Vehicle insurance automation

Python Playwright automation for the Tricentis sample insurance application.
The shared quote workflow fills vehicle, insurant, and product data, selects the
plan from `priceOption`, and fills **Send Quote** from `quote`. It submits once
after form recovery completes, verifies **Sending e-mail success!**, and dismisses
the dialog with OK. Pytest also checks the retained input values and selected plan.
Recovery scenarios use `prepare_quote` to fill the forms without submitting.

## Setup

Run from the project root using Python 3.14 (the verified interpreter):

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m playwright install chromium
```

Configuration is read from `Config/environments/.env.<TEST_ENV>`; `TEST_ENV`
defaults to `sit`. Keep local environment files private. Set `BASE_URL` and
`ENVIRONMENT` for the target application. Process variables override file values.
The browser defaults to Chromium; set `HEADLESS=true` for headless execution.
`ACTION_DELAY` defaults to `0`: Playwright waits for actionable controls, with
explicit assertions for application readiness. Set a positive delay only when
you want slower demonstration runs. [WaitUtility.py](./Utility/WaitUtility.py)
provides the shared fixed-delay implementation used by UI actions.

## Run tests

```powershell
$env:HEADLESS = 'true'
$env:ACTION_DELAY = '0'
./.venv/Scripts/python.exe -m pytest
./.venv/Scripts/python.exe -m behave Features/create_quote.feature --tags=@smoke
```

To run only the Python quote scenario, selecting its JSON record:

```powershell
./.venv/Scripts/python.exe -m pytest E2E_Test/QuoteCreate.py --test-case TC001
```

The default record is `TC001`. Other records are used unchanged and may contain
values rejected by the application; they are not all verified positive cases.

## Do you need both Python entry points?

- [QuoteCreate.py](./E2E_Test/QuoteCreate.py) defines the reusable workflow and the
  pytest quote test. Execute it through pytest; calling it directly with Python
  does not run the test. Behave imports the same workflow.
- [run_tests.py](./run_tests.py) launches pytest, Behave, or both and generates
  Allure HTML after execution. Keep it for automatic reporting and combined
  runs. It is optional when running pytest or Behave directly.

```powershell
./.venv/Scripts/python.exe run_tests.py --runner pytest -- -m smoke
```

The reporting wrapper requires the Allure CLI. See [ALLURE.md](./ALLURE.md).

## Project layout

| Location | Purpose |
| --- | --- |
| [Config](./Config/) | Environment reader and shared project paths |
| [Data](./Data/) | JSON quote records |
| [Pages](./Pages/) | Page locators, actions, and assertions |
| [Utility](./Utility/) | UI helpers, browser lifecycle, logging, data, and reporting |
| [E2E_Test](./E2E_Test/) | Pytest quote scenario, fixtures, and reporting regression checks |
| [Features](./Features/) | Behave scenarios, steps, and lifecycle hooks |
| [.codex/skills](./.codex/skills/) | Project-specific agent guidance |

Screenshots, traces, raw Allure results, and HTML are generated under `Reports/`;
logs are generated under `Logs/`. They can be deleted between runs and are
ignored by Git. The dependency file pins direct dependencies; pip resolves their
transitive dependencies. It is not a complete environment lockfile.
