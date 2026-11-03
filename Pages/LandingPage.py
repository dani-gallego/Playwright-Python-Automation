from playwright.sync_api import Page, Locator

from Utility.Utilities import Utilities


class LandingPage:
    """
    Page Object for the application Landing Page.
    """

    def __init__(self, page: Page):

        self.page = page

        # =====================================================
        # Locators
        # =====================================================

        self.automobile_link: Locator = page.get_by_role(
            "link",
            name="Automobile",
            exact=True
        )

    # =========================================================
    # Wait / Validate Landing Page
    # =========================================================

    def wait_for_landing_page(self) -> None:
        """
        Validate that the Landing Page is ready.
        """

        # The application installs navigation handlers during window.load.
        self.page.wait_for_load_state("load")

        Utilities.validate_exists(
            "Automobile Link",
            self.automobile_link
        )

        Utilities.validate_visible(
            "Automobile Link",
            self.automobile_link
        )

        Utilities.validate_enabled(
            "Automobile Link",
            self.automobile_link
        )

    # =========================================================
    # Click Automobile
    # =========================================================

    def click_automobile(self) -> None:
        """
        Click the Automobile link.
        """

        Utilities.click(
            "Automobile Link",
            self.automobile_link
        )
