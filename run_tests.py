"""Run pytest and/or Behave, then save the HTML report to Reports/allure-report."""

import argparse
from datetime import datetime
import subprocess
import sys

from Utility.AllureReport import find_allure_cli, generate_report
from Config.ProjectPaths import PROJECT_PATHS


def run_suite(runner, results_dir, extra_args):
    results_dir.mkdir(parents=True, exist_ok=True)
    if runner == "pytest":
        arguments = [
            sys.executable, "-X", "utf8", "-m", "pytest", "--alluredir", str(results_dir),
            *extra_args,
        ]
    else:
        arguments = [
            sys.executable, "-X", "utf8", "-m", "behave", "Features",
            "--format", "pretty", "--outfile", "-",
            "--format", "allure_behave.formatter:AllureFormatter",
            "--outfile", str(results_dir), *extra_args,
        ]
    print(f"\nRunning {runner}; Allure results: {results_dir}", flush=True)
    return subprocess.run(arguments, cwd=PROJECT_PATHS.root, check=False).returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", choices=("pytest", "behave", "all"), default="all")
    parser.add_argument("test_args", nargs=argparse.REMAINDER,
                        help="Arguments after -- are passed to one selected runner")
    args = parser.parse_args(argv)
    extra_args = args.test_args
    if extra_args[:1] == ["--"]:
        extra_args = extra_args[1:]
    if args.runner == "all" and extra_args:
        parser.error("Select --runner pytest or --runner behave to pass test arguments")

    try:
        command = find_allure_cli()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 2

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    results_root = PROJECT_PATHS.allure_results / run_id
    runners = ("pytest", "behave") if args.runner == "all" else (args.runner,)
    results_dirs = []
    test_status = 0
    for runner in runners:
        results_dir = results_root / runner
        results_dirs.append(results_dir)
        status = run_suite(runner, results_dir, extra_args)
        if test_status == 0 and status != 0:
            test_status = status

    # Generate after the runner processes exit, including when tests failed.
    # Behave's after_all hook runs before its formatter has closed its output.
    try:
        report_status = generate_report(command, results_dirs, PROJECT_PATHS)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Could not generate Allure report: {error}", file=sys.stderr)
        report_status = 2
    if report_status == 0:
        print(f"\nAllure report: {PROJECT_PATHS.allure_report / 'index.html'}")
        print(f'View it with: allure open "{PROJECT_PATHS.allure_report}"')
    return test_status or report_status


if __name__ == "__main__":
    raise SystemExit(main())
