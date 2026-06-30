# Nozzle Junction Analyzer (NoJA)

NoJA is an internal MechXcel Designs LLP engineering tool for shell-to-pipe nozzle junction finite element evaluation in accordance with ASME Section VIII Division 2 Part 5 elastic stress analysis.

## Milestone 1 Scope

This branch contains only the project skeleton:

- Python dependency list
- Configuration constants
- CSV input validation entry point
- Starter `Job.csv` input file
- Starter `materials.csv` input file
- Output folder placeholder

Geometry generation, meshing, solver execution, post-processing, stress classification, ASME checks, and report generation are intentionally not implemented in Milestone 1.

## Project Layout

```text
input/Job.csv
materials/materials.csv
outputs/.gitkeep
config.py
input.py
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

The command validates the CSV input files and creates a timestamped folder under `outputs/` containing a copy of `Job.csv`.
