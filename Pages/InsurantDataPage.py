from playwright.sync_api import Page, Locator

from Utility.Utilities import Utilities


class InsurantDataPage:
    """
    Page Object for the Insurant Data page.
    """

    def __init__(self, page: Page):

        self.page = page

        # =====================================================
        # Locators
        # =====================================================

        self.first_name: Locator = page.locator(
            "#firstname"
        )

        self.last_name: Locator = page.locator(
            "#lastname"
        )

        self.date_of_birth: Locator = page.locator(
            "#birthdate"
        )

        self.male: Locator = page.locator(
            'input[name="Gender"][value="Male"]'
        )

        self.female: Locator = page.locator(
            'input[name="Gender"][value="Female"]'
        )

        self.street_address: Locator = page.locator(
            "#streetaddress"
        )

        self.country: Locator = page.locator(
            "#country"
        )

        self.zip_code: Locator = page.locator(
            "#zipcode"
        )

        self.city: Locator = page.locator(
            "#city"
        )

        self.occupation: Locator = page.locator(
            "#occupation"
        )

        self.website: Locator = page.locator(
            "#website"
        )

        self.next: Locator = page.locator(
            "#nextenterproductdata"
        )

        # =====================================================
        # Hobby Locators
        # =====================================================

        self.hobby_map = {

            "speeding": page.locator(
                "#speeding"
            ),

            "bungeejumping": page.locator(
                "#bungeejumping"
            ),

            "cliffdiving": page.locator(
                "#cliffdiving"
            ),

            "skydiving": page.locator(
                "#skydiving"
            ),

            "other": page.locator(
                "#other"
            )
        }

    # =========================================================
    # Normalize Gender
    # =========================================================

    @staticmethod
    def normalize_gender(
        gender: str
    ) -> str:
        """
        Convert different gender representations
        into Male or Female.
        """

        value = gender.strip().lower()

        if value in ("male", "m"):
            return "Male"

        if value in ("female", "f"):
            return "Female"

        raise ValueError(
            f"Unsupported gender value: {gender}"
        )

    # =========================================================
    # Parse Hobbies
    # =========================================================

    @staticmethod
    def parse_hobbies(data) -> list[str]:
        """
        Convert hobby input into a list.

        Supported formats:

        - Single string
        - List
        - Semicolon separated
        - Pipe separated
        - Comma separated
        """

        if not data:
            return []

        # Already a list
        if isinstance(data, list):

            return [
                str(item).strip()
                for item in data
                if str(item).strip()
            ]

        # Convert to string
        value = str(data)

        # Support ; | ,
        for separator in ["|", ","]:
            value = value.replace(
                separator,
                ";"
            )

        return [
            item.strip()
            for item in value.split(";")
            if item.strip()
        ]

    # =========================================================
    # Select Gender
    # =========================================================

    def select_gender(
        self,
        gender: str
    ) -> None:

        normalized_gender = (
            self.normalize_gender(gender)
        )

        if normalized_gender == "Male":

            gender_option = self.male

        else:

            gender_option = self.female

        Utilities.select_radio_button(
            f"Gender {normalized_gender}",
            gender_option,
            # The application styles the input beneath a clickable label.
            click_target=gender_option.locator("..")
        )

    # =========================================================
    # Select Hobby
    # =========================================================

    def select_hobby(
        self,
        hobby: str
    ) -> None:

        normalized_key = (
            hobby.strip()
            .lower()
            .replace(" ", "")
        )

        hobby_locator = (
            self.hobby_map.get(
                normalized_key
            )
        )

        if hobby_locator is None:

            raise ValueError(
                f"Hobby not found: {hobby}"
            )

        Utilities.check_box(
            f"Hobby {hobby}",
            hobby_locator,
            click_target=hobby_locator.locator("..")
        )

    # =========================================================
    # Enter Insurant Data
    # =========================================================

    def enter_insurant_data(
        self,
        data
    ) -> None:

        # -----------------------------------------------------
        # Basic Information
        # -----------------------------------------------------

        Utilities.set_text(
            "First Name",
            self.first_name,
            data["firstName"]
        )

        Utilities.set_text(
            "Last Name",
            self.last_name,
            data["lastName"]
        )

        Utilities.set_text(
            "Date of Birth",
            self.date_of_birth,
            data["dateOfBirth"]
        )

        # -----------------------------------------------------
        # Gender
        # -----------------------------------------------------

        gender = data.get("gender")

        if gender:

            self.select_gender(
                gender
            )

        # -----------------------------------------------------
        # Address
        # -----------------------------------------------------

        Utilities.set_text(
            "Street Address",
            self.street_address,
            data["streetAddress"]
        )

        Utilities.select_from_list(
            "Country",
            self.country,
            data["country"]
        )

        Utilities.set_text(
            "Zip Code",
            self.zip_code,
            data["zipCode"]
        )

        Utilities.set_text(
            "City",
            self.city,
            data["city"]
        )

        # -----------------------------------------------------
        # Occupation
        # -----------------------------------------------------

        Utilities.select_from_list(
            "Occupation",
            self.occupation,
            data["occupation"]
        )

        # -----------------------------------------------------
        # Hobbies
        # -----------------------------------------------------

        hobbies = self.parse_hobbies(
            data.get("hobbies")
        )

        for hobby in hobbies:

            self.select_hobby(
                hobby
            )

        # -----------------------------------------------------
        # Website - Optional
        # -----------------------------------------------------

        website = data.get("website")

        if website:

            Utilities.set_text(
                "Website",
                self.website,
                website
            )

        # -----------------------------------------------------
        # Next
        # -----------------------------------------------------

        Utilities.click(
            "Next",
            self.next
        )
