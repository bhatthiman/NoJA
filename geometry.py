"""Shell-only CadQuery geometry generation for NoJA milestone 2a."""

from pathlib import Path

import config
from input import read_job_parameters


SHELL_SECTION = "Shell"
INSIDE_DIAMETER_PARAMETER = "Inside Diameter"
THICKNESS_PARAMETER = "Thickness"
MODEL_STEP_FILE = "model.step"
MODEL_BREP_FILE = "model.brep"


def _positive_float(value: str, label: str) -> float:
    """Convert a CSV value to a positive float for geometry generation."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a numeric value.") from exc
    if number <= 0.0:
        raise ValueError(f"{label} must be greater than zero; received {number}.")
    return number


def get_shell_parameters(job_path: Path = config.JOB_INPUT_FILE) -> dict[str, float]:
    """Read and validate shell inside diameter, thickness, and derived length."""
    job_parameters = read_job_parameters(job_path)
    try:
        shell_parameters = job_parameters[SHELL_SECTION]
        inside_diameter = _positive_float(
            shell_parameters[INSIDE_DIAMETER_PARAMETER],
            "Shell inside diameter",
        )
        thickness = _positive_float(shell_parameters[THICKNESS_PARAMETER], "Shell thickness")
    except KeyError as exc:
        raise ValueError(f"Job CSV is missing required shell parameter: {exc.args[0]}") from exc

    inside_radius = inside_diameter / 2.0
    if thickness >= inside_radius:
        raise ValueError(
            "Shell thickness must be less than the inside radius to create valid hollow geometry."
        )

    return {
        "inside_diameter": inside_diameter,
        "thickness": thickness,
        "length": config.SHELL_LENGTH_ID_MULTIPLIER * inside_diameter,
    }


def build_shell(inside_diameter: float, thickness: float, length: float):
    """Build a hollow cylindrical shell aligned with the global X axis."""
    import cadquery as cq

    inside_diameter = _positive_float(str(inside_diameter), "Shell inside diameter")
    thickness = _positive_float(str(thickness), "Shell thickness")
    length = _positive_float(str(length), "Shell length")

    inside_radius = inside_diameter / 2.0
    outside_radius = inside_radius + thickness
    if thickness >= inside_radius:
        raise ValueError(
            "Shell thickness must be less than the inside radius to create valid hollow geometry."
        )

    outer_cylinder = cq.Workplane("YZ").circle(outside_radius).extrude(length, both=True)
    inner_cylinder = cq.Workplane("YZ").circle(inside_radius).extrude(length * 1.1, both=True)
    shell = outer_cylinder.cut(inner_cylinder)

    if not shell.val().isValid():
        raise ValueError("Generated shell geometry is invalid.")
    return shell


def export_shell_model(output_folder: Path, job_path: Path = config.JOB_INPUT_FILE) -> dict[str, Path]:
    """Build the shell from Job.csv and export STEP and BREP files to the output folder."""
    if not isinstance(output_folder, Path):
        raise TypeError("output_folder must be a pathlib.Path instance.")
    output_folder.mkdir(parents=True, exist_ok=True)

    shell_parameters = get_shell_parameters(job_path)
    shell = build_shell(**shell_parameters)

    step_path = output_folder / MODEL_STEP_FILE
    brep_path = output_folder / MODEL_BREP_FILE
    cq.exporters.export(shell, str(step_path))
    cq.exporters.export(shell, str(brep_path))

    return {"step": step_path, "brep": brep_path}
