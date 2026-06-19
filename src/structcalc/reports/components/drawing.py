from dataclasses import dataclass, field


@dataclass
class Drawing:
    title: str
    image_path: str
    caption: str = ""
    scale: float = 1.0
    kind: str = field(default="drawing", init=False)

    @property
    def width_percent(self) -> float:
        return self.scale * 100


ReportFigure = Drawing

__all__ = ["Drawing", "ReportFigure"]
