"""Command-line entry point for NoJA milestone runs."""

import logging
import shutil
from datetime import datetime
from pathlib import Path

import config
from geometry import export_shell_model
from input import validate_inputs


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)


def create_output_folder(timestamp: datetime | None = None) -> Path:
    """Create and return a timestamped output folder for a NoJA analysis run."""
    run_time = timestamp or datetime.now()
    if not isinstance(run_time, datetime):
        raise TypeError("timestamp must be a datetime instance or None.")
    output_folder = config.OUTPUTS_DIR / f"Job_{run_time:%Y%m%d_%H%M%S}"
    output_folder.mkdir(parents=True, exist_ok=False)
    return output_folder


def main() -> Path:
    """Validate inputs, prepare the output folder, and export shell geometry."""
    LOGGER.info("Validating input files.")
    validate_inputs()
    output_folder = create_output_folder()
    LOGGER.info("Created output folder: %s", output_folder)
    shutil.copy2(config.JOB_INPUT_FILE, output_folder / config.JOB_INPUT_FILE.name)
    LOGGER.info("Copied Job.csv to output folder.")
    exported_files = export_shell_model(output_folder)
    LOGGER.info("Exported shell STEP model: %s", exported_files["step"])
    LOGGER.info("Exported shell BREP model: %s", exported_files["brep"])
    return output_folder


if __name__ == "__main__":
    main()
