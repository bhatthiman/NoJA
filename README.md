# Nozzle Junction Analyzer (NoJA)

NoJA is an internal MechXcel Designs LLP engineering tool for shell-to-pipe nozzle junction finite element evaluation in accordance with ASME Section VIII Division 2 Part 5 elastic stress analysis.

## Milestone 2a Scope

This branch contains the project skeleton plus shell and nozzle geometry generation:

- Python dependency list
- Configuration constants
- CSV input validation entry point
- Starter `Job.csv` input file
- Starter `materials.csv` input file
- Output folder placeholder
- Shell parameter reading from `input/Job.csv`
- Hollow cylindrical shell generation with CadQuery
- Hollow nozzle generation with angle, Y-direction centreline offset translation, outside projection, and inside projection inputs
- Shell opening cut with the nozzle outer profile using configurable boolean clearance before nozzle union
- Fish-mouth trimming for zero inside projection so the nozzle terminates flush with the shell ID
- `model.step` and `model.brep` export into each run output folder

Reinforcement pad geometry, meshing, solver execution, post-processing, stress classification, ASME checks, and report generation are intentionally not implemented in Milestone 2a.

## Project Layout

```text
input/Job.csv
materials/materials.csv
outputs/.gitkeep
config.py
input.py
geometry.py
run.py
requirements.txt
README.md
.gitignore
```

## Run

Install dependencies in a Python 3.11+ environment, then run:

```bash
python run.py
```

The command validates the CSV input files and creates a timestamped folder under `outputs/` containing a copy of `Job.csv`, `model.step`, and `model.brep`.
