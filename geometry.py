"""CadQuery geometry generation for NoJA milestone 2a."""

from math import cos, radians, sin, sqrt
from pathlib import Path

import cadquery as cq

import config
from input import read_job_parameters


SHELL_SECTION = "Shell"
NOZZLE_SECTION = "Nozzle"
REINFORCEMENT_PAD_SECTION = "Reinforcement Pad"
INSIDE_DIAMETER_PARAMETER = "Inside Diameter"
THICKNESS_PARAMETER = "Thickness"
OUTSIDE_DIAMETER_PARAMETER = "Outside Diameter"
ANGLE_PARAMETER = "Angle"
CENTRELINE_OFFSET_PARAMETER = "Centreline Offset"
OUTSIDE_PROJECTION_PARAMETER = "Outside Projection"
INSIDE_PROJECTION_PARAMETER = "Inside Projection"
PAD_WIDTH_PARAMETER = "Pad Width"
MODEL_STEP_FILE = "model.step"
MODEL_BREP_FILE = "model.brep"
MINIMUM_ANGLE_DEGREES = 0.0
MAXIMUM_ANGLE_DEGREES = 180.0
MINIMUM_NOZZLE_RADIAL_COMPONENT = 0.05


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


def get_reinforcement_pad_parameters(job_path: Path = config.JOB_INPUT_FILE) -> dict[str, float]:
    """Read and validate RF pad width and thickness."""
    job_parameters = read_job_parameters(job_path)
    pad_parameters = _section_parameters(job_parameters, REINFORCEMENT_PAD_SECTION)
    try:
        pad_width = _positive_float(pad_parameters[PAD_WIDTH_PARAMETER], "RF pad width")
        pad_thickness = _positive_float(pad_parameters[THICKNESS_PARAMETER], "RF pad thickness")
    except KeyError as exc:
        raise ValueError(f"Job CSV is missing required RF pad parameter: {exc.args[0]}") from exc

    return {
        "pad_width": pad_width,
        "pad_thickness": pad_thickness,
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


def _shell_surface_point(shell_radius: float, centreline_offset: float) -> cq.Vector:
    """Return the shell outer-surface point for a Y-direction nozzle offset."""
    if abs(centreline_offset) >= shell_radius:
        raise ValueError("Nozzle centreline offset must be inside the shell outside radius.")
    surface_z = sqrt((shell_radius * shell_radius) - (centreline_offset * centreline_offset))
    return cq.Vector(0.0, centreline_offset, surface_z)


def _nozzle_axis(angle: float) -> cq.Vector:
    """Return the nozzle axis in the XZ plane so Y offset does not angle the nozzle."""
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
    shell_length: float,
    boolean_clearance: float = config.BOOLEAN_CLEARANCE,
) -> tuple[cq.Workplane, cq.Workplane]:
    """Build hollow nozzle geometry and its outer-profile shell cutter."""
    outside_diameter = _positive_float(str(outside_diameter), "Nozzle outside diameter")
    thickness = _positive_float(str(thickness), "Nozzle thickness")
    angle = _angle_float(str(angle), "Nozzle angle")
    outside_projection = _non_negative_float(str(outside_projection), "Nozzle outside projection")
    inside_projection = _non_negative_float(str(inside_projection), "Nozzle inside projection")
    length = _positive_float(str(length), "Nozzle length")
    shell_inside_diameter = _positive_float(str(shell_inside_diameter), "Shell inside diameter")
    shell_thickness = _positive_float(str(shell_thickness), "Shell thickness")
    shell_length = _positive_float(str(shell_length), "Shell length")
    boolean_clearance = _non_negative_float(str(boolean_clearance), "Boolean clearance")

    inside_diameter = outside_diameter - (2.0 * thickness)
    if inside_diameter <= 0.0:
        raise ValueError("Nozzle thickness must be less than half of nozzle outside diameter.")

    shell_inside_radius = shell_inside_diameter / 2.0
    if abs(centreline_offset) >= shell_inside_radius:
        raise ValueError("Nozzle centreline offset must be inside the shell inside radius.")
    shell_outside_radius = shell_inside_radius + shell_thickness
    fish_mouth_trim = inside_projection == 0.0
    inward_projection = inside_projection
    if fish_mouth_trim:
        radial_component = max(abs(sin(radians(angle))), MINIMUM_NOZZLE_RADIAL_COMPONENT)
        inward_projection = (shell_thickness / radial_component) + outside_diameter
    minimum_intersection_length = outside_projection + shell_thickness + inward_projection
    modeled_length = max(length, minimum_intersection_length, outside_diameter)
    inward_modeled_length = modeled_length - outside_projection
    shell_outer_point = _shell_surface_point(shell_outside_radius, centreline_offset)
    axis = _nozzle_axis(angle)
    center = shell_outer_point + (axis * ((outside_projection - inward_modeled_length) / 2.0))

    outer_radius = outside_diameter / 2.0
    inner_radius = inside_diameter / 2.0
    nozzle_outer = _cylinder(outer_radius, modeled_length, center, axis)
    nozzle_inner = _cylinder(inner_radius, modeled_length * 1.1, center, axis)
    nozzle_outer_cutter = _cylinder(
        outer_radius + boolean_clearance,
        modeled_length * 1.1,
        center,
        axis,
    )
    nozzle = nozzle_outer.cut(nozzle_inner)
    if fish_mouth_trim:
        shell_inner_cutter = _cylinder(
            shell_inside_radius,
            shell_length * 1.1,
            cq.Vector(0.0, 0.0, 0.0),
            cq.Vector(1.0, 0.0, 0.0),
        )
        nozzle = nozzle.cut(shell_inner_cutter)
    if not nozzle.val().isValid():
        raise ValueError("Generated nozzle geometry is invalid.")
    if not nozzle_outer_cutter.val().isValid():
        raise ValueError("Generated nozzle outer-profile cutter is invalid.")
    return nozzle, nozzle_outer_cutter


