"""Check reporting and runner output without launching browsers."""

import run_tests
from Config.ProjectPaths import ProjectPaths


def test_failed_suite_still_generates_report_and_preserves_failure(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(run_tests, "PROJECT_PATHS", ProjectPaths(tmp_path))
    monkeypatch.setattr(run_tests, "find_allure_cli", lambda: "allure")

    def run_suite(runner, results_dir, extra_args):
        calls.append(runner)
        return 1 if runner == "pytest" else 0

    def generate_report(command, results_dirs, paths):
        calls.append("report")
        assert [path.name for path in results_dirs] == ["pytest", "behave"]
        assert paths.root == tmp_path
        assert paths.allure_report == tmp_path / "Reports" / "allure-report"
        assert all(path.parent.parent == tmp_path / "Reports" / "allure-results" for path in results_dirs)
        return 0

    monkeypatch.setattr(run_tests, "run_suite", run_suite)
    monkeypatch.setattr(run_tests, "generate_report", generate_report)
    assert run_tests.main(["--runner", "all"]) == 1
    assert calls == ["pytest", "behave", "report"]


def test_report_failure_fails_an_otherwise_successful_run(monkeypatch, tmp_path):
    monkeypatch.setattr(run_tests, "PROJECT_PATHS", ProjectPaths(tmp_path))
    monkeypatch.setattr(run_tests, "find_allure_cli", lambda: "allure")
    monkeypatch.setattr(run_tests, "run_suite", lambda *args: 0)
    monkeypatch.setattr(run_tests, "generate_report", lambda *args: 2)
    assert run_tests.main(["--runner", "pytest"]) == 2


def test_framework_processes_use_utf8_for_unicode_errors(monkeypatch, tmp_path, capfd):
    """Playwright error snapshots contain icons outside Windows' code page."""
    monkeypatch.setattr(run_tests, "PROJECT_PATHS", ProjectPaths(tmp_path))
    monkeypatch.setenv("PYTHONUTF8", "0")
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)
    for runner in ("pytest", "behave"):
        # Small stand-ins exercise actual child stdout without starting a suite.
        (tmp_path / f"{runner}.py").write_text("print('\\uf1cd')\n", encoding="utf-8")
        assert run_tests.run_suite(runner, tmp_path / runner, []) == 0

    assert capfd.readouterr().out.count("\uf1cd") == 2
