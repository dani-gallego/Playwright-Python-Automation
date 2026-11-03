"""Navigation and validation diagnostics shared by the quote wizard's forms."""

from playwright.sync_api import Locator, Page

from Utility.RecoveryScenario import StepDiagnostics
from Utility.Utilities import Utilities


class QuoteFormPage:
    def __init__(self, page: Page, tab_id: str, position: int):
        self.page = page
        self.tab: Locator = page.locator(f"#{tab_id}")
        self.counter: Locator = self.tab.locator(".counter")
        self.form: Locator = page.locator("#insurance-form .idealsteps-wrap > .idealsteps-step").nth(position)
        self.fields: Locator = self.form.locator(".field")

    def open(self) -> None:
        Utilities.click("Quote form tab", self.tab)

    def inspect(self) -> StepDiagnostics:
        """Read the same validation state used by the app's navigation counters.

        Ideal Forms can mark an input invalid before applying the 'invalid'
        CSS class, so inspect its validation metadata as well. Never return
        input values, including passwords or contact details.
        """
        text = self.counter.inner_text().strip() if self.counter.count() == 1 else ""
        fields = self.fields.evaluate_all("""fields => fields.filter(field =>
            (window.jQuery && window.jQuery(field).data('idealforms-valid') === false)
            || field.classList.contains('invalid')
            || field.querySelector('[aria-invalid="true"]')
        ).map(field => {
            const input = field.querySelector('input, select, textarea');
            const label = field.querySelector('label.main');
            const error = field.querySelector('.error');
            const name = label?.textContent.trim() || input?.name || input?.id || 'Unknown field';
            const reason = error?.textContent.trim();
            return reason ? `${name}: ${reason}` : name;
        })""")
        return StepDiagnostics(
            counter=int(text) if text.isdecimal() else None,
            fields=tuple(dict.fromkeys(fields)),
            note="" if text.isdecimal() else "Counter unavailable",
        )

    def clear_required_field(self) -> str:
        """Clear an actual required control to exercise recovery with any record."""
        controls = self.form.locator("input, select, textarea")
        target = controls.evaluate_all("""inputs => {
            const instance = window.jQuery?.('#insurance-form').data('idealforms');
            for (let index = 0; index < inputs.length; index++) {
                const input = inputs[index];
                const rules = instance?.opts.rules[input.name] || '';
                if (!input.disabled && input.getClientRects().length
                    && (input.required || /(^| )(required|select)(:| |$)/.test(rules))
                    && !['radio', 'checkbox', 'hidden', 'file', 'button', 'submit'].includes(input.type)) {
                    return {index, name: input.name || input.id};
                }
            }
            return null;
        }""")
        if target is None:
            raise AssertionError("No visible required control is available for a recovery scenario")
        control = controls.nth(target["index"])
        if control.evaluate("input => input.tagName") == "SELECT":
            control.select_option(index=0)
        else:
            control.fill("")
        control.blur()
        return target["name"]
