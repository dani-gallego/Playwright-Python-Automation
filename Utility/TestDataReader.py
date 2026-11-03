import json
from pathlib import Path


class TestDataReader:
    """
    Generic utility for reading test data from JSON files.
    """

    # =========================================================
    # READ JSON
    # =========================================================

    @staticmethod
    def read_json(file_path: str) -> list[dict]:

        path = Path(file_path)

        if not path.exists():

            raise FileNotFoundError(
                f"Test data file not found: {file_path}"
            )

        with path.open(
            mode="r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # =========================================================
    # GET TEST CASE DATA
    # =========================================================

    @staticmethod
    def get_test_case_data(
        file_path: str,
        test_case: str
    ) -> dict:

        records = TestDataReader.read_json(
            file_path
        )

        for record in records:

            if record.get("testCase") == test_case:

                return record

        raise ValueError(
            f"Test case '{test_case}' "
            f"not found in {file_path}"
        )

    # =========================================================
    # GET ALL TEST DATA
    # =========================================================

    @staticmethod
    def get_all_records(
        file_path: str
    ) -> list[dict]:

        return TestDataReader.read_json(
            file_path
        )