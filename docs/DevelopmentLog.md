# Development Log

## Milestone 2a - Shell Geometry

- Created shell-only CadQuery geometry generation.
- Read shell inside diameter and thickness from `input/Job.csv`.
- Applied the hardcoded shell length rule from `config.py`: shell length equals 4 × shell ID.
- Added validation for invalid shell geometry, including non-positive inside diameter, non-positive thickness, and excessive thickness.
- Exported `model.step` and `model.brep` to each timestamped output folder.
- Added run logging for input validation, output folder creation, input copy, and CAD export steps.
- No nozzle or reinforcement pad geometry was implemented in this partial milestone.
