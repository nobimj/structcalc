from pathlib import Path

from structcalc.calculations.beam import BeamInputs, simply_supported_beam_udl


def test_simply_supported_beam_udl():
    inputs = BeamInputs(span=5.0, udl=20.0, width=300.0, height=500.0)
    sheet = simply_supported_beam_udl(inputs)

    assert sheet.final_values["M__Ed"] == 62.5
    assert sheet.final_values["V__Ed"] == 50.0
    assert sheet.final_values["A"] == 150000.0
    assert sheet.final_values["I"] == 3125000000.0
    assert sheet.final_values["sigma_top"] == -5.0
    assert sheet.final_values["sigma_bottom"] == 5.0

    assert sheet.input_table.rows == [
        {"Parameter": "Span", "Symbol": "L", "Value": "5.0 m"},
        {"Parameter": "Uniformly distributed load", "Symbol": "w", "Value": "20.0 kN/m"},
        {"Parameter": "Section width", "Symbol": "b", "Value": "300.0 mm"},
        {"Parameter": "Section height", "Symbol": "h", "Value": "500.0 mm"},
    ]

    assert {"Parameter": "Section area", "Symbol": "A", "Value": "150000.0 mm^2"} in sheet.final_values_table.rows
    assert {"Parameter": "Second moment of area", "Symbol": "I", "Value": "3125000000.0 mm^4"} in sheet.final_values_table.rows
    assert {
        "Parameter": "Top fibre bending stress",
        "Symbol": r"\sigma_{top}",
        "Value": "-5.0 N/mm^2",
    } in sheet.final_values_table.rows
    assert {
        "Parameter": "Bottom fibre bending stress",
        "Symbol": r"\sigma_{bottom}",
        "Value": "5.0 N/mm^2",
    } in sheet.final_values_table.rows

    drawing_steps = [
        step for step in sheet.steps if getattr(step.component, "kind", "") == "drawing"
    ]
    table_steps = [
        step for step in sheet.steps if getattr(step.component, "kind", "") == "table"
    ]

    assert sheet.steps[0].title == "Input"
    assert sheet.steps[1].title == "Section drawing"
    assert sheet.steps[2].title == "Final values"
    assert len(drawing_steps) == 2
    assert all(Path(step.component.image_path).exists() for step in drawing_steps)
    assert len(table_steps) == 3
    assert len(table_steps[-1].component.rows) == 10

    moment_step = sheet.steps[3]
    assert moment_step.title == "1. Maximum bending moment"
    assert moment_step.metadata == "Moment calculation"
    assert moment_step.component.formula == r"M_{Ed} = \frac{wL^{2}}{8}"
    assert "20.000" in moment_step.component.substitution
    assert "5.000" in moment_step.component.substitution
    assert moment_step.component.result == r"M_{Ed} = 62.500\ \text{kNm}"
