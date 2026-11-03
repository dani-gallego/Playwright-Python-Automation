from playwright.sync_api import Locator, Page, expect

from Utility.Utilities import Utilities


class ProductDataPage:
    """Page object for the Automobile Enter Product Data form."""

    def __init__(self, page: Page):
        self.page = page
        self.start_date: Locator = page.locator("#startdate")
        self.start_date_calendar: Locator = page.locator("#openstartdatecalender")
        self.insurance_sum: Locator = page.locator("#insurancesum")
        self.merit_rating: Locator = page.locator("#meritrating")
        self.damage_insurance: Locator = page.locator("#damageinsurance")
        self.euro_protection: Locator = page.locator("#EuroProtection")
        self.legal_defense_insurance: Locator = page.locator("#LegalDefenseInsurance")
        self.courtesy_car: Locator = page.locator("#courtesycar")
        # The live application uses "insurance" in this button's ID.
        self.previous_insurant_data: Locator = page.locator("#preventerinsurancedata")
        self.next: Locator = page.locator("#nextselectpriceoption")
        self.product_errors: Locator = page.locator("#enterproductdata .counter")
        self.vehicle_errors: Locator = page.locator("#entervehicledata .counter")
        self.insurant_errors: Locator = page.locator("#enterinsurantdata .counter")

        self.optional_product_map: dict[str, Locator] = {
            "europrotection": self.euro_protection,
            "legaldefenseinsurance": self.legal_defense_insurance,
        }

    def wait_for_product_data(self) -> None:
        """Verify that all product controls are available for interaction."""
        expect(self.page).to_have_title("Enter Product Data")
        for locator in (
            self.start_date,
            self.start_date_calendar,
            self.insurance_sum,
            self.merit_rating,
            self.damage_insurance,
            self.courtesy_car,
            self.previous_insurant_data,
            self.next,
        ):
            expect(locator).to_be_visible()
        # The checkbox inputs are offscreen; users interact with their labels.
        for locator in self.optional_product_map.values():
            expect(locator.locator("..")).to_be_visible()

    def verify_ready(self) -> None:
        """Verify the destination and validity of the two preceding forms."""
        self.wait_for_product_data()
        # This application permits Next even when an earlier form is invalid.
        expect(self.vehicle_errors).to_have_text("0")
        expect(self.insurant_errors).to_have_text("0")

    def select_optional_products(self, products: str | list[str]) -> None:
        """Select exactly the supplied labels, including at least one product."""
        if isinstance(products, str):
            products = [products]
        selected = {product.strip().lower().replace(" ", "") for product in products}
        unsupported = selected - self.optional_product_map.keys()
        if unsupported:
            raise ValueError(f"Unsupported optional products: {sorted(unsupported)}")
        if not selected:
            raise ValueError("Select at least one optional product.")

        for name, locator in self.optional_product_map.items():
            label = locator.locator("..")
            if name in selected:
                Utilities.check_box(name, locator, click_target=label)
            elif locator.is_checked():
                Utilities.click(f"Uncheck {name}", label)
                expect(locator).not_to_be_checked()

    def enter_product_data(self, data: dict) -> None:
        """Fill the form and advance to price options; dropdowns use displayed labels.

        Expected keys: startDate (MM/DD/YYYY), insuranceSum, meritRating,
        damageInsurance, optionalProducts (one label or a list), courtesyCar.
        The application requires at least one of the 'Optional Products'.
        """
        self.wait_for_product_data()
        Utilities.set_text("Start Date", self.start_date, data["startDate"])
        Utilities.select_from_list("Insurance Sum", self.insurance_sum, data["insuranceSum"])
        Utilities.select_from_list("Merit Rating", self.merit_rating, data["meritRating"])
        Utilities.select_from_list(
            "Damage Insurance", self.damage_insurance, data["damageInsurance"]
        )
        self.select_optional_products(data["optionalProducts"])
        Utilities.select_from_list("Courtesy Car", self.courtesy_car, data["courtesyCar"])
        expect(self.product_errors).to_have_text("0")

        # -----------------------------------------------------
        # Navigate to Price Data
        # -----------------------------------------------------

        Utilities.click(
            "Next",
            self.next
        )
