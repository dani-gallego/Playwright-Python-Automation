from datetime import datetime
import re

import pytest

from Config.EnvironmentConfig import EnvironmentConfig
from Config.ProjectPaths import PROJECT_PATHS
from Utility.BrowserSession import BrowserSession
from Utility.AllureReport import attach_browser_evidence
from Utility.TestDataReader import TestDataReader as QuoteDataReader


def pytest_addoption(parser):
    parser.addoption(
        "--test-case", default="TC001",
        help="testCase identifier to load unchanged from Data/CreateQuoteData.json",
    )


@pytest.fixture
def quote_data(request):
    data_file = PROJECT_PATHS.data / "CreateQuoteData.json"
    return QuoteDataReader.get_test_case_data(
        str(data_file), request.config.getoption("--test-case")
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"report_{report.when}", report)


@pytest.fixture(scope="session")
def environment_config():
    config = EnvironmentConfig()
    _ = config.base_url
    return config


@pytest.fixture(scope="session")
def artifacts_root():
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return PROJECT_PATHS.reports / "pytest" / run_id


@pytest.fixture
def page(request, environment_config, artifacts_root):
    name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", request.node.name)
    with BrowserSession(environment_config, artifacts_root / name) as session:
        try:
            yield session.page
        finally:
            report = getattr(request.node, "report_call", None)
            outcome = "failed" if report is None or report.failed else "final"
            session.capture(outcome)
            print(f"Browser evidence: {session.artifacts_dir}")
    # The context manager finalizes trace.zip before it is attached.
    attach_browser_evidence(session.artifacts_dir)
