"""Verify local dotenv and CI configuration without launching a browser."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from Config.ConfigReader import ConfigReader
from Config.EnvironmentConfig import EnvironmentConfig


class ConfigReaderTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.env_dir = self.root / "Config" / "environments"
        self.env_dir.mkdir(parents=True)
        file_patch = patch(
            "Config.ConfigReader.__file__", str(self.root / "Config" / "ConfigReader.py")
        )
        file_patch.start()
        self.addCleanup(file_patch.stop)
        env_patch = patch.dict(os.environ, {}, clear=True)
        env_patch.start()
        self.addCleanup(env_patch.stop)
        loaded_patch = patch.object(ConfigReader, "_loaded", False)
        loaded_patch.start()
        self.addCleanup(loaded_patch.stop)

    def test_ci_configuration_does_not_require_a_dotenv_file(self):
        os.environ.update(
            TEST_ENV="demoweb", ENVIRONMENT="demoweb",
            DEMO_BASE_URL="https://example.invalid/", USERNAME="test@example.invalid",
            PASSWORD="test-only-placeholder",
        )
        config = EnvironmentConfig()
        self.assertEqual(config.base_url, "https://example.invalid/")
        self.assertEqual(config.environment, "demoweb")
        self.assertEqual(config.username, "test@example.invalid")
        self.assertEqual(config.password, "test-only-placeholder")

    def test_local_file_loads_without_overriding_injected_values(self):
        os.environ.update(TEST_ENV="DEMOWEB", PASSWORD="injected-placeholder")
        (self.env_dir / ".env.demoweb").write_text(
            "USERNAME=local@example.invalid\nPASSWORD=local-placeholder\n",
            encoding="utf-8",
        )
        config = EnvironmentConfig()
        self.assertEqual(config.username, "local@example.invalid")
        self.assertEqual(config.password, "injected-placeholder")

    def test_missing_required_secret_fails_without_exposing_values(self):
        os.environ["USERNAME"] = "test@example.invalid"
        with self.assertRaisesRegex(ValueError, "Required configuration 'PASSWORD'"):
            _ = EnvironmentConfig().password

    def test_optional_settings_keep_defaults_without_a_dotenv_file(self):
        config = EnvironmentConfig()
        self.assertEqual(config.browser, "chromium")
        self.assertEqual(config.default_timeout, 30000)


if __name__ == "__main__":
    unittest.main()
