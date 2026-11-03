
from behave import given, when, then

from Config.ProjectPaths import PROJECT_PATHS
from Utility.TestDataReader import TestDataReader
from E2E_Test.QuoteCreate import QuoteCreate
from playwright.sync_api import expect


@given("I am on the application landing page")
def step_open_application(context):

    context.quote_create = QuoteCreate(context.page)

    context.quote_create.open_application(
        context.environment_config.base_url
    )


@when('I create a quote using test data "{test_case}"')
def step_create_quote(context, test_case):

    test_data = TestDataReader.get_test_case_data(
        str(PROJECT_PATHS.data / "CreateQuoteData.json"),
        test_case
    )

    context.quote_create.create_quote(test_data)
    context.quote_data = test_data


@when('I fill a quote using test data "{test_case}" without submitting')
def step_prepare_quote(context, test_case):
    context.quote_data = TestDataReader.get_test_case_data(
        str(PROJECT_PATHS.data / "CreateQuoteData.json"), test_case
    )
    context.quote_create.prepare_quote(context.quote_data)


@then("the quote should be sent successfully")
def step_verify_quote_sent(context):
    context.quote_create.verify_quote_sent()


@then("I should be navigated to the product data page")
def step_verify_product_selection(context):

    context.quote_create.verify_product_data()


@then("I should be navigated to the price options page")
def step_verify_price_options(context):

    context.quote_create.verify_price_options()


@then("I should be navigated to the send quote page")
def step_verify_send_quote(context):

    context.quote_create.verify_send_quote()


@then("the Send Quote fields should match the selected test data")
def step_verify_quote_data(context):
    context.quote_create.verify_quote_data(context.quote_data)


@when("a required field in a completed form is cleared")
def step_clear_required_field(context):
    form = context.quote_create.form_pages["vehicle"]
    form.open()
    context.missing_field = form.clear_required_field()
    expect(form.counter).not_to_have_text("0")
    context.quote_create.form_pages["send_quote"].open()


@then("Send Quote should request a price option")
def step_verify_blocked_quote(context):
    page = context.quote_create.send_quote_page
    expect(page.blocked_message).to_be_visible()
    expect(page.email).not_to_be_visible()


@when("I retry filling Send Quote using the selected test data")
def step_retry_send_quote(context):
    context.quote_create.fill_send_quote(context.quote_data)


@then("recovery should report the missing required field")
def step_verify_recovery_diagnostics(context):
    history = context.quote_create.recovery.history
    assert history, "No recovery was performed"
    state = history[0]["diagnostics"]["vehicle"]
    assert state["counter"] > 0
    assert any(context.missing_field in field for field in state["fields"])
    assert history[0]["retry_from"] == "vehicle"
