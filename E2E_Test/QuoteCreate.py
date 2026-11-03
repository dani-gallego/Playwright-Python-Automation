"""Main quote E2E scenarios and workflow shared with Behave."""

import allure
from playwright.sync_api import expect
import pytest

from Pages.LandingPage import LandingPage
from Pages.VehicleDataPage import VehicleDataPage
from Pages.InsurantDataPage import InsurantDataPage
from Pages.ProductDataPage import ProductDataPage
from Pages.SelectPriceOptionPage import SelectPriceOptionPage


class QuoteCreate:

    def __init__(self, page):

        self.page = page

        self.landing_page = LandingPage(page)

        self.vehicle_page = VehicleDataPage(
            page,
            self.landing_page.automobile_link
        )

        self.insurant_page = InsurantDataPage(page)
        self.product_page = ProductDataPage(page)
        self.price_option_page = SelectPriceOptionPage(page)

    def open_application(self, base_url):

        self.page.goto(base_url, wait_until="domcontentloaded")

        self.landing_page.wait_for_landing_page()

    def create_quote(self, data):

        self.vehicle_page.enter_vehicle_data(
            data["vehicle"]
        )

        self.insurant_page.enter_insurant_data(
            data["insurant"]
        )

        self.verify_product_data()
        self.product_page.enter_product_data(
            data["product"]
        )
        # Selecting the plan also advances to Send Quote inside the page object.
        self.price_option_page.select_price_option(data["priceOption"])

    def verify_product_data(self):
        self.product_page.verify_ready()

    def verify_price_options(self):
        self.price_option_page.verify_ready()

    def verify_send_quote(self):
        expect(self.page).to_have_title("Send Quote")


@pytest.mark.smoke
@allure.feature("Vehicle insurance")
@allure.story("Select a price option and reach Send Quote")
def test_quote_reaches_send_quote(page, environment_config, quote_data):
    """Complete the forms, select the plan, and verify arrival and retained choices."""
    data = quote_data
    allure.dynamic.title(f"Reach Send Quote using {data['testCase']}")
    allure.dynamic.parameter("test_case", data["testCase"])

    quote = QuoteCreate(page)
    quote.open_application(environment_config.base_url)
    quote.create_quote(data)
    quote.verify_send_quote()

    selected_plan = data["priceOption"].strip().lower()
    expect(quote.price_option_page.selected_option).to_have_count(1)
    for name, locator in quote.price_option_page.price_option_map.items():
        expect(locator).to_be_checked(checked=name == selected_plan)
    expect(quote.price_option_page.price_option_errors).to_have_text("0")

    # Input state can be asserted even after its form has become hidden.
    expect(quote.vehicle_page.make).to_have_value(data["vehicle"]["make"])
    expect(quote.vehicle_page.engine).to_have_value(data["vehicle"]["enginePerformance"])
    expect(quote.insurant_page.first_name).to_have_value(data["insurant"]["firstName"])
    insurant = data["insurant"]
    expect(quote.insurant_page.website).to_have_value(insurant.get("website") or "")
    gender = insurant.get("gender")
    normalized_gender = InsurantDataPage.normalize_gender(gender) if gender else None
    expect(quote.insurant_page.male).to_be_checked(checked=normalized_gender == "Male")
    expect(quote.insurant_page.female).to_be_checked(checked=normalized_gender == "Female")
    chosen_hobbies = {
        hobby.lower().replace(" ", "")
        for hobby in InsurantDataPage.parse_hobbies(insurant.get("hobbies"))
    }
    for name, locator in quote.insurant_page.hobby_map.items():
        expect(locator).to_be_checked(checked=name in chosen_hobbies)

    product = data["product"]
    expect(quote.product_page.start_date).to_have_value(product["startDate"])
    for locator, key in (
        (quote.product_page.insurance_sum, "insuranceSum"),
        (quote.product_page.merit_rating, "meritRating"),
        (quote.product_page.damage_insurance, "damageInsurance"),
        (quote.product_page.courtesy_car, "courtesyCar"),
    ):
        expect(locator.locator("option:checked")).to_have_text(product[key])
    products = product["optionalProducts"]
    if isinstance(products, str):
        products = [products]
    chosen_products = {name.strip().lower().replace(" ", "") for name in products}
    for name, locator in quote.product_page.optional_product_map.items():
        expect(locator).to_be_checked(checked=name in chosen_products)
