from dataclasses import dataclass

from structcalc.reports.report_expression import AutoExpression, Expression
from structcalc.reports.report_sheet import ReportCalculationSheet


@dataclass
class EC2BeamInputs:
    width_mm: float
    effective_depth_mm: float
    fck_mpa: float
    fyk_mpa: float
    moment_ed_knm: float


def required_tension_steel(inputs: EC2BeamInputs) -> ReportCalculationSheet:
    """
    Preliminary EC2-style beam tension steel estimate.

    Units:
        M_Ed in kNm
        f_yd in N/mm2
        z in mm
        A_s in mm2
    """

    sheet = ReportCalculationSheet()
    sheet.set_header(
        {
            "title": "EC2 Beam Reinforcement Report",
            "calculation_name": "Required tension reinforcement",
        }
    )
    sheet.set_inputs(
        {
            "b": inputs.width_mm,
            "d": inputs.effective_depth_mm,
            "f_ck": inputs.fck_mpa,
            "f_yk": inputs.fyk_mpa,
            "M_Ed": inputs.moment_ed_knm,
        }
    )

    fyd = sheet.add_step(
        variable="f_yd",
        metadata="Material strength",
        title="Design yield strength of reinforcement",
        text_before="",
        component=Expression(
            AutoExpression(
                r"f_{yd}",
                "f_yk/gamma_s",
                f_yk=inputs.fyk_mpa,
                gamma_s=1.15,
            ),
            unit="N/mm^2",
            precision=2,
            reference="EN 1992-1-1, reinforcement partial factor",
        ),
        text_after="",
    )

    z = sheet.add_step(
        variable="z",
        metadata="Lever arm",
        title="Lever arm",
        text_before="",
        component=Expression(
            AutoExpression("z", "0.9*d", d=inputs.effective_depth_mm),
            unit="mm",
            precision=1,
            reference="Preliminary rectangular beam assumption",
        ),
        text_after="",
    )

    med_nmm = sheet.add_step(
        variable="M_Ed_Nmm",
        metadata="Unit conversion",
        title="Design moment conversion",
        text_before="",
        component=Expression(
            AutoExpression(
                r"M_{Ed,Nmm}",
                "10**6*M_Ed",
                M_Ed=inputs.moment_ed_knm,
            ),
            unit="Nmm",
            precision=0,
            reference="Unit conversion: 1 kNm = 10^6 Nmm",
        ),
        text_after="",
    )

    sheet.add_step(
        variable="A_s",
        metadata="Reinforcement area",
        title="Required tension reinforcement",
        text_before="",
        component=Expression(
            AutoExpression(
                r"A_s",
                "M_Ed_Nmm/(f_yd*z)",
                M_Ed_Nmm=med_nmm,
                f_yd=fyd,
                z=z,
            ),
            unit="mm^2",
            precision=1,
            reference="Basic flexural equilibrium",
        ),
        text_after="",
    )

    return sheet
