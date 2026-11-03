"""Behave lifecycle using the same browser utility as the pytest suite."""

from datetime import datetime
import re

from Config.EnvironmentConfig import EnvironmentConfig
from Config.ProjectPaths import PROJECT_PATHS
from Utility.BrowserSession import BrowserSession
from Utility.AllureReport import attach_browser_evidence
from Utility.Logger import Logger


def before_all(context):
    context.environment_config = EnvironmentConfig()
    _ = context.environment_config.base_url
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    context.artifacts_root = PROJECT_PATHS.reports / "behave" / run_id


def before_scenario(context, scenario):
    name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", scenario.name)
    context.browser_session = BrowserSession(
        context.environment_config, context.artifacts_root / name
    )
    context.page = context.browser_session.__enter__().page


def after_scenario(context, scenario):
    session = getattr(context, "browser_session", None)
    if session is None:
        return
    try:
        if hasattr(session, "page"):
            status = "failed" if scenario.status.name in ("failed", "error", "hook_error") else "final"
            session.capture(status)
    except Exception:
        Logger.exception("Could not capture scenario screenshot")
    finally:
        session.close()
    attach_browser_evidence(session.artifacts_dir)
