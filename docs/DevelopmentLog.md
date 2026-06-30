# Development Log

## Milestone 2a - Shell and Nozzle Geometry

- Created CadQuery geometry generation for the cylindrical shell and single nozzle.
- Read shell inside diameter and thickness from `input/Job.csv`.
- Applied the hardcoded shell length rule from `config.py`: shell length equals 4 × shell ID.
- Added validation for invalid shell geometry, including non-positive inside diameter, non-positive thickness, and excessive thickness.
- Added nozzle geometry using outside diameter, thickness, angle, centreline offset, outside projection, and inside projection inputs.
- Updated the shell-nozzle boolean sequence to cut the shell with the nozzle outer profile using configurable boolean clearance before unioning the nozzle.
- Changed nozzle centreline offset placement to the shell Y direction and trimmed zero-inside-projection nozzles against the shell inner cylinder to create a fish-mouth profile.
- Exported `model.step` and `model.brep` to each timestamped output folder.
- Added run logging for input validation, output folder creation, input copy, and CAD export steps.
- Reinforcement pad geometry was not implemented in this milestone update.