def build_rf_pad(
    shell: cq.Workplane,
    nozzle_outside_diameter: float,
    shell_inside_diameter: float,
    shell_thickness: float,
    angle: float,
    centreline_offset: float,
    outside_projection: float,
    width: float,
    pad_thickness: float,
) -> cq.Workplane:
    """
    Build reinforcement pad.

    Sequence:
        1. Outer cylinder (coaxial with nozzle)
        2. Intersect with shell
        3. Remove nozzle opening
        4. Thicken outward
    """

    shell_outside_radius = shell_inside_diameter / 2.0 + shell_thickness

    shell_outer_point = _shell_surface_point(
        shell_outside_radius,
        centreline_offset,
    )

    axis = _nozzle_axis(angle)

    outer_radius = nozzle_outside_diameter / 2.0 + width
    inner_radius = nozzle_outside_diameter / 2.0

    pad_length = (
        outside_projection
        + shell_thickness
        + pad_thickness
        + 2.0 * outer_radius
    )

    inward_length = pad_length - outside_projection

    center = shell_outer_point + (
        axis * ((outside_projection - inward_length) / 2.0)
    )

    # -----------------------------
    # Outer pad cylinder
    # -----------------------------

    outer_pad = _cylinder(
        outer_radius,
        pad_length,
        center,
        axis,
    )

    # -----------------------------
    # Nozzle cutter
    # -----------------------------

    nozzle_cutter = _cylinder(
        inner_radius,
        pad_length * 1.05,
        center,
        axis,
    )

    # -----------------------------
    shell_outer = _cylinder(
        shell_inside_diameter / 2.0 + shell_thickness,
        shell_inside_diameter * 4.0,
        cq.Vector(0.0, 0.0, 0.0),
        cq.Vector(1.0, 0.0, 0.0),
    )
    footprint_shape = outer_pad.val().intersect(shell_outer.val())
    footprint = cq.Workplane(obj=footprint_shape)
    opening_shape = footprint.val().cut(nozzle_cutter.val())
    footprint = cq.Workplane(obj=opening_shape)
    
    # -----------------------------
    # Thicken outward
    # -----------------------------

    pad_shape = footprint.val().offset(pad_thickness)
    pad = cq.Workplane(obj=pad_shape)

    if not pad.val().isValid():
        raise ValueError("Generated RF pad is invalid.")

    return pad


def build_model(job_path: Path = config.JOB_INPUT_FILE) -> cq.Workplane:
    """Build the shell, nozzle, and RF pad as one fused hollow solid body."""
    shell_parameters = get_shell_parameters(job_path)
    nozzle_parameters = get_nozzle_parameters(job_path)
    pad_parameters = get_reinforcement_pad_parameters(job_path)

    shell = build_shell(**shell_parameters)
    nozzle, nozzle_outer_cutter = build_nozzle(
        **nozzle_parameters,
        shell_inside_diameter=shell_parameters["inside_diameter"],
        shell_thickness=shell_parameters["thickness"],
        shell_length=shell_parameters["length"],
        boolean_clearance=config.BOOLEAN_CLEARANCE,
    )

    opened_shell = shell.cut(nozzle_outer_cutter)
    if not opened_shell.val().isValid():
        raise ValueError("Shell cut with nozzle outer profile produced invalid geometry.")

    model = opened_shell.union(nozzle)
    if not model.val().isValid():
        raise ValueError("Generated shell-and-nozzle model is invalid.")

    # Build RF pad at shell-nozzle junction
    rf_pad = build_rf_pad(
        shell=shell,
        nozzle_outside_diameter=nozzle_parameters["outside_diameter"],
        shell_thickness=shell_parameters["thickness"],
        shell_inside_diameter=shell_parameters["inside_diameter"],
        angle=nozzle_parameters["angle"],
        centreline_offset=nozzle_parameters["centreline_offset"],
        outside_projection=nozzle_parameters["outside_projection"],
        width=pad_parameters["pad_width"],
        pad_thickness=pad_parameters["pad_thickness"],
    )

    # Union RF pad with model
    model = model.union(rf_pad)
    if not model.val().isValid():
        raise ValueError("Generated model with RF pad is invalid.")

    solid_count = len(model.solids().vals())
    if solid_count != 1:
        raise ValueError(f"Generated model must contain one solid; found {solid_count} solids.")
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
