from dataclasses import dataclass

from structcalc.reports.report_expression import AutoExpression, Expression
from structcalc.reports.report_sheet import ReportCalculationSheet
from structcalc.reports.report_step import TextBlock


@dataclass
class DemoInputs:
    span: float
    load: float


def test_expression_generates_display_and_value_from_one_formula():
    expression = Expression(
        AutoExpression(r"M_{Ed}", "w*L**2/8", w=20.0, L=5.0),
        unit="kNm",
        precision=3,
    )

    assert expression.value == 62.5
    assert expression.formula == r"M_{Ed} = \frac{wL^{2}}{8}"
    assert "20.000" in expression.substitution
    assert "5.000" in expression.substitution
    assert expression.result == r"M_{Ed} = 62.500\ \text{kNm}"


def test_expression_precision_override():
    expression = Expression(
        AutoExpression(r"A_s", "M/z", M=1000.0, z=3.0),
        unit="mm^2",
        precision=0,
    )

    assert expression.value == 1000.0 / 3.0
    assert expression.result == r"A_s = 333\ \text{mm^2}"


def test_report_calculation_sheet_stores_report_data_and_final_values():
    sheet = ReportCalculationSheet()
    sheet.set_header({"title": "Demo"})
    sheet.set_footer({"checked_by": "Engineer"})
    sheet.set_metadata({"member": "B1"})
    sheet.set_inputs_from_dataclass(
        DemoInputs(span=5.0, load=20.0),
        {
            "span": {"symbol": "L", "label": "Span", "unit": "m"},
            "load": {
                "symbol": "w",
                "label": "Uniformly distributed load",
                "unit": "kN/m",
            },
        },
    )

    med = sheet.add_step(
        variable="M_Ed",
        metadata="Moment",
        title="Maximum bending moment",
        text_before="",
        component=Expression(
            AutoExpression(r"M_{Ed}", "w*L**2/8", w=20.0, L=5.0),
            unit="kNm",
            precision=3,
        ),
        text_after="",
    )

    sheet.add_step(
        variable=None,
        metadata="Note",
        title="Design note",
        text_before="",
        component=TextBlock("Use simply supported beam formula."),
        text_after="",
    )

    assert med == 62.5
    assert sheet.inputs["w"] == 20.0
    assert sheet.input_table.rows == [
        {"Parameter": "Span", "Symbol": "L", "Value": "5.0 m"},
        {"Parameter": "Uniformly distributed load", "Symbol": "w", "Value": "20.0 kN/m"},
    ]
    assert sheet.header["title"] == "Demo"
    assert sheet.footer["checked_by"] == "Engineer"
    assert sheet.metadata["member"] == "B1"
    assert sheet.final_values["M_Ed"] == 62.5
    assert sheet.final_values_table.rows == [
        {"Parameter": "Maximum bending moment", "Symbol": r"M_{Ed}", "Value": "62.5 kNm"}
    ]
    assert len(sheet.steps) == 2
