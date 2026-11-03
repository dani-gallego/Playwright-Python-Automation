from playwright.sync_api import Locator, expect
import allure

from Config.EnvironmentConfig import EnvironmentConfig
from Utility.WaitUtility import WaitUtility


class Utilities:
    """
    Generic reusable UI utilities for Playwright automation.

    This class should contain only technical/UI operations.
    Cross-page business operations belong in the shared quote workflow.
    """

    # ---------------------------------------------------------
    # Click
    # ---------------------------------------------------------

    @staticmethod
    def click(object_name: str, locator: Locator) -> None:
        """
        Click an object after validating that it is visible.
        """

        with allure.step(f"Click {object_name}"):

            expect(
                locator,
                f"{object_name} should be visible"
            ).to_be_visible()

            locator.click()

            print(f"Clicked: {object_name}")

            Utilities.wait_after_action()

    # ---------------------------------------------------------
    # Click Previous
    # ---------------------------------------------------------

    @staticmethod
    def click_previous(object_name: str, locator: Locator) -> None:
        """Click a page's Previous button using the shared click behavior."""
        Utilities.click(object_name, locator)

    # ---------------------------------------------------------
    # Enter Text
    # ---------------------------------------------------------

    @staticmethod
    def set_text(
        object_name: str,
        locator: Locator,
        value: str
    ) -> None:
        """
        Enter text into an input field.
        """

        with allure.step(f"Enter text in {object_name}"):

            expect(
                locator,
                f"{object_name} should be visible"
            ).to_be_visible()

            locator.fill(value)

            print(f"Entered value in: {object_name}")

            Utilities.wait_after_action()

    # ---------------------------------------------------------
    # Get Text
    # ---------------------------------------------------------

    @staticmethod
    def get_text(
        object_name: str,
        locator: Locator
    ) -> str:
        """
        Retrieve text from an object.
        """

        captured_text = ""

        with allure.step(f"Get text from {object_name}"):

            expect(
                locator,
                f"{object_name} should be visible"
            ).to_be_visible()

            captured_text = locator.text_content() or ""

            captured_text = captured_text.strip()

            print(
                f'Captured "{captured_text}" from: '
                f'{object_name}'
            )

            Utilities.wait_after_action()

        return captured_text

    # ---------------------------------------------------------
    # Validate Text Contains
    # ---------------------------------------------------------

    @staticmethod
    def validate_text(
        object_name: str,
        locator: Locator,
        expected_value: str
    ) -> None:
        """
        Validate that an object contains expected text.
        """

        with allure.step(
            f"Validate {object_name} contains text: "
            f"{expected_value}"
        ):

            expect(
                locator,
                f"{object_name} should contain text: "
                f"{expected_value}"
            ).to_contain_text(expected_value)

            print(
                f"Validation passed: {object_name}"
            )

    # ---------------------------------------------------------
    # Validate Exact Text
    # ---------------------------------------------------------

    @staticmethod
    def validate_exact_text(
        object_name: str,
        locator: Locator,
        expected_value: str
    ) -> None:
        """
        Validate exact text of an object.
        """

        with allure.step(
            f"Validate {object_name} has exact text: "
            f"{expected_value}"
        ):

            expect(
                locator,
                f"{object_name} should have exact text: "
                f"{expected_value}"
            ).to_have_text(expected_value)

            print(
                f'Validated exact text "{expected_value}" '
                f'for: {object_name}'
            )

    # ---------------------------------------------------------
    # Select From Dropdown
    # ---------------------------------------------------------

    @staticmethod
    def select_from_list(
        object_name: str,
        locator: Locator,
        value: str
    ) -> None:
        """
        Select an option from a standard HTML select element.
        """

        with allure.step(
            f'Select "{value}" from {object_name}'
        ):

            print(
                f'Selecting "{value}" from: '
                f'{object_name}'
            )

            expect(
                locator,
                f"{object_name} should be visible"
            ).to_be_visible()

            locator.select_option(label=value)

            print(
                f'Selected "{value}" from: '
                f'{object_name}'
            )

            Utilities.wait_after_action()

    # ---------------------------------------------------------
    # Select Radio Button
    # ---------------------------------------------------------

    @staticmethod
    def select_radio_button(
        object_name: str,
        locator: Locator,
        click_target: Locator | None = None
    ) -> None:
        """
        Select a radio button.
        """

        with allure.step(
            f"Select radio button: {object_name}"
        ):

            print(
                f"Selecting radio button: "
                f'{object_name}'
            )

            target = click_target if click_target is not None else locator
            expect(target, f"{object_name} should be visible").to_be_visible()
            if click_target is None:
                locator.check()
            elif not locator.is_checked():
                target.click()
            expect(locator, f"{object_name} should be selected").to_be_checked()

            print(
                f"Selected radio button: "
                f'{object_name}'
            )

            Utilities.wait_after_action()

    # ---------------------------------------------------------
    # Check Checkbox
    # ---------------------------------------------------------

    @staticmethod
    def check_box(
        object_name: str,
        locator: Locator,
        click_target: Locator | None = None
    ) -> None:
        """
        Check a checkbox.
        """

        with allure.step(
            f"Check checkbox: {object_name}"
        ):

            print(
                f"Checking checkbox: {object_name}"
            )

            target = click_target if click_target is not None else locator
            expect(target, f"{object_name} should be visible").to_be_visible()
            if click_target is None:
                locator.check()
            elif not locator.is_checked():
                target.click()
            expect(locator, f"{object_name} should be selected").to_be_checked()

            print(
                f"Checked checkbox: {object_name}"
            )

            Utilities.wait_after_action()

    # ---------------------------------------------------------
    # Uncheck Checkbox
    # ---------------------------------------------------------

    @staticmethod
    def uncheck_box(
        object_name: str,
        locator: Locator
    ) -> None:
        """
        Uncheck a checkbox.
        """

        with allure.step(
            f"Uncheck checkbox: {object_name}"
        ):

            print(
                f"Unchecking checkbox: "
                f'{object_name}'
            )

            expect(
                locator,
                f"{object_name} should be visible"
            ).to_be_visible()

            locator.uncheck()

            print(
                f"Unchecked checkbox: "
                f'{object_name}'
            )

            Utilities.wait_after_action()

    # ---------------------------------------------------------
    # Validate Checkbox
    # ---------------------------------------------------------

    @staticmethod
    def validate_checked(
        object_name: str,
        locator: Locator
    ) -> None:
        """
        Validate that a checkbox/radio button is selected.
        """

        with allure.step(
            f"Validate {object_name} is checked"
        ):

            expect(
                locator,
                f"{object_name} should be selected"
            ).to_be_checked()

            print(
                f"Validated checked: {object_name}"
            )

    # ---------------------------------------------------------
    # Validate Visible
    # ---------------------------------------------------------

    @staticmethod
    def validate_visible(
        object_name: str,
        locator: Locator
    ) -> None:
        """
        Validate that an object is visible.
        """

        with allure.step(
            f"Validate {object_name} is visible"
        ):

            expect(
                locator,
                f"{object_name} should be visible"
            ).to_be_visible()

            print(
                f"Validated visible: {object_name}"
            )

    # ---------------------------------------------------------
    # Validate Enabled
    # ---------------------------------------------------------

    @staticmethod
    def validate_enabled(
        object_name: str,
        locator: Locator
    ) -> None:
        """
        Validate that an object is enabled.
        """

        with allure.step(
            f"Validate {object_name} is enabled"
        ):

            expect(
                locator,
                f"{object_name} should be enabled"
            ).to_be_enabled()

            print(
                f"Validated enabled: {object_name}"
            )

    # ---------------------------------------------------------
    # Clear Text
    # ---------------------------------------------------------

    @staticmethod
    def clear_text(
        object_name: str,
        locator: Locator
    ) -> None:
        """
        Clear a text field.
        """

        with allure.step(
            f"Clear {object_name}"
        ):

            expect(
                locator,
                f"{object_name} should be visible"
            ).to_be_visible()

            locator.fill("")

            print(
                f"Cleared: {object_name}"
            )

    # ---------------------------------------------------------
    # Validate Object Exists
    # ---------------------------------------------------------

    @staticmethod
    def validate_exists(
        object_name: str,
        locator: Locator
    ) -> None:
        """
        Validate that exactly one object exists.
        """

        with allure.step(
            f"Validate {object_name} exists"
        ):

            expect(
                locator,
                f"{object_name} should exist"
            ).to_have_count(1)

            print(
                f"Validated object exists: "
                f'{object_name}'
            )

    # ---------------------------------------------------------
    # Wait After Action
    # ---------------------------------------------------------

    @staticmethod
    def wait_after_action(
        seconds: int | None = None
    ) -> None:
        """
        Wait after an action.

        NOTE:
        This should be used sparingly. Playwright already
        provides automatic waiting for most UI operations.
        """

        delay = EnvironmentConfig().action_delay if seconds is None else seconds
        WaitUtility.wait_after_action(delay)
