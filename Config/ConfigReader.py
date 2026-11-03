import os
from pathlib import Path
from dotenv import load_dotenv


class ConfigReader:

    _loaded = False

    @classmethod
    def load(cls):
        if cls._loaded:
            return

        environment = os.getenv("TEST_ENV", "sit").lower()

        project_root = Path(__file__).resolve().parent.parent

        env_file = (
            project_root
            / "Config"
            / "environments"
            / f".env.{environment}"
        )

        if not env_file.exists():
            raise FileNotFoundError(
                f"Environment file not found: {env_file}"
            )

        load_dotenv(env_file)

        cls._loaded = True

    @classmethod
    def get(cls, key: str, default=None):
        cls.load()
        return os.getenv(key, default)

    @classmethod
    def get_required(cls, key: str):
        cls.load()

        value = os.getenv(key)

        if not value:
            raise ValueError(
                f"Required configuration '{key}' is not defined."
            )

        return value

    @classmethod
    def get_boolean(cls, key: str, default=False):
        value = cls.get(key, str(default))

        return value.lower() in ("true", "1", "yes", "y")

    @classmethod
    def get_integer(cls, key: str, default=0):
        value = cls.get(key, str(default))

        return int(value)