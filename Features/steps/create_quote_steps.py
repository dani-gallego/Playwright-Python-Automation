
from behave import given, when, then

from Config.ProjectPaths import PROJECT_PATHS
from Utility.TestDataReader import TestDataReader
from E2E_Test.QuoteCreate import QuoteCreate


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


@then("I should be navigated to the product data page")
def step_verify_product_selection(context):

    context.quote_create.verify_product_data()


@then("I should be navigated to the price options page")
def step_verify_price_options(context):

    context.quote_create.verify_price_options()


@then("I should be navigated to the send quote page")
def step_verify_send_quote(context):

    context.quote_create.verify_send_quote()
