# Development Log

## Milestone 2a - Shell and Nozzle Geometry

- Created CadQuery geometry generation for the cylindrical shell and single nozzle.
- Read shell inside diameter and thickness from `input/Job.csv`.
- Applied the hardcoded shell length rule from `config.py`: shell length equals 4 × shell ID.
- Added validation for invalid shell geometry, including non-positive inside diameter, non-positive thickness, and excessive thickness.
- Added nozzle geometry using outside diameter, thickness, angle, centreline offset, outside projection, and inside projection inputs.
- Updated the shell-nozzle boolean sequence to cut the shell with the nozzle outer profile using configurable boolean clearance before unioning the nozzle.
- Changed nozzle centreline offset placement to the shell Y direction and trimmed zero-inside-projection nozzles against the shell inner cylinder to create a fish-mouth profile.
- Kept nozzle angle in the XZ plane so Y offset translates the nozzle without adding a Y-direction angular component, and limited zero-inside-projection inward trim stock so angled fish-mouth edges reach the shell ID without protruding through the opposite shell side.
- Exported `model.step` and `model.brep` to each timestamped output folder.
- Added run logging for input validation, output folder creation, input copy, and CAD export steps.
- Reinforcement pad geometry was not implemented in this milestone update.
