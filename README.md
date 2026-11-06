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

Local configuration is read from optional `Config/environments/.env.<TEST_ENV>`; `TEST_ENV`
defaults to `sit`. Keep local environment files private. Set `BASE_URL` and
`ENVIRONMENT` for the target application. Process variables override file values.
The browser defaults to Chromium; set `HEADLESS=true` for headless execution.
`ACTION_DELAY` defaults to `0`: Playwright waits for actionable controls, with
explicit assertions for application readiness. Set a positive delay only when
you want slower demonstration runs. [WaitUtility.py](./Utility/WaitUtility.py)
provides the shared fixed-delay implementation used by UI actions.

## GitHub Actions secrets

In the repository's **Settings > Secrets and variables > Actions**, add these
repository secrets using **New repository secret**:

| Secret | Value |
| --- | --- |
| `DEMOWEB_USERNAME` | Your dedicated Demo Web Shop account email |
| `DEMOWEB_PASSWORD` | That account's password |

Store each value separately. Do not put credentials in Git ignore rules, workflow
YAML, test data, or command-line arguments. GitHub's
[secret setup instructions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
describe the repository secret store.

After publishing [the workflow](./.github/workflows/demoweb-secrets.yml) to the
default branch, open **Actions > Verify Demo Web Shop secrets > Run workflow**.
The workflow injects the secrets as `USERNAME` and `PASSWORD` only in the step
that needs them. It supplies the public URL as ordinary configuration and does
not create a dotenv file or upload artifacts containing credentials.

This manual workflow verifies configuration availability. It does not log in
or run the vehicle insurance scenarios against Demo Web Shop. Test jobs that
need the same credentials can reuse the step's `env` mapping.

CI can run entirely from environment variables. Missing required settings raise
an error naming the setting, without including its value. Local dotenv files
continue to work, and injected environment variables take precedence.

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
| [Agent](./Agent/) | Optional GPT/agentic automation components and project skills |

Screenshots, traces, raw Allure results, and HTML are generated under `Reports/`;
logs are generated under `Logs/`. They can be deleted between runs and are
ignored by Git. The dependency file pins direct dependencies; pip resolves their
transitive dependencies. It is not a complete environment lockfile.

## Optional agent capabilities

[Agent/README.md](./Agent/README.md) describes the candidate AI capabilities,
approval requirements, and boundaries between generated content, test execution,
and reporting. Project skills live in [Agent/skills](./Agent/skills/).

For this phase, the optional folder and guidance are sufficient. Stabilize the
core framework first, then agree on the required AI capabilities and approve the
design before adding selected dependencies. Do not install AI dependencies merely
because they appear in a framework checklist.
