# Report Creation Engine Architecture

## Objective

Create a core report generation engine that can produce:

* HTML
* PDF
* JSON

The engine must be usable through a function call or API.

The design calculation function is responsible only for creating report data. Rendering to HTML, PDF, or JSON is handled separately by the report engine.

---

# Report Structure

A report is made from:

```text
Report
├── Header
├── Body
│   └── Steps
└── Footer
```

The HTML and PDF output shall be generated using templates.

The template shall define:

* Header layout
* Footer layout
* Body layout
* Step rendering style
* Component rendering style

---

# Report Function

Each design report shall be created by a single function.

Example:

```python
def beam_design_report(inputs) -> Report:
    ...
```

This function shall create:

* Header
* Footer
* Steps
* Final values
* Metadata

The function shall expose the report as JSON so it can be used by:

* HTML renderer
* PDF renderer
* API response
* Storage/database
* Future UI

---

# Step Structure

A step is the basic unit of the report.

```text
Step
├── metadata
├── title
├── text_before
├── component
└── text_after
```

## Step Fields

### metadata

Used for tagging and filtering.

Examples:

* pass / fail
* warning
* design section
* final result
* code clause
* member name
* load case
* utilization value

### title

The title of the calculation step.

Example:

```text
Bending resistance check
```

### text_before

Text shown before the main component.

This can include:

* explanation
* assumption
* code reference
* design note
* warning
* input description

### component

The main report component.

Each step has one main component.

### text_after

Text shown after the component.

This can include:

* conclusion
* pass/fail statement
* warning
* engineering judgement
* design selection note

---

# Components

Each step shall contain one of the following component types:

```text
Component
├── Expression
├── Drawing
├── Table
└── TextBlock
```

---

# 1. Expression

Used for mathematical calculations.

```text
Expression
├── AutoExpression
├── StepExpression
└── ManualExpression
```

## AutoExpression

`AutoExpression` is the core automatic expression class.

The user provides:

* symbolic expression
* input variables
* values of input variables
* units where applicable

The class shall automatically generate:

* LaTeX expression
* substitution display
* final value
* result attributes

Important:

```text
Do not modify report_auto_expression.py
```

This file contains the core `AutoExpression` class.

## StepExpression

Used when the calculation needs intermediate steps.

Example:

```text
M_Rd = W_pl f_y / γ_M0
     = 556 × 355 / 1.0
     = 197.4 kNm
```

## ManualExpression

Escape hatch for special cases.

Used when automatic expression generation is not suitable.

The user manually provides:

* LaTeX
* substitution text
* result
* units
* comments if needed

---

# 2. Drawing

Used for all visual drawing-based components.

This includes:

* beam cross-section
* column cross-section
* I-section geometry
* connection sketch
* bending moment diagram
* shear force diagram
* axial force diagram
* interaction curve
* stress-strain curve
* stress distribution
* FEA contour plot

The report engine shall treat all of these as `Drawing`.

The drawing may be rendered as:

* SVG
* Canvas
* image
* HTML drawing
* exported PNG/PDF graphic

---

# 3. Table

Used for tabular data.

The source data may be:

* pandas DataFrame
* list of dictionaries
* list of rows
* JSON table data

Examples:

* section properties
* load combinations
* material properties
* design results
* utilization summary

---

# 4. TextBlock

Used for plain or styled text.

This can represent:

* explanation
* warning
* assumption
* note
* reference
* design decision
* selection statement
* conclusion

TextBlock may have a style such as:

```text
normal
note
warning
assumption
reference
success
failure
```

---

# Rendering Principle

The calculation function creates structured report data.

The renderer decides how to display it.

```text
Calculation Function → Report JSON → Renderer → HTML / PDF / JSON
```

The calculation logic must not directly generate HTML or PDF.

---

# Core Design Principle

Keep the report model small.

Use only four main component types:

```text
TextBlock
Expression
Table
Drawing
```

Warnings, explanations, references, assumptions, and selections are handled as styled `TextBlock`.

Figures, diagrams, graphs, charts, and engineering sketches are handled as `Drawing`.

Equations, checks, substitutions, and calculation results are handled as `Expression`.
