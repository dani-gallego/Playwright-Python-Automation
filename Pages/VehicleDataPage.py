from playwright.sync_api import Page, Locator

from Utility.Utilities import Utilities


class VehicleDataPage:
    """
    Page Object for the Vehicle Data page.
    """

    def __init__(
        self,
        page: Page,
        automobile_link: Locator
    ):

        self.page = page

        # =====================================================
        # Locator received from Landing Page
        # =====================================================

        self.automobile_link: Locator = automobile_link
        # The app assigns this ID after configuring the selected vehicle form.
        self.vehicle_tab: Locator = page.locator("#entervehicledata")

        # =====================================================
        # Vehicle Data Locators
        # =====================================================

        self.make: Locator = page.locator(
            "#make"
        )

        self.engine: Locator = page.locator(
            "#engineperformance"
        )

        self.date_of_manufacture: Locator = page.locator(
            "#dateofmanufacture"
        )

        self.seats: Locator = page.locator(
            "#numberofseats"
        )

        self.fuel_type: Locator = page.locator(
            "#fuel"
        )

        self.price: Locator = page.locator(
            "#listprice"
        )

        self.license: Locator = page.locator(
            "#licenseplatenumber"
        )

        self.mileage: Locator = page.locator(
            "#annualmileage"
        )

        self.next: Locator = page.locator(
            "#nextenterinsurantdata"
        )

    # =========================================================
    # Enter Vehicle Data
    # =========================================================

    def enter_vehicle_data(
        self,
        data,
        *,
        navigate_from_landing: bool = True,
    ) -> None:
        """
        Navigate to Vehicle Data and enter the
        supplied vehicle information.
        """

        # -----------------------------------------------------
        # Navigate from Landing Page to Vehicle Data
        # -----------------------------------------------------

        if navigate_from_landing:
            Utilities.click("Automobile Link", self.automobile_link)
        else:
            Utilities.click("Vehicle Data tab", self.vehicle_tab)

        # Vehicle controls are built by the destination's window.load handler.
        self.page.wait_for_load_state("load")
        Utilities.validate_visible("Initialized Vehicle Data tab", self.vehicle_tab)

        # -----------------------------------------------------
        # Enter Vehicle Data
        # -----------------------------------------------------

        Utilities.select_from_list(
            "Make",
            self.make,
            data["make"]
        )

        Utilities.set_text(
            "Engine",
            self.engine,
            data["enginePerformance"]
        )

        Utilities.set_text(
            "Date of Manufacture",
            self.date_of_manufacture,
            data["dateOfManufacture"]
        )

        Utilities.select_from_list(
            "Seats",
            self.seats,
            data["seats"]
        )

        Utilities.select_from_list(
            "Fuel",
            self.fuel_type,
            data["fuelType"]
        )

        Utilities.set_text(
            "Price",
            self.price,
            data["price"]
        )

        Utilities.set_text(
            "Mileage",
            self.mileage,
            data["mileage"]
        )

        Utilities.set_text(
            "License Plate",
            self.license,
            data["license"]
        )

        # -----------------------------------------------------
        # Navigate to Insurant Data
        # -----------------------------------------------------

        Utilities.click(
            "Next",
            self.next
        )
