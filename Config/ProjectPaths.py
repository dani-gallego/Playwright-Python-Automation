"""Project-wide output paths, independent of the current working directory."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])

    @property
    def data(self) -> Path:
        return self.root / "Data"

    @property
    def logs(self) -> Path:
        return self.root / "Logs"

    @property
    def reports(self) -> Path:
        return self.root / "Reports"

    @property
    def allure_results(self) -> Path:
        return self.reports / "allure-results"

    @property
    def allure_report(self) -> Path:
        return self.reports / "allure-report"


PROJECT_PATHS = ProjectPaths()
