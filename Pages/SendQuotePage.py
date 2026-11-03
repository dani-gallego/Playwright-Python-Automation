from playwright.sync_api import Locator, Page, expect

from Utility.Utilities import Utilities


class SendQuotePage:
    """Page object for the Automobile Send Quote form."""

    def __init__(self, page: Page):
        self.page = page

        self.quote_form: Locator = page.locator("#sendQuoteForm")
        self.email: Locator = page.locator("#email")
        self.phone: Locator = page.locator("#phone")
        self.username: Locator = page.locator("#username")
        self.password: Locator = page.locator("#password")
        self.confirm_password: Locator = page.locator("#confirmpassword")
        # The live application's Comments ID starts with an uppercase C.
        self.comments: Locator = page.locator("#Comments")
        self.previous_price_option: Locator = page.locator("#prevselectpriceoption")
        self.send: Locator = page.locator("#sendemail")

        self.vehicle_errors: Locator = page.locator("#entervehicledata .counter")
        self.insurant_errors: Locator = page.locator("#enterinsurantdata .counter")
        self.product_errors: Locator = page.locator("#enterproductdata .counter")
        self.price_option_errors: Locator = page.locator("#selectpriceoption .counter")
        self.quote_errors: Locator = page.locator("#sendquote .counter")

    def wait_for_send_quote(self) -> None:
        """Wait for the form revealed by selecting a price option."""
        expect(self.page).to_have_title("Send Quote")
        expect(self.quote_form).to_be_visible()
        for locator in (
            self.email,
            self.phone,
            self.username,
            self.password,
            self.confirm_password,
            self.comments,
            self.previous_price_option,
            self.send,
        ):
            expect(locator).to_be_visible()
            expect(locator).to_be_enabled()

    def verify_ready(self) -> None:
        """Verify form readiness and validity of the preceding quote steps."""
        self.wait_for_send_quote()
        for errors in (
            self.vehicle_errors,
            self.insurant_errors,
            self.product_errors,
            self.price_option_errors,
        ):
            expect(errors).to_have_text("0")

    def enter_quote_data(self, quotedata: dict) -> None:
        """Fill and validate data from the record's quote object without sending.

        Required keys: email, username, password. Phone and comments are optional.
        confirmPassword defaults to password when no separate value is supplied.
        Optional fields are cleared when omitted, allowing reuse of the form.
        """
        self.verify_ready()
        Utilities.set_text("E-Mail", self.email, quotedata["email"])
        Utilities.set_text("Phone", self.phone, quotedata.get("phone") or "")
        Utilities.set_text("Username", self.username, quotedata["username"])
        Utilities.set_text("Password", self.password, quotedata["password"])
        Utilities.set_text(
            "Confirm Password",
            self.confirm_password,
            quotedata.get("confirmPassword", quotedata["password"]),
        )
        Utilities.set_text("Comments", self.comments, data.get("comments") or "")
        expect(self.quote_errors).to_have_text("0")

    def send_quote(self) -> None:
        """Submit the validated form; call explicitly when sending is intended."""
        self.verify_ready()
        expect(self.quote_errors).to_have_text("0")
        Utilities.click("Send E-Mail", self.send)
