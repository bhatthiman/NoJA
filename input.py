"""CSV input validation for the NoJA milestone 1 skeleton."""

import csv
from pathlib import Path

import config

REQUIRED_JOB_SECTIONS = ("Shell", "Nozzle", "Reinforcement Pad", "Loads")
REQUIRED_JOB_COLUMNS = ("Section", "Parameter", "Value", "Unit")
REQUIRED_MATERIAL_COLUMNS = ("Material Name", "Elastic Modulus MPa", "Poisson Ratio", "Allowable Stress MPa")


def _require_csv(path: Path) -> Path:
    """Return a CSV path after verifying that it exists and is a .csv file."""
    if not isinstance(path, Path):
        raise TypeError("CSV path must be a pathlib.Path instance.")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Input file must be a .csv file: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file into dictionaries keyed by the header row."""
    csv_path = _require_csv(path)
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file is empty: {csv_path}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"CSV file contains no data rows: {csv_path}")
    return rows


def _validate_columns(actual_columns: list[str], required_columns: tuple[str, ...], file_label: str) -> None:
    """Validate that all required columns are present in a CSV header."""
    missing_columns = [column for column in required_columns if column not in actual_columns]
    if missing_columns:
        raise ValueError(f"{file_label} is missing required columns: {', '.join(missing_columns)}")


def read_job_parameters(path: Path = config.JOB_INPUT_FILE) -> dict[str, dict[str, str]]:
    """Read Job.csv into a nested dictionary keyed by section and parameter."""
    rows = _read_csv_rows(path)
    _validate_columns(list(rows[0].keys()), REQUIRED_JOB_COLUMNS, "Job CSV")
    parameters: dict[str, dict[str, str]] = {}
    for row in rows:
        section = row.get("Section", "").strip()
        parameter = row.get("Parameter", "").strip()
        value = row.get("Value", "").strip()
        if not section or not parameter:
            raise ValueError("Job CSV contains a row with an empty Section or Parameter.")
        parameters.setdefault(section, {})[parameter] = value
    return parameters


def validate_job_file(path: Path = config.JOB_INPUT_FILE) -> None:
    """Validate that the job CSV contains required milestone 1 sections and columns."""
    rows = _read_csv_rows(path)
    _validate_columns(list(rows[0].keys()), REQUIRED_JOB_COLUMNS, "Job CSV")
    sections = {row["Section"] for row in rows if row.get("Section")}
    missing_sections = [section for section in REQUIRED_JOB_SECTIONS if section not in sections]
    if missing_sections:
        raise ValueError(f"Job CSV is missing required sections: {', '.join(missing_sections)}")


def validate_materials_file(path: Path = config.MATERIALS_INPUT_FILE) -> None:
    """Validate that the materials CSV contains required material property columns."""
    rows = _read_csv_rows(path)
    _validate_columns(list(rows[0].keys()), REQUIRED_MATERIAL_COLUMNS, "Materials CSV")


def validate_inputs() -> None:
    """Validate all milestone 1 input files required before future analysis steps."""
    validate_job_file(config.JOB_INPUT_FILE)
    validate_materials_file(config.MATERIALS_INPUT_FILE)
