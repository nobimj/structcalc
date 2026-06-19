# AGENTS.md

## Project Purpose

This project is a structural engineering calculation and reporting framework.

The objective is to build reusable Python modules that:

* perform engineering calculations,
* generate structured calculation reports,
* export reports as JSON,
* render reports as HTML and PDF,
* support future web, desktop, and API applications.

The framework should provide a calculation experience similar to Mathcad or TEDDS while maintaining clean, maintainable Python code.

---

# Core Philosophy

## Calculations and Rendering Are Separate

Engineering calculations must never generate HTML or PDF directly.

Calculation modules create structured report data.

Renderers convert that report data into:

* HTML
* PDF
* JSON
* future output formats

Architecture:

```text
Calculation Function
        ↓
     Report
        ↓
 JSON Representation
        ↓
HTML / PDF Renderer
```

---

# Report Model

A report consists of:

```text
Report
├── Header
├── Body
│   └── Steps
└── Footer
```

The report object is the canonical representation.

HTML and PDF are generated from templates.

---

# Report Function

Each engineering calculation shall expose a single report function.

Example:

```python
def beam_bending_report(inputs) -> Report:
    ...
```

The function is responsible for:

* creating header data,
* creating footer data,
* creating report steps,
* exposing final values,
* returning a complete report.

The function must not generate HTML.

---

# Step Model

A step is the fundamental report unit.

```text
Step
├── metadata
├── title
├── text_before
├── component
└── text_after
```

## Metadata

Metadata is used for filtering, grouping, and report summaries.

Examples:

```text
pass
fail
warning
section
final_result
code_clause
utilization
```

Metadata is not presentation.

It is structured information.

---

# Components

Each step contains exactly one component.

Supported components:

```text
Component
├── Expression
├── Drawing
├── Table
└── TextBlock
```

Keep the component system small.

Do not create unnecessary component types.

---

# Expression

Expressions represent mathematical calculations.

```text
Expression
├── AutoExpression
├── StepExpression
└── ManualExpression
```

## AutoExpression

AutoExpression is the preferred implementation.

The user provides:

* symbolic formula
* variable values
* output symbol
* units

The system generates:

* symbolic display
* LaTeX display
* substitution display
* final result

The formula must be written once.

Example:

```python
AutoExpression(
    "MEd",
    "w*L**2/8",    
        w= 20,
        L= 5,
    }
    
)
```

The formula string is the single source of truth.

Avoid duplicating formula logic.

## StepExpression

Used when intermediate calculation steps are required.

Example:

```text
MRd = Wpl fy / γM0
    = 556 × 355 / 1.0
    = 197.4 kNm
```

## ManualExpression

Escape hatch for special cases.

Allows manual control of displayed content.

Use only when automatic generation is not practical.

---

# Drawing

Drawing represents any visual engineering output.

Examples:

* beam cross-section
* column cross-section
* connection sketch
* bending moment diagram
* shear force diagram
* interaction curve
* stress-strain curve
* stress distribution
* finite element contour plot

The report engine does not distinguish between figure, diagram, chart, or graph.

All visual outputs are treated as:

```text
Drawing
```

The renderer decides how the drawing is displayed.

---

# Table

Represents structured tabular data.

Supported sources:

* pandas DataFrame
* list of dictionaries
* JSON table data

Examples:

* section properties
* material properties
* load combinations
* utilization summaries

---

# TextBlock

Represents formatted text.

Examples:

* explanations
* assumptions
* warnings
* references
* conclusions
* design notes

TextBlock may contain styling metadata.

Examples:

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

# JSON First

The report model must be serializable to JSON.

JSON is the canonical interchange format.

Example workflow:

```text
Calculation
    ↓
Report Object
    ↓
JSON
    ↓
HTML Renderer

or

JSON
    ↓
PDF Renderer
```

---

# Package Structure

Preferred structure:

```text
src/
└── structcalc/
    ├── report/
    │   ├── report.py
    │   ├── step.py
    │   ├── components/
    │   │   ├── expression.py
    │   │   ├── drawing.py
    │   │   ├── table.py
    │   │   └── textblock.py
    │   └── renderers/
    │       ├── html/
    │       └── pdf/
    │
    ├── calculations/
    │   ├── aci/
    │   ├── eurocode/
    │   └── common/
    │
    ├── config/
    │   ├──settings.py

---

# Development Rules

## Do

* Keep calculations separate from rendering.
* Use AutoExpression whenever possible.
* Keep formulas defined once.
* Return structured report data.
* Keep components generic.
* Keep report objects JSON serializable.
* Attach code references through metadata or TextBlocks.
* Write reusable calculation modules.

## Avoid

* Generating HTML inside calculations.
* Generating PDF inside calculations.
* Creating specialized component types for every engineering concept.
* Distinguishing between figures, diagrams, and graphs in the core model.
* Duplicating formulas in multiple places.
* Hardcoding report formatting inside engineering calculations.

---

# Long-Term Direction

The framework should support:

* Eurocode 2
* Eurocode 3
* ACI 318
* load combinations
* material libraries
* pass/fail checks
* utilization calculations
* warnings and assumptions
* HTML reports
* PDF reports
* web applications
* desktop applications
* APIs

The foundation remains:

```text
Calculation
    ↓
Structured Report
    ↓
JSON
    ↓
Renderer
```
