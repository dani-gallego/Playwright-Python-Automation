---
name: quote-test-data
description: Add, update, or diagnose JSON quote test cases and their field mappings in this vehicle insurance automation project. Use for CreateQuoteData records, testCase lookup, vehicle and insurant payloads, and input normalization; not for environment secrets or general page object work.
---

# Maintain quote test data

Read [CreateQuoteData.json](../../../Data/CreateQuoteData.json), [TestDataReader.py](../../../Utility/TestDataReader.py), and the affected page method before changing records. Preserve unrelated cases and use synthetic data for new examples.

## Preserve the record contract

The JSON root is a list. Each record contains a `testCase` string and nested `vehicle` and `insurant` objects. The current identifiers are `TC001` through `TC010`; check the file for the next unused identifier rather than assuming that list remains current.

`get_test_case_data(file_path, test_case)` performs an exact identifier match and returns the first matching record. Missing identifiers raise `ValueError`; a missing file raises `FileNotFoundError`. Keep identifiers unique so duplicate records cannot silently select the wrong data. Paths passed to the reader resolve from the current working directory.

The [quote workflow](../../../E2E_Test/QuoteCreate.py) consumes `data["vehicle"]` and `data["insurant"]`. The [step definitions](../../../Features/steps/create_quote_steps.py) load the selected record by identifier. Keep feature identifiers and JSON identifiers aligned.

## Match page inputs

| Section | Fields | Current consumption |
| --- | --- | --- |
| `vehicle` | `make`, `enginePerformance`, `dateOfManufacture`, `seats`, `fuelType`, `price`, `license`, `mileage` | All accessed directly by [VehicleDataPage](../../../Pages/VehicleDataPage.py) |
| `insurant` | `firstName`, `lastName`, `dateOfBirth`, `streetAddress`, `country`, `zipCode`, `city`, `occupation` | Accessed directly by [InsurantDataPage](../../../Pages/InsurantDataPage.py) |
| `insurant` | `gender`, `hobbies`, `website` | Read with `.get`; empty or missing values skip their actions |

Current text and dropdown values are strings. Keep numeric-looking values such as engine performance, price, mileage, seats, and ZIP codes as strings: the shared text helper passes values directly to `locator.fill`, and ZIP codes can have leading zeros. Match existing date formatting and the application's accepted format before introducing new dates.

Dropdown data uses displayed labels because [Utilities.select_from_list](../../../Utility/Utilities.py) calls `select_option(label=value)`. Do not substitute HTML option values without also changing the consumer deliberately.

Gender normalization accepts `male`/`m` and `female`/`f`, ignoring case and surrounding whitespace. Hobbies accept a list or a string delimited by semicolons, pipes, or commas. Hobby lookup ignores case and spaces; the current keys are `speeding`, `bungeejumping`, `cliffdiving`, `skydiving`, and `other`. Prefer the existing list representation for new records.

## Add or change a case

1. Find the scenario and the record it uses. Determine whether the request changes test data, accepted input handling, or expected behavior.
2. Add a uniquely identified record or edit the requested record while preserving field names and nesting. Update the consuming page and workflow only if the requested data contract changes.
3. For a boundary or invalid-input case, state the expected result in the scenario and implement a corresponding assertion. Invalid data alone does not create a meaningful negative test; the current positive workflow always attempts to advance through both pages.
4. Validate JSON syntax, identifier uniqueness, and the fields consumed by the affected page. Exercise `get_test_case_data` for a new identifier. Check input normalization separately if changing gender or hobby handling.

For data-only changes, local parsing and reader checks do not require launching a browser. Run the affected UI scenario when requested or when needed to establish application acceptance; distinguish data validation from successful quote creation.

## Learnings

The observed application uses `MM/DD/YYYY` date inputs and offers occupation labels `Employee`, `Public Official`, `Farmer`, `Unemployed`, and `Selfemployed`. Several existing records after `TC001` contain unsupported occupation labels and dates with a first component greater than 12; do not treat them as valid positive scenarios or guess their intended replacements. Pytest reads the record selected by `--test-case` (default `TC001`) without hardcoded field overrides, while the Behave smoke scenario reads its feature-specified identifier directly.
