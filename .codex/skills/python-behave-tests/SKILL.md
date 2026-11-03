---
name: python-behave-tests
description: Add or modify Python Playwright page objects, reusable quote workflows, pytest tests, Behave steps, and Gherkin scenarios in this vehicle insurance automation project. Use for test implementation and assertions, rather than standalone browser exploration or execution troubleshooting.
---

# Develop Python Playwright tests

Work from the project root. Inspect the relevant source before editing; the map below describes the current implementation, not a requirement to retain unfinished behavior.

## Follow the existing execution path

| Layer | Existing source | Responsibility |
| --- | --- | --- |
| Scenario | [create_quote.feature](../../../Features/create_quote.feature) | Business behavior, tags, and test case selection |
| Pytest | [QuoteCreate.py](../../../E2E_Test/QuoteCreate.py), [conftest.py](../../../E2E_Test/conftest.py), [pytest.ini](../../../pytest.ini) | Main E2E script with a JSON-driven browser test, fixtures, and discovery |
| Steps | [create_quote_steps.py](../../../Features/steps/create_quote_steps.py) | Translate Gherkin into calls using Behave context |
| Workflow | [QuoteCreate.py](../../../E2E_Test/QuoteCreate.py) | Compose the landing, vehicle, and insurant page objects |
| Pages | [LandingPage.py](../../../Pages/LandingPage.py), [VehicleDataPage.py](../../../Pages/VehicleDataPage.py), [InsurantDataPage.py](../../../Pages/InsurantDataPage.py) | Locators and page-specific interactions |
| UI helpers | [Utilities.py](../../../Utility/Utilities.py) | Shared technical actions, Playwright assertions, and Allure steps |
| Lifecycle | [BrowserSession.py](../../../Utility/BrowserSession.py), [environment.py](../../../Features/environment.py) | Shared browser cleanup and tracing; Behave hooks |
| Data | [TestDataReader.py](../../../Utility/TestDataReader.py), [CreateQuoteData.json](../../../Data/CreateQuoteData.json) | Look up records by `testCase` |

Keep cross-page orchestration in the existing `QuoteCreate` workflow unless the requested change justifies a different design. The unused empty Business package was removed; there is no separate business service or base page class.

[QuoteCreate.py](../../../E2E_Test/QuoteCreate.py) contains both the reusable `QuoteCreate` class imported by Behave and the module-level pytest E2E scenarios. Keep quote scenarios in that main script; its filename is explicitly included in [pytest.ini](../../../pytest.ini) alongside the standard test filename pattern.

## Implement a change

1. Read the relevant scenario, step definitions, workflow, page object, and shared helper. Reuse existing step wording when its meaning matches the new case.
2. Keep scenarios about observable behavior. Both frameworks load records from `PROJECT_PATHS.data / "CreateQuoteData.json"` using `TestDataReader.get_test_case_data`. The pytest `quote_data` fixture selects `--test-case` (default `TC001`); Behave selects the ID in the When step. Keep field values in JSON and use the selected record unchanged instead of overriding it with hardcoded scenario values.
3. Keep selectors and field operations in page objects. Use the synchronous `Page`, `Locator`, and `expect` APIs already used here. Define locators in the constructor; match stable IDs or accessible names that are supported by the actual page.
4. Reuse `Utilities` actions with their existing argument order: an object name, a locator, and a value when needed. `select_from_list` selects by option **label**, so data must contain the displayed label. Add a helper only when the technical behavior is reusable; keep business rules out of that utility class.
5. Compose page actions in the workflow and call the workflow from steps. Add a real assertion for the requested result using a destination page marker, URL, or other observable state supported by the application.

The current `VehicleDataPage` receives `LandingPage.automobile_link` and clicks it inside `enter_vehicle_data`. Avoid adding a second click to the workflow. `QuoteCreate.create_quote` enters vehicle and insurant data, verifies product readiness through `QuoteCreate.verify_product_data`, and fills product data to reach price options.

For insurant inputs, reuse the existing `normalize_gender`, `parse_hobbies`, and `select_hobby` behavior instead of duplicating normalization in steps. Read those methods before extending accepted values.

## Preserve verified behavior

- Pytest fixtures and Behave hooks use `BrowserSession` for a fresh browser context, configured timeouts, cleanup, and traces. Reuse this lifecycle instead of adding competing browser startup code.
- The final destination is **Select Price Option**. Before filling product data, the workflow asserts visible product controls and zero errors on both earlier forms. Product entry checks its own error count before advancing. Navigation alone does not establish valid input in this application.
- `Utilities` actions honor `ACTION_DELAY`; set it to `0` for execution without fixed delays. Retain explicit readiness assertions instead of adding sleeps.

## Verify the change

Run commands from the project root so imports and data paths resolve. First inspect [requirements.txt](../../../requirements.txt) and the selected interpreter's installed packages.

```powershell
$env:HEADLESS = 'true'
$env:ACTION_DELAY = '0'
python -m pytest -m smoke
python -m behave Features/create_quote.feature --dry-run
```

Dry-run checks scenario and step matching; it does not execute hooks, validate browser behavior, or prove assertions pass. If the runtime and hooks are ready, execute the affected scenario or tag, such as `python -m behave Features/create_quote.feature --tags=@smoke`. Report missing dependencies or lifecycle blockers separately from failures introduced by the change.

## Learnings

The app configures vehicle-specific fields and assigns `#entervehicledata` during its window-load handler; wait for that tab before filling the vehicle form. Styled gender and hobby inputs can have their pointer events intercepted: pass their visible parent labels as `click_target` to the shared helpers, then assert the actual input state. The current E2E test covers the selected JSON record, defaulting to `TC001`, through arrival at price options; choosing a price and sending the quote remain outside its coverage.
