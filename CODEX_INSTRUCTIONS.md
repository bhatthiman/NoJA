# MechXcel Nozzle Junction Analyzer (NoJA) - Master Development Instructions

## 1. Project Objective

Develop an internal engineering software called **Nozzle Junction Analyzer (NoJA)** by MechXcel Designs LLP.

The software shall automatically perform Finite Element Analysis of shell-to-pipe (nozzle) junctions in accordance with **ASME Section VIII Division 2 Part 5 (Elastic Stress Analysis)**.

This is **NOT** intended to become a generic FEA platform.

It is a production tool used internally by MechXcel Designs LLP.

Primary objectives:

* Reduce engineering time
* Produce consistent analyses
* Produce consistent reports
* Require minimum user interaction
* Remain simple and maintainable
---

# 2. General Philosophy

Always prefer:

* Simplicity
* Readability
* Reliability
* Maintainability
Never add flexibility unless explicitly requested.
Hardcode engineering assumptions wherever practical.
Avoid unnecessary abstractions.
Avoid plugin systems.
Avoid frameworks.
Avoid premature optimization.
Avoid architecture that resembles a CAD or FEA platform.
This software solves exactly one engineering problem.
---

# 3. Version 1 Scope

Support ONLY:

* Cylindrical shell
* Single nozzle
* Angled nozzle
* Centreline offset
* Optional reinforcement pad
* Linear elastic analysis
* ASME VIII Div 2 Part 5
* Automatic report generation

Do NOT implement:

* Multiple nozzles
* Heads
* Saddles
* Lugs
* Cones
* Thermal analysis
* Nonlinear analysis
* Buckling
* Fatigue
* Contact analysis
* GUI
* Database
* REST API
* Cloud features
---

# 4. Software Stack

Language: Python 3.11+
Geometry : CadQuery
CAD Kernel : OpenCascade
Meshing : Gmsh OCC API
Solver : CalculiX
Spreadsheet : openpyxl
Reports : python-docx
Plots : matplotlib
Numerical : numpy
scipy : 
Data : pandas
Version Control : Git
Target Platform : Windows or webbased
---

# 5. Units

Length : mm
Stress : MPa
Force : N
Moment : N-mm
Pressure : MPa
Angle : Degrees
Internally use SI consistently.
---

# 6. Project Structure

NoJA/

```
input/
    Job.xlsx

materials/
    materials.xlsx

templates/
    Report_Template.docx

outputs/

docs/
    Architecture.md
    Assumptions.md
    DevelopmentLog.md

config.py
input.py
geometry.py
mesh.py
solver.py
post.py
scl.py
asme.py
report.py
run.py

requirements.txt
README.md
.gitignore
```

---

# 7. Input Data

Shell

* Inside Diameter
* Thickness
* Material Name

Nozzle

* Outside Diameter
* Thickness
* Material Name
* Angle
* Centreline Offset
* Outside Projection
* Inside Projection

Reinforcement Pad

* Enabled
* Outside Diameter
* Thickness
* Material

Loads

Multiple load cases. Each contains

* Internal Pressure and nozzle loads (Fx, Fy, Fz, Mx, My, Mz)

# 8. Hardcoded Engineering Assumptions

These shall not be changed.

Shell Length : 4 × Shell ID
Nozzle Length : 2 × Nozzle OD
Second Order Elements : Always enabled
Boundary Conditions: 
-----------
Shell End Constraints : Create a Remote Reference Point at each shell end. Couple each shell end face to its Remote Point. Use distributing coupling. Do NOT directly fix shell nodes.

Remote Point A : Restrain: UX, UY, UZ ; Allow : RX, RY, RZ
Remote Point B : Restrain: UY, UZ ; Allow : UX, RX, RY, RZ

This prevents rigid body motion while allowing axial expansion due to pressure.
------------

Mesh Strategy : Hex dominant mesh, element size = (min. of nozzle thickness or shell thickness) / 3 (to ensure minimum 3 elements across thickness). fine mesh at junction. coarser mesh away from junction.

Stress Classification Lines : 4 SCLs, 90 degree apart (total 360 degree) across shell thickness at junction, 4 SCLs, 90 degree apart across nozzle thickness at junction. 2 SCLs on Shell thickness 1D from junction, 2 SCLs on nozzle thickness 1D away from junction.

Report Format : Fixed

Folder Structure : Fixed as below

---

# 9. Output Folder

Each run shall automatically create

outputs/

Job_YYYYMMDD_HHMMSS/

containing

Job.xlsx

model.step

model.brep

mesh.inp

analysis.inp

solver output files

CSV files

Stress contour images

Deformation images

SCL output

Report.docx

Report.pdf

Everything for one analysis shall remain inside one folder.

---

# 10. Coding Standards

Prefer functions over classes.

Create classes only when clearly beneficial.

Maximum file size

Approximately 300 lines whenever practical.

Every function shall

* Have docstrings
* Validate inputs
* Raise meaningful exceptions

Never silently ignore errors.

Use descriptive names.

No magic numbers.

Engineering constants belong in config.py.

---

# 11. Geometry Philosophy

Create one fused solid body consisting of

Shell

*

Nozzle

*

Optional RF Pad (based on user choice in input)

Weld geometry shall NOT be modeled in Version 1.

---

# 12. Meshing Philosophy

Use Gmsh OCC.

Read BREP directly.

Export CalculiX INP.

Use tetrahedral second-order elements.

Automatically refine around the junction.

---

# 13. Solver Philosophy

Automatically generate CalculiX input.

Assign materials.

Assign pressure.

Assign nozzle loads.

Execute CalculiX.

Store results.

No user interaction.

---

# 14. Post Processing

Automatically extract

Displacements

Stress tensor

Principal stresses

Von Mises stress

Reaction forces

CSV output

Contour images

---

# 15. Stress Classification Lines

Automatic generation only.

No manual drawing.

Automatically identify required SCL locations.

Extract stresses through thickness.

Calculate

Primary Membrane

Primary Bending

Membrane + Bending

Peak Stress

Prepare data for ASME checks.

---

# 16. ASME VIII Div 2 Part 5

Implement elastic stress analysis checks.

Generate

Pass/Fail tables

Engineering summary

No design optimization.

Only evaluation.

---

# 17. Report

Automatically generate Report.docx.

Contents

Title Page

Input Summary

Materials

Geometry

Loads

Mesh

Boundary Conditions

Stress Contours

Stress Linearization

ASME Checks

Engineering Conclusion

Store report inside output folder.

---

# 18. Development Process

Work milestone by milestone.

Never implement future milestones early.

Each milestone shall compile successfully before continuing.

Wait for approval before moving to the next milestone.

---

# 19. Milestones

Milestone 1

Project skeleton

requirements.txt

config.py

run.py

input.py

Job.xlsx

materials.xlsx

README

.gitignore

Milestone 2

Geometry generation

STEP export

BREP export

Milestone 3

Meshing

Milestone 4

Solver

Milestone 5

Post Processing

Milestone 6

Stress Classification Lines

Milestone 7

ASME Part 5 Checks

Milestone 8

Report Generation

---

# 20. Important Rules

Never redesign the architecture without approval.

Never introduce unnecessary complexity.

Never create generic frameworks.

Never create plugin systems.

Never implement features outside the current milestone.

Whenever multiple approaches exist, choose the one with the least code that remains reliable.

Think like an engineering software developer—not like a framework developer.

The objective is an internal production tool that engineers at MechXcel can trust and use every day.

