from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle


def draw_rectangular_rc_section(
    b_mm: float,
    h_mm: float,
    cover_mm: float,
    bar_diameter_mm: float,
    number_of_bars: int,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(5, 7))

    ax.add_patch(
        Rectangle(
            (0, 0),
            b_mm,
            h_mm,
            fill=False,
            linewidth=2,
        )
    )

    y_bar = cover_mm + bar_diameter_mm / 2

    if number_of_bars == 1:
        x_positions = [b_mm / 2]
    else:
        x_start = cover_mm + bar_diameter_mm / 2
        x_end = b_mm - cover_mm - bar_diameter_mm / 2
        spacing = (x_end - x_start) / (number_of_bars - 1)
        x_positions = [x_start + i * spacing for i in range(number_of_bars)]

    for x in x_positions:
        ax.add_patch(
            Circle(
                (x, y_bar),
                bar_diameter_mm / 2,
                fill=True,
            )
        )

    ax.text(b_mm / 2, -40, f"b = {b_mm:.0f} mm", ha="center")
    ax.text(b_mm + 20, h_mm / 2, f"h = {h_mm:.0f} mm", va="center", rotation=90)

    ax.set_aspect("equal")
    ax.set_xlim(-60, b_mm + 80)
    ax.set_ylim(-70, h_mm + 50)
    ax.axis("off")

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return output_path


def draw_rectangular_section(
    b_mm: float,
    h_mm: float,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(5, 6))

    ax.add_patch(
        Rectangle(
            (-b_mm / 2, -h_mm / 2),
            b_mm,
            h_mm,
            fill=False,
            linewidth=2,
        )
    )

    ax.axhline(0, color="0.5", linestyle="--", linewidth=1)
    ax.axvline(0, color="0.85", linewidth=1)

    ax.text(0, -h_mm / 2 - 40, f"b = {b_mm:.0f} mm", ha="center")
    ax.text(
        b_mm / 2 + 30,
        0,
        f"h = {h_mm:.0f} mm",
        va="center",
        rotation=90,
    )
    ax.text(-b_mm / 2, 15, "centroid", ha="left", fontsize=9, color="0.35")

    ax.set_aspect("equal")
    ax.set_xlim(-b_mm / 2 - 80, b_mm / 2 + 100)
    ax.set_ylim(-h_mm / 2 - 80, h_mm / 2 + 80)
    ax.axis("off")

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return output_path


def draw_rectangular_stress_distribution(
    h_mm: float,
    top_stress: float,
    bottom_stress: float,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(5, 6))

    max_abs_stress = max(abs(top_stress), abs(bottom_stress), 1.0)
    scale = 160 / max_abs_stress

    y_top = h_mm / 2
    y_bottom = -h_mm / 2
    x_top = top_stress * scale
    x_bottom = bottom_stress * scale

    ax.plot([0, 0], [y_bottom, y_top], color="black", linewidth=2)
    ax.plot([x_top, x_bottom], [y_top, y_bottom], color="#b22222", linewidth=2)
    ax.fill([0, x_top, x_bottom, 0], [y_top, y_top, y_bottom, y_bottom], color="#f2b8b5", alpha=0.45)

    ax.axhline(0, color="0.5", linestyle="--", linewidth=1)
    ax.text(0, y_top + 25, f"top = {top_stress:.3f} N/mm^2", ha="center")
    ax.text(0, y_bottom - 45, f"bottom = {bottom_stress:.3f} N/mm^2", ha="center")
    ax.text(15, 0, "neutral axis", va="bottom", fontsize=9, color="0.35")

    ax.set_xlim(-190, 190)
    ax.set_ylim(y_bottom - 80, y_top + 80)
    ax.set_xlabel("Stress")
    ax.set_ylabel("Depth")
    ax.axis("off")

    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return output_path
