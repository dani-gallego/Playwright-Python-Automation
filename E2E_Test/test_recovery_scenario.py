"""Recovery policy checks independent of quote data and browser setup."""

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from Utility.RecoveryScenario import (
    RecoveryError, RecoveryScenario, RecoveryStep, StepDiagnostics,
)


def test_restarts_earliest_invalid_step_and_replays_dependencies():
    calls = []
    invalid = {"profile": False}

    def profile():
        calls.append("profile")
        invalid["profile"] = False

    def summary():
        calls.append("summary")
        if calls.count("summary") == 1:
            invalid["profile"] = True
            raise AssertionError("Prerequisite became invalid")

    recovery = RecoveryScenario()
    recovery.run([
        RecoveryStep("profile", profile, lambda: StepDiagnostics(
            int(invalid["profile"]), ("Required choice",) if invalid["profile"] else (),
        )),
        RecoveryStep("review", lambda: calls.append("review"), StepDiagnostics),
        RecoveryStep("summary", summary, StepDiagnostics),
    ])
    assert calls == ["profile", "review", "summary", "profile", "review", "summary"]
    assert recovery.history[0]["retry_from"] == "profile"
    assert recovery.history[0]["diagnostics"]["profile"]["fields"] == ("Required choice",)


def test_blocked_step_replays_prerequisite_even_with_zero_counters():
    calls = []

    def finish():
        calls.append("finish")
        if "choose" not in calls:
            raise AssertionError("Form blocked")

    recovery = RecoveryScenario()
    recovery.run([
        RecoveryStep("choose", lambda: calls.append("choose"), lambda: StepDiagnostics(0)),
        RecoveryStep("finish", finish, lambda: StepDiagnostics(0), lambda: "choose"),
    ], start_at="finish")
    assert calls == ["finish", "choose", "finish"]


def test_permanent_failure_exhausts_budget_and_preserves_cause():
    calls = []
    failure = AssertionError("Still invalid")

    def action():
        calls.append("attempt")
        raise failure

    recovery = RecoveryScenario(max_retries=2)
    with pytest.raises(RecoveryError, match="after 2 retries") as caught:
        recovery.run([RecoveryStep("input", action, lambda: StepDiagnostics(1, ("Required field",)))])
    assert len(calls) == 3
    assert caught.value.__cause__ is failure
    assert "Required field" in str(caught.value)


def test_retry_budget_is_shared_when_recovery_itself_fails():
    calls = []

    def first():
        calls.append("first")
        if len(calls) > 1:
            raise PlaywrightTimeoutError("Unavailable")

    def second():
        calls.append("second")
        raise AssertionError("Blocked")

    recovery = RecoveryScenario(max_retries=1)
    with pytest.raises(RecoveryError):
        recovery.run([
            RecoveryStep("first", first, lambda: StepDiagnostics(1)),
            RecoveryStep("second", second, StepDiagnostics),
        ])
    assert calls == ["first", "second", "first"]


@pytest.mark.parametrize("failure", [ValueError("Invalid record"), KeyError("missing"), TypeError("Bug")])
def test_data_and_programming_errors_are_not_retried(failure):
    calls = []

    def action():
        calls.append(True)
        raise failure

    recovery = RecoveryScenario()
    with pytest.raises(type(failure)):
        recovery.run([RecoveryStep("input", action, StepDiagnostics)])
    assert calls == [True]
    assert not recovery.history


def test_success_does_not_read_diagnostics_or_replay():
    calls = []

    def unnecessary_diagnostics():
        raise AssertionError("Diagnostics should only run on failure")

    recovery = RecoveryScenario()
    recovery.run([RecoveryStep("input", lambda: calls.append(True), unnecessary_diagnostics)])
    assert calls == [True]
    assert not recovery.history


def test_unknown_start_and_duplicate_names_are_rejected():
    step = RecoveryStep("input", lambda: None, StepDiagnostics)
    with pytest.raises(ValueError):
        RecoveryScenario().run([step], start_at="missing")
    with pytest.raises(ValueError, match="unique"):
        RecoveryScenario().run([step, step])
