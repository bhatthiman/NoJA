"""CadQuery geometry generation for NoJA milestone 2a."""

from math import cos, radians, sin
from pathlib import Path

import cadquery as cq

import config
from input import read_job_parameters


SHELL_SECTION = "Shell"
NOZZLE_SECTION = "Nozzle"
INSIDE_DIAMETER_PARAMETER = "Inside Diameter"
THICKNESS_PARAMETER = "Thickness"
OUTSIDE_DIAMETER_PARAMETER = "Outside Diameter"
ANGLE_PARAMETER = "Angle"
CENTRELINE_OFFSET_PARAMETER = "Centreline Offset"
OUTSIDE_PROJECTION_PARAMETER = "Outside Projection"
INSIDE_PROJECTION_PARAMETER = "Inside Projection"
MODEL_STEP_FILE = "model.step"
MODEL_BREP_FILE = "model.brep"
MINIMUM_ANGLE_DEGREES = 0.0
MAXIMUM_ANGLE_DEGREES = 180.0


def _positive_float(value: str, label: str) -> float:
    """Convert a CSV value to a positive float for geometry generation."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a numeric value.") from exc
    if number <= 0.0:
        raise ValueError(f"{label} must be greater than zero; received {number}.")
    return number


def _non_negative_float(value: str, label: str) -> float:
    """Convert a CSV value to a non-negative float for geometry generation."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a numeric value.") from exc
    if number < 0.0:
        raise ValueError(f"{label} must be zero or greater; received {number}.")
    return number


def _angle_float(value: str, label: str) -> float:
    """Convert and validate a nozzle angle in degrees."""
    angle = _positive_float(value, label)
    if angle <= MINIMUM_ANGLE_DEGREES or angle >= MAXIMUM_ANGLE_DEGREES:
        raise ValueError(f"{label} must be between 0 and 180 degrees; received {angle}.")
    return angle


def _section_parameters(job_parameters: dict[str, dict[str, str]], section: str) -> dict[str, str]:
    """Return one Job.csv section or raise a clear validation error."""
    try:
        return job_parameters[section]
    except KeyError as exc:
        raise ValueError(f"Job CSV is missing required section: {section}") from exc


def get_shell_parameters(job_path: Path = config.JOB_INPUT_FILE) -> dict[str, float]:
    """Read and validate shell inside diameter, thickness, and derived length."""
    job_parameters = read_job_parameters(job_path)
    shell_parameters = _section_parameters(job_parameters, SHELL_SECTION)
    try:
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


def get_nozzle_parameters(job_path: Path = config.JOB_INPUT_FILE) -> dict[str, float]:
    """Read and validate nozzle dimensions, angle, offset, and projections."""
    job_parameters = read_job_parameters(job_path)
    nozzle_parameters = _section_parameters(job_parameters, NOZZLE_SECTION)
    try:
        outside_diameter = _positive_float(
            nozzle_parameters[OUTSIDE_DIAMETER_PARAMETER],
            "Nozzle outside diameter",
        )
        thickness = _positive_float(nozzle_parameters[THICKNESS_PARAMETER], "Nozzle thickness")
        angle = _angle_float(nozzle_parameters[ANGLE_PARAMETER], "Nozzle angle")
        centreline_offset = float(nozzle_parameters[CENTRELINE_OFFSET_PARAMETER])
        outside_projection = _non_negative_float(
            nozzle_parameters[OUTSIDE_PROJECTION_PARAMETER],
            "Nozzle outside projection",
        )
        inside_projection = _non_negative_float(
            nozzle_parameters[INSIDE_PROJECTION_PARAMETER],
            "Nozzle inside projection",
        )
    except KeyError as exc:
        raise ValueError(f"Job CSV is missing required nozzle parameter: {exc.args[0]}") from exc
    except ValueError as exc:
        if "could not convert" in str(exc):
            raise ValueError("Nozzle centreline offset must be a numeric value.") from exc
        raise

    inside_diameter = outside_diameter - (2.0 * thickness)
    if inside_diameter <= 0.0:
        raise ValueError("Nozzle thickness must be less than half of nozzle outside diameter.")

    return {
        "outside_diameter": outside_diameter,
        "thickness": thickness,
        "angle": angle,
        "centreline_offset": centreline_offset,
        "outside_projection": outside_projection,
        "inside_projection": inside_projection,
        "length": config.NOZZLE_LENGTH_OD_MULTIPLIER * outside_diameter,
    }


