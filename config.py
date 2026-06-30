"""Configuration constants for the Nozzle Junction Analyzer milestone 1 skeleton."""

from pathlib import Path

PROJECT_NAME = "Nozzle Junction Analyzer"
PROJECT_SHORT_NAME = "NoJA"
COMPANY_NAME = "MechXcel Designs LLP"

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
MATERIALS_DIR = BASE_DIR / "materials"
OUTPUTS_DIR = BASE_DIR / "outputs"

JOB_INPUT_FILE = INPUT_DIR / "Job.csv"
MATERIALS_INPUT_FILE = MATERIALS_DIR / "materials.csv"

LENGTH_UNIT = "mm"
STRESS_UNIT = "MPa"
FORCE_UNIT = "N"
MOMENT_UNIT = "N-mm"
PRESSURE_UNIT = "MPa"
ANGLE_UNIT = "degrees"

SHELL_LENGTH_ID_MULTIPLIER = 4.0
NOZZLE_LENGTH_OD_MULTIPLIER = 2.0
MESH_ELEMENTS_THROUGH_THICKNESS = 3
SECOND_ORDER_ELEMENTS = True
