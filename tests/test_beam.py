from pathlib import Path

from structcalc.calculations.beam import BeamInputs, simply_supported_beam_udl
from structcalc.reports.components.expression import ManualExpression


def test_simply_supported_beam_udl():
    inputs = BeamInputs(span=5.0, udl=20.0, width=300.0, height=500.0, fck=30.0)
    sheet = simply_supported_beam_udl(inputs)

    assert sheet.final_values["M__Ed"] == 62.5
    assert sheet.final_values["f__ck"] == 30.0
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
        {
            "Parameter": "Characteristic compressive strength of concrete",
            "Symbol": r"f_{ck}",
            "Value": "30.0 MPa",
        },
    ]

    assert {"Parameter": "Section area", "Symbol": "A", "Value": "150000.0 mm^2"} in sheet.final_values_table.rows
    assert {
        "Parameter": "Characteristic compressive strength of concrete",
        "Symbol": r"f_{ck}",
        "Value": "30.0 MPa",
    } in sheet.final_values_table.rows
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

    shear_step = sheet.steps[5]
    assert shear_step.title == "2. Maximum shear force"
    assert isinstance(shear_step.component.auto_expression, ManualExpression)
    assert shear_step.component.formula == r"V_{Ed} = \frac{wL}{2}"
    assert shear_step.component.substitution == r"V_{Ed} = \frac{20.000 \times 5.000}{2}"
    assert shear_step.component.result == r"V_{Ed} = 50.000\ \text{kN}"


def test_simply_supported_beam_udl_stores_header_fields():
    inputs = BeamInputs(
        span=5.0,
        udl=20.0,
        width=300.0,
        height=500.0,
        fck=30.0,
        project_name="Project Alpha",
        title="Custom Beam Report",
        element_id="B-101",
        revision="P02",
        report_date="2026-06-19",
    )

    sheet = simply_supported_beam_udl(inputs)

    assert sheet.header["project_name"] == "Project Alpha"
    assert sheet.header["title"] == "Custom Beam Report"
    assert sheet.header["calculation_name"] == "Simply Supported Beam v1"
    assert sheet.header["element_id"] == "B-101"
    assert sheet.header["revision"] == "P02"
    assert sheet.header["date"] == "2026-06-19"
    assert sheet.metadata == {}


def test_simply_supported_beam_udl_uses_blank_date_when_not_passed():
    inputs = BeamInputs(span=5.0, udl=20.0, width=300.0, height=500.0, fck=30.0)

    sheet = simply_supported_beam_udl(inputs)

    assert sheet.header["date"] == ""


def test_generate_html_report_supports_template_selection(tmp_path):
    from structcalc.reports.renderers.html import generate_html_report

    inputs = BeamInputs(
        span=5.0,
        udl=20.0,
        width=300.0,
        height=500.0,
        fck=30.0,
        element_id="B-102",
        revision="C01",
        report_date="2026-06-19",
    )
    sheet = simply_supported_beam_udl(inputs)

    output_path = generate_html_report(
        sheet,
        tmp_path / "beam_report_compact.html",
        template_name="calculation_report_compact.html",
    )

    html = output_path.read_text(encoding="utf-8")
    assert "Element ID" in html
    assert "B-102" in html
    assert "Revision" in html
    assert "C01" in html
    assert "2026-06-19" in html


def test_generate_html_report_supports_a4_print_template(tmp_path):
    from structcalc.reports.renderers.html import generate_html_report

    inputs = BeamInputs(
        span=5.0,
        udl=20.0,
        width=300.0,
        height=500.0,
        fck=30.0,
        project_name="Project Beta",
        title="A4 Beam Report",
        element_id="B-103",
        revision="D01",
        report_date="2026-06-19",
    )
    sheet = simply_supported_beam_udl(inputs)

    output_path = generate_html_report(
        sheet,
        tmp_path / "beam_report_a4.html",
        template_name="calculation_report_print_a4.html",
    )

    html = output_path.read_text(encoding="utf-8")
    assert "Project Beta" in html
    assert "A4 Beam Report" in html
    assert "B-103" in html
    assert "D01" in html
    assert "display: table-header-group" in html


def test_simply_supported_beam_udl_stores_header_fields():
    inputs = BeamInputs(
        span=5.0,
        udl=20.0,
        width=300.0,
        height=500.0,
        fck=30.0,
        project_name="Project Alpha",
        title="Custom Beam Report",
        element_id="B-101",
        revision="P02",
        report_date="2026-06-19",
    )

    sheet = simply_supported_beam_udl(inputs)

    assert sheet.header["project_name"] == "Project Alpha"
    assert sheet.header["title"] == "Custom Beam Report"
    assert sheet.header["calculation_name"] == "Simply Supported Beam v1"
    assert sheet.header["element_id"] == "B-101"
    assert sheet.header["revision"] == "P02"
    assert sheet.header["date"] == "2026-06-19"
    assert sheet.metadata == {}


def test_simply_supported_beam_udl_uses_blank_date_when_not_passed():
    inputs = BeamInputs(span=5.0, udl=20.0, width=300.0, height=500.0, fck=30.0)

    sheet = simply_supported_beam_udl(inputs)

    assert sheet.header["date"] == ""


def test_generate_html_report_supports_template_selection(tmp_path):
    from structcalc.reports.renderers.html import generate_html_report

    inputs = BeamInputs(
        span=5.0,
        udl=20.0,
        width=300.0,
        height=500.0,
        fck=30.0,
        element_id="B-102",
        revision="C01",
        report_date="2026-06-19",
    )
    sheet = simply_supported_beam_udl(inputs)

    output_path = generate_html_report(
        sheet,
        tmp_path / "beam_report_compact.html",
        template_name="calculation_report_compact.html",
    )

    html = output_path.read_text(encoding="utf-8")
    assert "Element ID" in html
    assert "B-102" in html
    assert "Revision" in html
    assert "C01" in html
    assert "2026-06-19" in html


def test_generate_html_report_supports_a4_print_template(tmp_path):
    from structcalc.reports.renderers.html import generate_html_report

    inputs = BeamInputs(
        span=5.0,
        udl=20.0,
        width=300.0,
        height=500.0,
        fck=30.0,
        project_name="Project Beta",
        title="A4 Beam Report",
        element_id="B-103",
        revision="D01",
        report_date="2026-06-19",
    )
    sheet = simply_supported_beam_udl(inputs)

    output_path = generate_html_report(
        sheet,
        tmp_path / "beam_report_a4.html",
        template_name="print/a4.html",
    )

    html = output_path.read_text(encoding="utf-8")
    assert "Project Beta" in html
    assert "A4 Beam Report" in html
    assert "B-103" in html
    assert "D01" in html
    assert "display: table-header-group" in html
