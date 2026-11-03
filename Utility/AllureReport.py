"""Allure evidence attachments and HTML report generation."""

from pathlib import Path
import shutil
import subprocess

import allure

from Config.ProjectPaths import PROJECT_PATHS, ProjectPaths


def find_allure_cli():
    command = shutil.which("allure")
    if command is None:
        raise RuntimeError(
            "Allure CLI is missing from PATH. Install Allure Report before running "
            "run_tests.py (the Python adapters alone do not generate HTML)."
        )
    return command


def attach_browser_evidence(artifacts_dir):
    """Attach screenshots and the finalized trace to the active test."""
    artifacts_dir = Path(artifacts_dir)
    for name in ("failed", "final"):
        screenshot = artifacts_dir / f"{name}.png"
        if screenshot.is_file():
            allure.attach.file(
                str(screenshot), name=f"{name.title()} screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
    trace = artifacts_dir / "trace.zip"
    if trace.is_file():
        allure.attach.file(
            str(trace), name="Playwright trace",
            attachment_type="application/zip", extension="zip",
        )


def generate_report(command, results_dirs, paths: ProjectPaths = PROJECT_PATHS):
    project_root = paths.root.resolve()
    output_dir = paths.allure_report
    # --clean replaces only the generated report in this project.
    if not output_dir.resolve().is_relative_to(project_root):
        raise ValueError("The Allure output directory must be inside the project")
    result = subprocess.run(
        [command, "generate", *(str(path) for path in results_dirs),
         "--output", str(output_dir), "--clean"],
        cwd=project_root,
        check=False,
    )
    if result.returncode == 0 and not (output_dir / "index.html").is_file():
        raise RuntimeError("Allure exited successfully but produced no index.html")
    return result.returncode
