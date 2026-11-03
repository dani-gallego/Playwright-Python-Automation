import re

from playwright.sync_api import Locator, Page, expect

from Utility.Utilities import Utilities


class SelectPriceOptionPage:
    """Page object for the Automobile Select Price Option step."""

    def __init__(self, page: Page):
        self.page = page

        self.price_plans: Locator = page.locator("#pricePlans")
        self.price_table: Locator = page.locator("#priceTable")
        self.silver: Locator = page.locator("#selectsilver")
        self.gold: Locator = page.locator("#selectgold")
        self.platinum: Locator = page.locator("#selectplatinum")
        self.ultimate: Locator = page.locator("#selectultimate")
        self.selected_option: Locator = self.price_table.locator(
            'input[name="Select Option"]:checked'
        )

        self.view_quote: Locator = page.locator("#viewquote")
        self.download_quote: Locator = page.locator("#downloadquote")
        self.previous_product_data: Locator = page.locator("#preventerproductdata")
        self.next: Locator = page.locator("#nextsendquote")

        self.vehicle_errors: Locator = page.locator("#entervehicledata .counter")
        self.insurant_errors: Locator = page.locator("#enterinsurantdata .counter")
        self.product_errors: Locator = page.locator("#enterproductdata .counter")
        self.price_option_errors: Locator = page.locator("#selectpriceoption .counter")

        self.price_option_map: dict[str, Locator] = {
            "silver": self.silver,
            "gold": self.gold,
            "platinum": self.platinum,
            "ultimate": self.ultimate,
        }
        self.annual_price_map: dict[str, Locator] = {
            name: page.locator(f"#select{name}_price")
            for name in self.price_option_map
        }

    def _normalize_price_option(self, price_option: str) -> str:
        name = price_option.strip().lower()
        if name not in self.price_option_map:
            raise ValueError(
                f"Unsupported price option: {price_option}. "
                "Choose Silver, Gold, Platinum, or Ultimate."
            )
        return name

    def wait_for_price_options(self) -> None:
        """Wait for the real price table, which requires three valid forms."""
        expect(self.page).to_have_title("Select Price Option")
        expect(self.price_plans).to_be_visible()
        expect(self.price_table).to_be_visible()
        for name, locator in self.price_option_map.items():
            expect(
                self.price_table.get_by_role("columnheader", name=name.title(), exact=True)
            ).to_be_visible()
            # The styled radio inputs are offscreen; their labels are clickable.
            expect(locator.locator("..")).to_be_visible()
            expect(locator).to_be_enabled()
            expect(self.annual_price_map[name]).to_have_text(re.compile(r"\d"))

    def verify_ready(self) -> None:
        """Verify calculated prices and validity of all preceding forms."""
        self.wait_for_price_options()
        for errors in (self.vehicle_errors, self.insurant_errors, self.product_errors):
            expect(errors).to_have_text("0")

    def get_price_per_year(self, price_option: str) -> str:
        """Return the displayed annual price, preserving its number formatting."""
        name = self._normalize_price_option(price_option)
        self.wait_for_price_options()
        return Utilities.get_text(f"{name.title()} price per year", self.annual_price_map[name])

    def select_price_option(self, price_option: str) -> None:
        """Select a plan using the priceOption data value and advance to Send Quote."""
        name = self._normalize_price_option(price_option)
        self.verify_ready()
        locator = self.price_option_map[name]
        Utilities.select_radio_button(
            f"{name.title()} price option", locator, click_target=locator.locator("..")
        )
        expect(self.selected_option).to_have_count(1)
        expect(self.selected_option).to_have_value(name.title())
        expect(self.price_option_errors).to_have_text("0")
        # The application reveals these controls only after a plan is selected.
        for control in (
            self.view_quote,
            self.download_quote,
            self.previous_product_data,
            self.next,
        ):
            expect(control).to_be_visible()

        Utilities.click("Next (Send Quote)", self.next)
        expect(self.page).to_have_title("Send Quote")
