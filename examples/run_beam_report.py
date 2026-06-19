from structcalc.calculations.beam import BeamInputs, simply_supported_beam_udl
from structcalc.reports.html_report import generate_html_report


inputs = BeamInputs(
    span=5,
    udl=20,
    width=300,
    height=500,
    project_name="Demo Project",
    title="Beam Calculation Report",
    element_id="B1",
    revision="R0",
    report_date="2026-06-19",
    fck=30,
)

sheet = simply_supported_beam_udl(inputs)

generate_html_report(
    sheet,
    output_path="outputs/beam_report.html",
    template_name="print/a4.html",
)
