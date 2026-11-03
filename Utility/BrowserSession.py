"""Browser lifecycle and trace collection shared by pytest and Behave."""

from contextlib import ExitStack
from pathlib import Path

from playwright.sync_api import sync_playwright


class BrowserSession:
    def __init__(self, config, artifacts_dir):
        self.config = config
        self.artifacts_dir = Path(artifacts_dir)
        self._resources = ExitStack()

    def __enter__(self):
        browser_name = self.config.browser.lower()
        if browser_name not in ("chromium", "firefox", "webkit"):
            raise ValueError(f"Unsupported browser: {browser_name}")

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        try:
            playwright = self._resources.enter_context(sync_playwright())
            browser = getattr(playwright, browser_name).launch(
                headless=self.config.headless
            )
            self._resources.callback(browser.close)
            context = browser.new_context()
            self._resources.callback(context.close)
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            self._resources.callback(
                context.tracing.stop,
                path=str(self.artifacts_dir / "trace.zip"),
            )
            self.page = context.new_page()
            self.page.set_default_timeout(self.config.default_timeout)
            self.page.set_default_navigation_timeout(self.config.navigation_timeout)
            return self
        except BaseException:
            self.close()
            raise

    def capture(self, name="final"):
        path = self.artifacts_dir / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def close(self):
        self._resources.close()

    def __exit__(self, exc_type, exc_value, traceback):
        return self._resources.__exit__(exc_type, exc_value, traceback)