def build_shell(inside_diameter: float, thickness: float, length: float) -> cq.Workplane:
    """Build a hollow cylindrical shell aligned with the global X axis."""
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


def _nozzle_axis(angle: float) -> cq.Vector:
    """Return the nozzle axis vector in the shell XZ plane."""
    angle_radians = radians(angle)
    return cq.Vector(cos(angle_radians), 0.0, sin(angle_radians)).normalized()


def _cylinder(radius: float, length: float, center: cq.Vector, direction: cq.Vector) -> cq.Workplane:
    """Create a CadQuery cylinder from center, length, radius, and axis direction."""
    start = center - (direction * (length / 2.0))
    solid = cq.Solid.makeCylinder(radius, length, start, direction)
    return cq.Workplane(obj=solid)


def build_nozzle(
    outside_diameter: float,
    thickness: float,
    angle: float,
    centreline_offset: float,
    outside_projection: float,
    inside_projection: float,
    length: float,
    shell_inside_diameter: float,
    shell_thickness: float,
) -> tuple[cq.Workplane, cq.Workplane]:
    """Build hollow nozzle geometry and its bore cutter."""
    outside_diameter = _positive_float(str(outside_diameter), "Nozzle outside diameter")
    thickness = _positive_float(str(thickness), "Nozzle thickness")
    angle = _angle_float(str(angle), "Nozzle angle")
    outside_projection = _non_negative_float(str(outside_projection), "Nozzle outside projection")
    inside_projection = _non_negative_float(str(inside_projection), "Nozzle inside projection")
    length = _positive_float(str(length), "Nozzle length")
    shell_inside_diameter = _positive_float(str(shell_inside_diameter), "Shell inside diameter")
    shell_thickness = _positive_float(str(shell_thickness), "Shell thickness")

    inside_diameter = outside_diameter - (2.0 * thickness)
    if inside_diameter <= 0.0:
        raise ValueError("Nozzle thickness must be less than half of nozzle outside diameter.")

    shell_outside_radius = (shell_inside_diameter / 2.0) + shell_thickness
    minimum_intersection_length = outside_projection + shell_thickness + inside_projection
    modeled_length = max(length, minimum_intersection_length, outside_diameter)
    axis = _nozzle_axis(angle)
    shell_outer_point = cq.Vector(centreline_offset, 0.0, shell_outside_radius)
    center = shell_outer_point + (axis * ((outside_projection - inside_projection) / 2.0))

    nozzle_outer = _cylinder(outside_diameter / 2.0, modeled_length, center, axis)
    nozzle_inner = _cylinder(inside_diameter / 2.0, modeled_length * 1.1, center, axis)
    nozzle = nozzle_outer.cut(nozzle_inner)
    if not nozzle.val().isValid():
        raise ValueError("Generated nozzle geometry is invalid.")
    return nozzle, nozzle_inner


def build_model(job_path: Path = config.JOB_INPUT_FILE) -> cq.Workplane:
    """Build the shell and nozzle as one fused hollow solid body."""
    shell_parameters = get_shell_parameters(job_path)
    nozzle_parameters = get_nozzle_parameters(job_path)
    shell = build_shell(**shell_parameters)
    nozzle, nozzle_bore_cutter = build_nozzle(
        **nozzle_parameters,
        shell_inside_diameter=shell_parameters["inside_diameter"],
        shell_thickness=shell_parameters["thickness"],
    )
    model = shell.cut(nozzle_bore_cutter).union(nozzle)
    if not model.val().isValid():
        raise ValueError("Generated shell-and-nozzle model is invalid.")
    return model


def export_model(output_folder: Path, job_path: Path = config.JOB_INPUT_FILE) -> dict[str, Path]:
    """Build the model from Job.csv and export STEP and BREP files to the output folder."""
    if not isinstance(output_folder, Path):
        raise TypeError("output_folder must be a pathlib.Path instance.")
    output_folder.mkdir(parents=True, exist_ok=True)

    model = build_model(job_path)
    step_path = output_folder / MODEL_STEP_FILE
    brep_path = output_folder / MODEL_BREP_FILE
    cq.exporters.export(model, str(step_path))
    cq.exporters.export(model, str(brep_path))

    return {"step": step_path, "brep": brep_path}


def export_shell_model(output_folder: Path, job_path: Path = config.JOB_INPUT_FILE) -> dict[str, Path]:
    """Export the current milestone model while preserving the old function name."""
    return export_model(output_folder, job_path)
