# Nozzle Junction Analyzer (NoJA)

NoJA is an internal MechXcel Designs LLP engineering tool for shell-to-pipe nozzle junction finite element evaluation in accordance with ASME Section VIII Division 2 Part 5 elastic stress analysis.

## status: Shell to nozzle geometry is working. next add RF pad at user's option

## input from file Job.csv shall be as below:
Section,Parameter,Value,Unit
Shell,Inside Diameter,1000,mm
Shell,Thickness,20,mm
Shell,Material Name,SA-516 Gr 70,
Nozzle,Outside Diameter,300,mm
Nozzle,Thickness,12,mm
Nozzle,Material Name,SA-106 Gr B,
Nozzle,Angle,80,degrees
Nozzle,Centreline Offset,300,mm
Nozzle,Outside Projection,250,mm
Nozzle,Inside Projection,0,mm
Reinforcement Pad,Enabled,No,
Reinforcement Pad,Outside Diameter,450,mm
Reinforcement Pad,Thickness,10,mm
Reinforcement Pad,Material,SA-516 Gr 70,
Loads,Load Case,Internal Pressure MPa,Fx N,Fy N,Fz N,Mx N-mm,My N-mm,Mz N-mm
Loads,LC1,1.0,0,0,0,0,0,0

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
