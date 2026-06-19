from dataclasses import dataclass, field


@dataclass
class Table:
    title: str
    columns: list[str]
    rows: list[dict[str, str]] = field(default_factory=list)
    kind: str = field(default="table", init=False)

    def add_row(self, row: dict[str, str]) -> None:
        self.rows.append(row)


ReportTable = Table

__all__ = ["Table", "ReportTable"]
