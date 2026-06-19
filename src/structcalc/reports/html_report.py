from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from structcalc.reports.report_sheet import ReportCalculationSheet


def _prepare_drawing_paths(sheet: ReportCalculationSheet, output_dir: Path) -> None:
    for step in sheet.steps:
        component = step.component

        if getattr(component, "kind", "") != "drawing":
            continue

        image_path = Path(component.image_path)

        try:
            display_path = image_path.resolve().relative_to(output_dir.resolve())
        except ValueError:
            display_path = image_path

        component.image_path = display_path.as_posix()


def generate_html_report(
    sheet: ReportCalculationSheet,
    output_path: str | Path,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _prepare_drawing_paths(sheet, output_path.parent)

    template_dir = Path(__file__).parent / "templates"

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("calculation_report.html")

    html = template.render(
        title=sheet.header.get("title", "Calculation Report"),
        project_name=sheet.header.get("project_name", ""),
        calculation_name=sheet.header.get("calculation_name", ""),
        footer=sheet.footer,
        metadata=sheet.metadata,
        steps=sheet.steps,
    )

    output_path.write_text(html, encoding="utf-8")

    return output_path
