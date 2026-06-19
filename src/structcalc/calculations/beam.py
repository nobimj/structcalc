from dataclasses import dataclass

from structcalc.graphics.rc_section import (
    draw_rectangular_section,
    draw_rectangular_stress_distribution,
)
from structcalc.reports.report_expression import AutoExpression, Expression
from structcalc.reports.report_figure import Drawing
from structcalc.reports.report_sheet import ReportCalculationSheet
from structcalc.reports.report_table import Table


@dataclass
class BeamInputs:
    span: float
    udl: float
    width: float
    height: float
    project_name: str = "Demo Project"
    title: str = "Beam Calculation Report"
    element_id: str = ""
    revision: str = ""
    report_date: str = ""


BEAM_INPUTS = {
    "span": {
        "symbol": "L",
        "label": "Span",
        "unit": "m",
    },
    "udl": {
        "symbol": "w",
        "label": "Uniformly distributed load",
        "unit": "kN/m",
    },
    "width": {
        "symbol": "b",
        "label": "Section width",
        "unit": "mm",
    },
    "height": {
        "symbol": "h",
        "label": "Section height",
        "unit": "mm",
    },
}


def simply_supported_beam_udl(inputs: BeamInputs) -> ReportCalculationSheet:
    sheet = ReportCalculationSheet()

    sheet.set_header(
        {
            "title": inputs.title,
            "project_name": inputs.project_name,
            "calculation_name": "Simply Supported Beam v1",
            "element_id": inputs.element_id,
            "revision": inputs.revision,
            "date": inputs.report_date,
        }
    )
    sheet.set_inputs_from_dataclass(inputs, BEAM_INPUTS)

    sheet.add_step(
        variable=None,
        metadata="Input",
        title="Input",
        text_before="",
        component=sheet.input_table,
        text_after="",
    )

    section_path = draw_rectangular_section(
        b_mm=inputs.width,
        h_mm=inputs.height,
        output_path="outputs/figures/rectangular_section.png",
    )

    sheet.add_step(
        variable=None,
        metadata="Section drawing",
        title="Section drawing",
        text_before="",
        component=Drawing(
            title="Rectangular cross-section",
            image_path=str(section_path),
            caption="Gross rectangular beam section.",
            scale=0.55,
        ),
        text_after="",
    )

    sheet.add_step(
        variable=None,
        metadata="Final values",
        title="Final values",
        text_before="",
        component=sheet.final_values_table,
        text_after="",
    )

    sheet.add_step(
        variable="M__Ed",
        metadata="Moment calculation",
        title="1. Maximum bending moment",
        text_before="",
        component=Expression(
            AutoExpression(r"M_{Ed}", "w*L**2/8", **sheet.values),
            unit="kNm",
            precision=3,
            reference="Basic beam formula: simply supported beam under UDL",
        ),
        text_after="",
    )

    sheet.add_step(
        variable="V__Ed",
        metadata="Shear calculation",
        title="2. Maximum shear force",
        text_before="",
        component=Expression(
            AutoExpression(r"V_{Ed}", "w*L/2", **sheet.values),
            unit="kN",
            precision=3,
            reference="Basic beam formula: simply supported beam under UDL",
        ),
        text_after="",
    )

    sheet.add_step(
        variable="A",
        metadata="Section property",
        title="3. Section area",
        text_before="",
        component=Expression(
            AutoExpression("A", "b*h", **sheet.values),
            unit="mm^2",
            precision=0,
            reference="Rectangular section area",
        ),
        text_after="",
    )

    sheet.add_step(
        variable="I",
        metadata="Section property",
        title="4. Second moment of area",
        text_before="",
        component=Expression(
            AutoExpression("I", "b*h**3/12", **sheet.values),
            unit="mm^4",
            precision=0,
            reference="Rectangular section about centroidal strong axis",
        ),
        text_after="",
    )

    sheet.add_step(
        variable="sigma_top",
        metadata="Stress calculation",
        title="5. Top fibre bending stress",
        text_before="",
        component=Expression(
            AutoExpression(
                r"\sigma_{top}",
                "-M__Ed*10**6*(h/2)/I",
                **sheet.values,
            ),
            unit="N/mm^2",
            precision=3,
            reference="Elastic bending stress: sigma = My/I",
        ),
        text_after="",
    )

    sheet.add_step(
        variable="sigma_bottom",
        metadata="Stress calculation",
        title="6. Bottom fibre bending stress",
        text_before="",
        component=Expression(
            AutoExpression(
                r"\sigma_{bottom}",
                "M__Ed*10**6*(h/2)/I",
                **sheet.values,
            ),
            unit="N/mm^2",
            precision=3,
            reference="Elastic bending stress: sigma = My/I",
        ),
        text_after="",
    )

    stress_path = draw_rectangular_stress_distribution(
        h_mm=inputs.height,
        top_stress=sheet.final_values["sigma_top"],
        bottom_stress=sheet.final_values["sigma_bottom"],
        output_path="outputs/figures/stress_distribution.png",
    )

    sheet.add_step(
        variable=None,
        metadata="Stress drawing",
        title="7. Bending stress distribution",
        text_before="",
        component=Drawing(
            title="Bending stress distribution",
            image_path=str(stress_path),
            caption="Linear elastic stress distribution for sagging bending.",
            scale=0.2,
        ),
        text_after="",
    )

    sheet.add_step(
        variable=None,
        metadata="Stress table",
        title="8. Stress distribution through section depth",
        text_before="",
        component=_stress_distribution_table(
            height=inputs.height,
            moment=sheet.final_values["M__Ed"],
            second_moment=sheet.final_values["I"],
        ),
        text_after="",
    )

    return sheet


def _stress_distribution_table(
    height: float,
    moment: float,
    second_moment: float,
) -> Table:
    table = Table(
        title="Stress distribution through section depth",
        columns=["Position", "y from centroid (mm)", "Stress (N/mm^2)"],
    )

    for index in range(10):
        fraction = index / 9
        y = -height / 2 + fraction * height
        stress = moment * 10**6 * y / second_moment

        if index == 0:
            position = "Top fibre"
        elif index == 9:
            position = "Bottom fibre"
        else:
            position = f"Point {index + 1}"

        table.add_row(
            {
                "Position": position,
                "y from centroid (mm)": f"{y:.3f}",
                "Stress (N/mm^2)": f"{stress:.3f}",
            }
        )

    return table
