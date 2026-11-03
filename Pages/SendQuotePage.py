from playwright.sync_api import Locator, Page, expect

from Utility.Utilities import Utilities


class SendQuotePage:
    """Page object for the Automobile Send Quote form."""

    def __init__(self, page: Page):
        self.page = page

        self.quote_form: Locator = page.locator("#sendQuoteForm")
        self.blocked_message: Locator = page.get_by_text(
            "Please, select a price option to send the quote.", exact=True
        )
        self.email: Locator = page.locator("#email")
        self.phone: Locator = page.locator("#phone")
        self.username: Locator = page.locator("#username")
        self.password: Locator = page.locator("#password")
        self.confirm_password: Locator = page.locator("#confirmpassword")
        # The live application's Comments ID starts with an uppercase C.
        self.comments: Locator = page.locator("#Comments")
        self.previous_price_option: Locator = page.locator("#prevselectpriceoption")
        self.send: Locator = page.locator("#sendemail")
        self.submission_message: Locator = page.locator(".sweet-alert h2")

        self.vehicle_errors: Locator = page.locator("#entervehicledata .counter")
        self.insurant_errors: Locator = page.locator("#enterinsurantdata .counter")
        self.product_errors: Locator = page.locator("#enterproductdata .counter")
        self.price_option_errors: Locator = page.locator("#selectpriceoption .counter")
        self.quote_errors: Locator = page.locator("#sendquote .counter")

    def wait_for_send_quote(self) -> None:
        """Wait for the form revealed by selecting a price option."""
        expect(self.page).to_have_title("Send Quote")
        if self.is_blocked():
            raise AssertionError("Send Quote is blocked: select a valid price option after completing prior forms")
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

    def is_blocked(self) -> bool:
        return not self.quote_form.is_visible() and self.blocked_message.is_visible()

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
        Utilities.set_text("Comments", self.comments, quotedata.get("comments") or "")
        expect(self.quote_errors).to_have_text("0")

    def verify_quote_sent(self, timeout: float = 30000) -> None:
        """Wait for the success dialog after the application's delayed request."""
        expect(self.submission_message).to_be_visible(timeout=timeout)
        expect(self.submission_message).to_have_text(
            "Sending e-mail success!", timeout=timeout
        )

    def send_quote(self) -> None:
        """Submit the validated form and wait for the application's success dialog."""
        self.verify_ready()
        expect(self.quote_errors).to_have_text("0")
        Utilities.click("Send E-Mail", self.send)
        self.verify_quote_sent()
