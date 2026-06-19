from structcalc.calculations.beam import BeamInputs, simply_supported_beam_udl
from structcalc.reports.html_report import generate_html_report


inputs = BeamInputs(
    span=5,
    udl=20,
    width=300,
    height=500,
)

sheet = simply_supported_beam_udl(inputs)

generate_html_report(
    sheet,
    output_path="outputs/beam_report.html",
)
