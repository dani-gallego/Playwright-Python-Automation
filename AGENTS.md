# Repository agent guidance

Read [Agent/README.md](./Agent/README.md) for the optional AI capability boundaries.
Do not install AI dependencies solely because they appear in a checklist. Agree
on the required capabilities and approve the design after the core framework is
stable, before adding selected AI dependencies or an autonomous component.

Keep execution constrained to approved test environments and deterministic test
workflows. An AI agent must never autonomously approve financial transactions,
change production data, or bypass access controls. Sanitize failure evidence
before sending it to an approved model.

## Project skills

Repository skills live under [Agent/skills](./Agent/skills/). Before performing a
matching task, read the relevant skill file and follow its instructions within
the user's authorized scope. Resolve supporting references relative to that
skill's directory.

| Task | Skill instructions |
| --- | --- |
| Run or troubleshoot automation and configuration | [automation-troubleshooting](./Agent/skills/automation-troubleshooting/SKILL.md) |
| Explore or interact with a browser using Playwright CLI | [playwright-cli](./Agent/skills/playwright-cli/SKILL.md) |
| Create or extend a Python page object | [pom](./Agent/skills/pom/SKILL.md) |
| Implement pytest/Behave scenarios, steps, and workflows | [python-behave-tests](./Agent/skills/python-behave-tests/SKILL.md) |
| Add or maintain quote JSON data and mappings | [quote-test-data](./Agent/skills/quote-test-data/SKILL.md) |
