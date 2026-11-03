from Config.ConfigReader import ConfigReader


class EnvironmentConfig:

    @property
    def environment(self):
        return ConfigReader.get_required("ENVIRONMENT")

    @property
    def base_url(self):
        return ConfigReader.get_required("BASE_URL")

    @property
    def username(self):
        return ConfigReader.get_required("USERNAME")

    @property
    def password(self):
        return ConfigReader.get_required("PASSWORD")

    @property
    def browser(self):
        return ConfigReader.get("BROWSER", "chromium")

    @property
    def headless(self):
        return ConfigReader.get_boolean("HEADLESS", False)

    @property
    def default_timeout(self):
        return ConfigReader.get_integer(
            "DEFAULT_TIMEOUT",
            30000
        )

    @property
    def navigation_timeout(self):
        return ConfigReader.get_integer(
            "NAVIGATION_TIMEOUT",
            60000
        )

    @property
    def action_delay(self):
        return ConfigReader.get_integer(
            "ACTION_DELAY",
            0
        )
