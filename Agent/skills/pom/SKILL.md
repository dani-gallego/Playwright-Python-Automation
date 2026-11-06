---
name: pom
description: Create or extend Python Playwright Page Object Model (POM) classes for new application pages in this project. Use when a user requests a new page object, page class, or page-specific locators and actions; keep scenario authoring and execution troubleshooting in their existing skills.
---

# POM

Create the requested page object using this project's synchronous Python Playwright conventions. The display name is **POM**; the invocation identifier is `$pom`.

## Create a validation run folder

At the beginning of every invocation, create a new run directory under [Reports/POM Validation](../../../Reports/POM%20Validation). Resolve it through [PROJECT_PATHS](../../../Config/ProjectPaths.py), so it is independent of the shell's working directory. Keep earlier runs intact.

```python
from datetime import datetime
from Config.ProjectPaths import PROJECT_PATHS

run_dir = PROJECT_PATHS.reports / "POM Validation" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
run_dir.mkdir(parents=True, exist_ok=False)
```

Use this directory for the invocation's validation artifacts:

- `validation.py`: the actual validation script used for the created or updated page object, when browser validation is possible.
- `validation.log`: the validation command's stdout and stderr, including failures.
- `validation.md`: the page object, inspected URL, checks performed, outcome, and any blockers. Start with a pending status and update it when work finishes. For an invocation without browser execution, record why it was skipped and which checks ran.
- `passed.png` or `failed.png`: the final browser screenshot when a page is available.
- `trace.zip`: the Playwright trace from browser validation, including screenshots, DOM snapshots, and sources.

Do not put POM validation scripts, screenshots, logs, or traces in ad hoc report folders or elsewhere in the project. Generated page objects still belong in [Pages](../../../Pages).

## Establish the page contract

- Identify the page name, controls, required actions, and expected ready state from the request, existing source, supplied HTML, or an accessible application page. Ask only for essential information that cannot be found.
- Inspect [Pages](../../../Pages), the nearest existing page object, and [Utilities.py](../../../Utility/Utilities.py) before writing code. [LandingPage.py](../../../Pages/LandingPage.py) demonstrates shared actions; [ProductDataPage.py](../../../Pages/ProductDataPage.py) demonstrates readiness assertions.
- Extend an existing object when it already represents the page. For a new page, create one module and class named with a PascalCase page name ending in `Page`, such as `LoginPage`. Avoid appending `Page` twice.
- Obtain selectors from observed markup or supplied evidence. Prefer stable accessible roles, labels, test IDs, or IDs. If evidence is missing, request the page URL or markup before claiming to have working locators. If the user explicitly requests a skeleton, clearly identify its unfinished parts.

## Implement the page object

- Place the class in [Pages](../../../Pages). Use `playwright.sync_api`, an injected `page: Page`, `self.page`, and descriptive snake_case locator attributes defined in `__init__`. Match the neighboring modules' imports and type annotations. Do not start a browser in a page object or introduce a base class solely for the new page.
- Keep selectors, page-specific actions, and readiness checks inside the page class. Use snake_case methods such as `verify_ready`, `enter_login_data`, and `click_next`, with appropriate type annotations.
- Reuse `Utilities.click(object_name, locator)`, `Utilities.set_text(object_name, locator, value)`, and other existing helpers when they fit. Read their signatures first. `select_from_list` takes a displayed option label. For styled radio buttons and checkboxes, inspect the existing `click_target` handling before adding custom clicks.
- Accept input values as method parameters or the existing data dictionary. Keep scenario values out of the page class; preserve established JSON field names and normalization behavior.
- Use retrying `expect` assertions or existing validation helpers for readiness and results. Pick a marker unique to the target page, optionally with a supported title or URL assertion. Do not add fixed sleeps. In this application, a successful Next click alone does not establish valid form data.
- Keep cross-page sequencing in the existing workflow. Read [QuoteCreate.py](../../../E2E_Test/QuoteCreate.py) and its callers before integrating a page into a requested flow. Add workflow calls, Behave steps, scenarios, or test data only when the user's request needs them. Preserve the single Automobile navigation click currently owned by `VehicleDataPage.enter_vehicle_data`.

## Validate and report

- Check syntax of changed Python modules and verify helper signatures and imports against the current source. Run the affected existing test when behavior or workflow integration changes and the required runtime is available. A syntax check does not validate browser selectors.
- Save the actual browser validation code as `validation.py` in the current run directory and execute it with the project's interpreter. Because this script is nested under the reports folder, initialize project imports from `Path(__file__).resolve().parents[3]` before importing project modules; derive its artifact directory from `Path(__file__).resolve().parent`.
- Reuse [BrowserSession](../../../Utility/BrowserSession.py) with the current run directory as `artifacts_dir`. It starts tracing with screenshots, snapshots, and sources, and finalizes `trace.zip` when its context manager exits. Capture `passed.png` after successful checks or `failed.png` before re-raising a validation failure. Retain the failure status and write stdout/stderr to `validation.log`. Avoid masking the original failure if screenshot capture also fails.
- Inspecting the shared browser is useful for discovering selectors; also exercise the Python page object in the recorded validation script when the browser runtime is available. If browser startup is blocked, retain the run summary and logs and state that no trace was produced rather than claiming browser validation passed.
- Finish `validation.md` after the browser context manager exits so the trace has been finalized. Report the created or updated page class, its actions, checks performed, and any unverified selectors or runtime blockers. Link the run directory and available validation summary and trace in the final response. Include a short import and usage example when helpful.

## Invocation

In Codex chat, for example:

```text
$pom Create a page object for the Login page at <URL>, with username and password fields, a Sign in action, and a readiness check. Inspect the actual page for selectors.
```

The skill may also be selected automatically for a matching page-object request. It runs during an agent task; it does not watch the application for newly deployed pages. Fully unattended detection would require a separately requested trigger or automation.
