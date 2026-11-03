"""Bounded recovery for ordered, safely repeatable UI steps.

Application locators, navigation, and test data belong to callers. Do not
register irreversible actions such as email submission or payment here.
"""

from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
import json

import allure
from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError


@dataclass(frozen=True)
class StepDiagnostics:
    counter: int | None = None
    fields: tuple[str, ...] = ()
    note: str = ""

    @property
    def has_errors(self) -> bool:
        return (self.counter is not None and self.counter > 0) or bool(self.fields)


@dataclass(frozen=True)
class RecoveryStep:
    name: str
    action: Callable[[], None]
    inspect: Callable[[], StepDiagnostics]
    prerequisite: Callable[[], str | None] = lambda: None


class RecoveryError(AssertionError):
    """The retry budget was exhausted; diagnostics describe remaining errors."""


class RecoveryScenario:
    def __init__(self, max_retries: int = 2):
        if max_retries < 0:
            raise ValueError("max_retries must be nonnegative")
        self.max_retries = max_retries
        self.history: list[dict] = []

    def run(self, steps: Sequence[RecoveryStep], *, start_at: str | None = None) -> None:
        """Retry from the earliest invalid prerequisite through the remaining steps.

        Only UI assertion failures and Playwright timeouts are recoverable.
        Invalid data and programming errors propagate immediately. The retry
        budget applies to the entire run, including failures during recovery.
        Diagnostics must contain field names and counts, never entered values.
        """
        names = [step.name for step in steps]
        if len(set(names)) != len(names):
            raise ValueError("Recovery step names must be unique")
        index = names.index(start_at) if start_at is not None else 0
        self.history = []
        while index < len(steps):
            step = steps[index]
            try:
                with allure.step(f"Run {step.name}"):
                    step.action()
            except (AssertionError, PlaywrightTimeoutError) as exc:
                diagnostics = {}
                for previous in steps[:index + 1]:
                    try:
                        diagnostics[previous.name] = previous.inspect()
                    except PlaywrightError as diagnostic_error:
                        diagnostics[previous.name] = StepDiagnostics(
                            note=f"Diagnostics unavailable: {type(diagnostic_error).__name__}"
                        )
                candidates = [
                    i for i, previous in enumerate(steps[:index + 1])
                    if diagnostics[previous.name].has_errors
                ]
                prerequisite = step.prerequisite()
                if prerequisite is not None:
                    dependency = names.index(prerequisite)
                    if dependency > index:
                        raise ValueError("A recovery prerequisite must precede its step") from exc
                    candidates.append(dependency)
                restart = min(candidates, default=index)
                event = {
                    "failure": len(self.history) + 1,
                    "failed_step": step.name,
                    "retry_from": names[restart],
                    "diagnostics": {name: asdict(state) for name, state in diagnostics.items()},
                }
                self.history.append(event)
                summary = json.dumps(event, indent=2)
                print(f"Recovery diagnostics: {summary}")
                allure.attach(summary, name="Recovery diagnostics", attachment_type=allure.attachment_type.JSON)
                if len(self.history) > self.max_retries:
                    raise RecoveryError(
                        f"Recovery exhausted after {self.max_retries} retries. {summary}"
                    ) from exc
                index = restart
            else:
                index += 1
