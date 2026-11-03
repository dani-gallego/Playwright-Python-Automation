"""Keep quote submission outside retries and after form validation."""

from importlib import import_module
from unittest.mock import Mock, call

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from E2E_Test.QuoteCreate import QuoteCreate
from Pages.SendQuotePage import SendQuotePage
from Utility.RecoveryScenario import RecoveryError, StepDiagnostics


@pytest.fixture
def workflow():
    quote = QuoteCreate(Mock())
    for name in ("vehicle_page", "insurant_page", "product_page", "price_option_page"):
        setattr(quote, name, Mock())
    quote.send_quote_page = Mock(spec=SendQuotePage)
    quote.send_quote_page.is_blocked.return_value = False
    for form in quote.form_pages.values():
        form.open = Mock()
        form.inspect = Mock(return_value=StepDiagnostics(0))
    return quote


@pytest.fixture
def data():
    return {"vehicle": {}, "insurant": {}, "product": {}, "priceOption": "silver", "quote": {}}


def test_preparing_quote_does_not_submit(workflow, data):
    workflow.prepare_quote(data)

    workflow.send_quote_page.enter_quote_data.assert_called_once_with(data["quote"], submit=False)
    workflow.send_quote_page.send_quote.assert_not_called()


def test_form_recovery_submits_once_after_success(workflow, data):
    workflow.send_quote_page.enter_quote_data.side_effect = [AssertionError("Not ready"), None]

    workflow.create_quote(data)

    assert workflow.send_quote_page.enter_quote_data.call_args_list == [
        call(data["quote"], submit=False), call(data["quote"], submit=False)
    ]
    workflow.send_quote_page.send_quote.assert_called_once_with()
    assert len(workflow.recovery.history) == 1


def test_failed_form_recovery_never_submits(workflow, data):
    workflow.send_quote_page.enter_quote_data.side_effect = AssertionError("Invalid form")

    with pytest.raises(RecoveryError):
        workflow.create_quote(data)

    workflow.send_quote_page.send_quote.assert_not_called()


def test_submission_timeout_is_not_retried(workflow, data):
    workflow.send_quote_page.send_quote.side_effect = PlaywrightTimeoutError("No confirmation")

    with pytest.raises(PlaywrightTimeoutError, match="No confirmation"):
        workflow.create_quote(data)

    workflow.send_quote_page.send_quote.assert_called_once_with()
    workflow.send_quote_page.enter_quote_data.assert_called_once_with(data["quote"], submit=False)
    assert not workflow.recovery.history


@pytest.mark.parametrize("valid, submit", [(True, True), (True, False), (False, True)])
def test_direct_entry_submits_only_when_valid_and_requested(monkeypatch, valid, submit):
    module = import_module("Pages.SendQuotePage")
    form = SendQuotePage(Mock())
    form.verify_ready = Mock()
    form.send_quote = Mock()
    assertion = Mock()
    if not valid:
        assertion.to_have_text.side_effect = AssertionError("Invalid quote data")
    monkeypatch.setattr(module, "expect", Mock(return_value=assertion))
    monkeypatch.setattr(module.Utilities, "set_text", Mock())
    quote = {"email": "test@example.com", "username": "TestUser", "password": "Password123!"}

    if valid:
        form.enter_quote_data(quote, **({} if submit else {"submit": False}))
    else:
        with pytest.raises(AssertionError, match="Invalid quote data"):
            form.enter_quote_data(quote)

    if valid and submit:
        form.send_quote.assert_called_once_with()
    else:
        form.send_quote.assert_not_called()
