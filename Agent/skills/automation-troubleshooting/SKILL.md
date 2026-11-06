---
name: automation-troubleshooting
description: Run or troubleshoot this project's Python Behave and Playwright automation, including browser hooks, environment selection, imports, timeouts, screenshots, and Allure output. Use for execution failures or configuration changes rather than authoring scenarios or maintaining quote data.
---

# Run and troubleshoot automation

Work from the project root. Follow the first relevant failure through configuration, Behave context, workflow, and UI helpers instead of changing locators before browser setup is working.

## Establish the runtime

- Dependencies are pinned in [requirements.txt](../../../requirements.txt). Use the intended Python interpreter and inspect missing modules before installing packages. The project uses synchronous Python Playwright with both pytest and Behave; [pytest.ini](../../../pytest.ini) discovers tests in the E2E directory.
- [Utilities.py](../../../Utility/Utilities.py) and [AllureReport.py](../../../Utility/AllureReport.py) import `allure` at module load time. A missing `allure` import can prevent step loading even when no report is requested. Check the declared `allure-python-commons` and `allure-behave` dependencies before attributing this to Behave discovery.
- Run commands against the explicit, case-correct [Features directory](../../../Features), because that is the directory present in this project.

Useful commands, chosen according to the requested task:

```powershell
python -m pip show behave playwright allure-python-commons allure-behave python-dotenv
$env:HEADLESS = 'true'
$env:ACTION_DELAY = '0'
python -m pytest -m smoke --junitxml=Reports/pytest-results.xml
python -m behave Features/create_quote.feature --dry-run
python -m behave Features/create_quote.feature --tags=@smoke
```

If dependencies are missing, the installation source is `python -m pip install -r requirements.txt`. If the selected browser executable is missing, install that browser with the same interpreter, for example `python -m playwright install chromium`. Do not install unrelated packages or assume Chromium is the configured browser.

## Check hooks before UI failures

Inspect [environment.py](../../../Features/environment.py), [conftest.py](../../../E2E_Test/conftest.py), and [BrowserSession.py](../../../Utility/BrowserSession.py) together. Both runners now use the same browser session utility; the original debug-only hooks have been replaced. Each scenario receives a fresh browser context and page, with tracing and timeouts configured before execution.

The Given step requires both `context.page` and an environment object exposing `.base_url`. A missing `context.page` or an attribute error on `environment_config` is a lifecycle failure, not a selector failure.

When changing lifecycle behavior, preserve cleanup after partial setup and stop tracing before closing the context and browser. `BrowserSession` registers cleanup using `ExitStack`; the runners capture screenshots before exiting the session. Inspect the actual hook or fixture failure before changing selectors.

## Resolve environment settings

[EnvironmentConfig.py](../../../Config/EnvironmentConfig.py) imports the single [ConfigReader.py](../../../Config/ConfigReader.py). The unused duplicate reader was removed.

The active reader selects `Config/environments/.env.<environment>` using the process variable `TEST_ENV`, defaulting to `sit` and lowercasing the value. [The SIT environment file](../../../Config/environments/.env.sit) is currently the only environment file. The `ENVIRONMENT` setting is a reported value, not the file selector. `load_dotenv` is called without `override=True`, so existing process variables take precedence. Settings load once per Python process through `_loaded`.

To select SIT for a run in PowerShell:

```powershell
$env:TEST_ENV = 'sit'
python -m behave Features/create_quote.feature --tags=@smoke
```

`ENVIRONMENT`, `BASE_URL`, `USERNAME`, and `PASSWORD` are required when their respective properties are read. Browser defaults to `chromium`, headless to false, default timeout to 30000 milliseconds, and navigation timeout to 60000 milliseconds. Boolean parsing accepts `true`, `1`, `yes`, or `y`, ignoring case. Integer settings must parse as integers.

`ACTION_DELAY` controls [Utilities.wait_after_action](../../../Utility/Utilities.py) when no explicit argument is passed and defaults to `0`. This method delegates to [WaitUtility.py](../../../Utility/WaitUtility.py), the shared implementation for fixed delays. Keep this helper, as requested by the user. Avoid adding sleeps to hide missing readiness conditions; use a positive delay only for deliberately slower demonstration runs.

## Use execution evidence accurately

- [Logger.py](../../../Utility/Logger.py) creates timestamped files under the project-root `Logs/` directory using `PROJECT_PATHS.logs`.
- The runners save final or failure screenshots and traces in timestamped subdirectories under [Reports](../../../Reports), using [BrowserSession.py](../../../Utility/BrowserSession.py). [AllureReport.py](../../../Utility/AllureReport.py) attaches the finalized evidence; there is no separate screenshot utility.
- For automatic Allure HTML output, use [run_tests.py](../../../run_tests.py): `python run_tests.py` runs both frameworks, or select `--runner pytest` / `--runner behave`. It generates [Reports/allure-report](../../../Reports/allure-report) after the runner processes exit and preserves test failures in its exit code. [ALLURE.md](../../../ALLURE.md) documents selection arguments and setup.
- Raw data is retained under timestamped directories in [Reports/allure-results](../../../Reports/allure-results), with only the latest invocation included in the generated HTML. Global output locations are defined by `PROJECT_PATHS` in [ProjectPaths.py](../../../Config/ProjectPaths.py); the runner, report generator, and both frameworks' browser evidence directories use this shared configuration. Screenshots and finalized traces are attached through [AllureReport.py](../../../Utility/AllureReport.py). Direct pytest or Behave commands bypass the combined runner's HTML generation; a formatter output directory alone is raw result data.
- The workflow verifies product controls and zero errors on the earlier forms through [ProductDataPage.py](../../../Pages/ProductDataPage.py), enters product data, and advances to price options. The final Then step asserts the price options title. A dry-run does not execute those assertions or the browser lifecycle.

After a fix, rerun the smallest affected check and report the command, result, and any remaining blocker. Keep environment values and personal test data out of diagnostic summaries.

## Learnings

If setting `ACTION_DELAY=0` exposes extra vehicle-type fields or an unresponsive Next button, inspect app initialization: it finishes in a window-load handler. The landing and vehicle page objects wait for page load, then assert readiness, including the generated `#entervehicledata` tab. The runner launches framework processes with Python's UTF-8 mode so Windows can print Unicode icons in assertion snapshots. The current gender and hobby helpers support an optional visible `click_target` for styled inputs and assert the underlying checked state. Preserve these observable conditions instead of restoring sleeps or forcing clicks.
