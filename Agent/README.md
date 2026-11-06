# Optional GPT/agentic automation components

This folder holds the project's [skills](./skills/) and the design boundaries for
future AI capabilities. For this phase, the folder and guidance are sufficient;
there is no model integration or autonomous browser execution component here.

Stabilize the core framework first, then agree on which AI capabilities are
actually required. Once the design is approved, add only the selected
dependencies. Do not install AI dependencies merely because they appear in the
framework checklist. Core test execution and reporting must work without an AI
SDK, model credentials, or access to a model service.

## Candidate capabilities

These are options for an approved future design, not implemented features.

| Capability | Implementation approach |
| --- | --- |
| Generate Gherkin scenarios from approved requirements | GPT API or an approved agent SDK |
| Generate candidate locators | AI-assisted suggestions, validated by an engineer |
| Recommend test data | Controlled input generation with validation |
| Analyze failed test results | Provide sanitized logs and failure evidence to an approved model |
| Execute browser actions autonomously | Separate, permission-controlled agent component |

## Boundaries for an approved design

- **Generated content:** Treat scenarios, locators, and test data as candidates.
  Validate and review them before incorporating them into deterministic test
  workflows. Generate scenarios from approved requirements and have an engineer
  validate locator suggestions.
- **Test execution:** Keep model calls outside the core pytest/Behave execution
  path. Any autonomous browser component requires separate permission controls
  and an explicit scope of allowed actions. Constrain execution to approved test
  environments and deterministic test workflows.
- **Reporting:** Preserve the original runner results and failure evidence.
  Sanitize logs, screenshots, traces, credentials, and sensitive application data
  before sending evidence to an approved model. Keep model analysis separate
  from the runner's pass/fail result.

For enterprise applications, an AI agent must never autonomously approve
financial transactions, change production data, or bypass access controls.
The presence of a skill or browser command reference does not grant permission
to perform those actions.

## Project skills

All five repository skills, including their references and agent metadata, live
under [skills/](./skills/). Their instructions do not install or activate AI
capabilities.

| Skill | Use |
| --- | --- |
| [automation-troubleshooting](./skills/automation-troubleshooting/SKILL.md) | Diagnose execution and configuration failures |
| [playwright-cli](./skills/playwright-cli/SKILL.md) | Browser exploration and Playwright CLI guidance |
| [pom](./skills/pom/SKILL.md) | Create or extend Python page objects |
| [python-behave-tests](./skills/python-behave-tests/SKILL.md) | Implement pytest/Behave scenarios and reusable workflows |
| [quote-test-data](./skills/quote-test-data/SKILL.md) | Maintain quote JSON records and field mappings |

The repository's [AGENTS.md](../AGENTS.md) points agents to these files. This
custom location is not a standard automatic skill discovery directory; agents
can read the matching file through those instructions or an explicit file path.
Globally installed and plugin-managed skills remain managed by their providers.
