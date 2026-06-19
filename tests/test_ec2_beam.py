from structcalc.eurocode.ec2_concrete.beams import EC2BeamInputs, required_tension_steel


def test_required_tension_steel_uses_report_expressions():
    inputs = EC2BeamInputs(
        width_mm=300.0,
        effective_depth_mm=500.0,
        fck_mpa=30.0,
        fyk_mpa=500.0,
        moment_ed_knm=62.5,
    )

    sheet = required_tension_steel(inputs)

    assert round(sheet.final_values["f_yd"], 3) == 434.783
    assert sheet.final_values["z"] == 450.0
    assert sheet.final_values["M_Ed_Nmm"] == 62_500_000.0
    assert round(sheet.final_values["A_s"], 3) == 319.444
    assert len(sheet.steps) == 4
    assert sheet.steps[-1].component.result == r"A_s = 319.4\ \text{mm^2}"
