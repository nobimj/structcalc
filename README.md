# Structural Calculation Starter

A simple Python starter project for engineering calculations with step-by-step reports.

## What this does

- Keeps calculations reusable as normal Python functions
- Uses one expression string for calculation, formula display, substitution, and result display
- Records structured report steps that can be rendered later
- Generates an HTML report
- Can later be connected to a web app, desktop app, Excel, or API

## Install

```bash
cd structural_calc_starter
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
or 
pip install -e .
```

On Mac/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run example

```bash
python examples/run_beam_report.py
```

The report will be created in:

```text
outputs/beam_report.html
```

## Calculation pattern

Permanent calculation logic belongs in `src/structcalc/`. Jupyter notebooks should call
the package rather than contain the final engineering logic.

```python
from structcalc.calculations.beam import BeamInputs, simply_supported_beam_udl

inputs = BeamInputs(span_m=5.0, udl_kn_per_m=20.0)
result = simply_supported_beam_udl(inputs)
```

Calculation modules return a `ReportCalculationSheet`. It stores the report header,
inputs, calculation steps, final values, footer, and metadata in one plain object.
Each step contains one component such as an `Expression`, `Drawing`, `Table`, or
`TextBlock`.

## Suggested next steps

1. Add more calculations in `structcalc/calculations/`
2. Add Eurocode clause references to each check
3. Add PDF export using Playwright or WeasyPrint
4. Build a web interface using FastAPI, Django, or Streamlit

## Coding convetions
M__Ed The double underscore is used for subscript
Variable 