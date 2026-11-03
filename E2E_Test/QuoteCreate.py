"""Main quote E2E scenarios and workflow shared with Behave."""

import allure
from playwright.sync_api import expect
import pytest

from Pages.LandingPage import LandingPage
from Pages.VehicleDataPage import VehicleDataPage
from Pages.InsurantDataPage import InsurantDataPage
from Pages.ProductDataPage import ProductDataPage
from Pages.SelectPriceOptionPage import SelectPriceOptionPage
from Pages.SendQuotePage import SendQuotePage
from Pages.QuoteFormPage import QuoteFormPage
from Utility.RecoveryScenario import RecoveryScenario, RecoveryStep


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
        self.send_quote_page = SendQuotePage(page)
        self.form_pages = {
            name: QuoteFormPage(page, tab_id, position)
            for position, (name, tab_id) in enumerate((
                ("vehicle", "entervehicledata"),
                ("insurant", "enterinsurantdata"),
                ("product", "enterproductdata"),
                ("price_option", "selectpriceoption"),
                ("send_quote", "sendquote"),
            ))
        }
        self.recovery = RecoveryScenario()

    def open_application(self, base_url):

        self.page.goto(base_url, wait_until="domcontentloaded")

        self.landing_page.wait_for_landing_page()

    def create_quote(self, data):
        """Complete recoverable form entry, then submit once as the final action."""
        self.recovery.run(self._recovery_steps(data))
        self.send_quote_page.send_quote()

    def fill_send_quote(self, data):
        """Resume at Send Quote, repairing prerequisites if the form is blocked."""
        self.recovery.run(self._recovery_steps(data), start_at="send_quote")

    def _recovery_steps(self, data):
        def enter_vehicle():
            self.vehicle_page.enter_vehicle_data(
                data["vehicle"],
                navigate_from_landing=self.form_pages["vehicle"].tab.count() == 0,
            )

        def enter_form(name, action):
            self.form_pages[name].open()
            action()

        def enter_product():
            self.verify_product_data()
            self.product_page.enter_product_data(data["product"])

        actions = (
            ("vehicle", enter_vehicle),
            ("insurant", lambda: enter_form("insurant", lambda: self.insurant_page.enter_insurant_data(data["insurant"]))),
            ("product", lambda: enter_form("product", enter_product)),
            ("price_option", lambda: enter_form("price_option", lambda: self.price_option_page.select_price_option(data["priceOption"]))),
            ("send_quote", lambda: enter_form("send_quote", lambda: self.send_quote_page.enter_quote_data(data["quote"], submit=False))),
        )
        return [
            RecoveryStep(
                name, action, self.form_pages[name].inspect,
                prerequisite=(
                    lambda: "price_option" if self.send_quote_page.is_blocked() else None
                ) if name == "send_quote" else lambda: None,
            )
            for name, action in actions
        ]

    def verify_product_data(self):
        self.product_page.verify_ready()

    def verify_price_options(self):
        self.price_option_page.verify_ready()

    def verify_send_quote(self):
        self.send_quote_page.verify_ready()

    def verify_quote_data(self, data):
        self.verify_send_quote()
        quote = data["quote"]
        for locator, expected in (
            (self.send_quote_page.email, quote["email"]),
            (self.send_quote_page.phone, quote.get("phone") or ""),
            (self.send_quote_page.username, quote["username"]),
            (self.send_quote_page.password, quote["password"]),
            (self.send_quote_page.confirm_password, quote.get("confirmPassword", quote["password"])),
            (self.send_quote_page.comments, quote.get("comments") or ""),
        ):
            expect(locator).to_have_value(expected)
        expect(self.send_quote_page.quote_errors).to_have_text("0")


@pytest.mark.smoke
@allure.feature("Vehicle insurance")
@allure.story("Fill Send Quote and recover invalid prerequisites")
def test_quote_reaches_send_quote(page, environment_config, quote_data):
    """Complete the forms, select the plan, and verify arrival and retained choices."""
    data = quote_data
    allure.dynamic.title(f"Reach Send Quote using {data['testCase']}")
    allure.dynamic.parameter("test_case", data["testCase"])

    quote = QuoteCreate(page)
    quote.open_application(environment_config.base_url)
    quote.create_quote(data)
    quote.verify_send_quote()
    quote.verify_quote_data(data)

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


@pytest.mark.recovery
def test_quote_recovers_missing_required_field(page, environment_config, quote_data):
    """Diagnose a cleared prerequisite and restore it using the selected record."""
    quote = QuoteCreate(page)
    quote.open_application(environment_config.base_url)
    quote.create_quote(quote_data)
    form = quote.form_pages["vehicle"]
    form.open()
    missing_field = form.clear_required_field()
    expect(form.counter).not_to_have_text("0")
    quote.form_pages["send_quote"].open()
    expect(quote.send_quote_page.blocked_message).to_be_visible()
    expect(quote.send_quote_page.email).not_to_be_visible()

    quote.fill_send_quote(quote_data)
    quote.verify_quote_data(quote_data)
    assert quote.recovery.history, "The scenario did not exercise recovery"
    diagnosis = quote.recovery.history[0]["diagnostics"]["vehicle"]
    assert diagnosis["counter"] > 0
    assert any(missing_field in field for field in diagnosis["fields"])
    assert quote.recovery.history[0]["retry_from"] == "vehicle"
