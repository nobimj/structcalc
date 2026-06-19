from dataclasses import dataclass
from typing import Any


@dataclass
class TextBlock:
    text: str
    style: str = "normal"
    kind: str = "text"


@dataclass
class ReportStep:
    metadata: str | dict[str, object] | None
    title: str
    text_before: str
    component: Any
    text_after: str
