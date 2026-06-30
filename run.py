"""Milestone 1 command-line entry point for the NoJA project skeleton."""

import shutil
from datetime import datetime
from pathlib import Path

import config
from input import validate_inputs


def create_output_folder(timestamp: datetime | None = None) -> Path:
    """Create and return a timestamped output folder for a NoJA analysis run."""
    run_time = timestamp or datetime.now()
    if not isinstance(run_time, datetime):
        raise TypeError("timestamp must be a datetime instance or None.")
    output_folder = config.OUTPUTS_DIR / f"Job_{run_time:%Y%m%d_%H%M%S}"
    output_folder.mkdir(parents=True, exist_ok=False)
    return output_folder


def main() -> Path:
    """Validate milestone 1 inputs and prepare the run output folder."""
    validate_inputs()
    output_folder = create_output_folder()
    shutil.copy2(config.JOB_INPUT_FILE, output_folder / config.JOB_INPUT_FILE.name)
    print(f"NoJA milestone 1 input validation complete: {output_folder}")
    return output_folder


if __name__ == "__main__":
    main()
