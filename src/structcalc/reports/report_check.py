from dataclasses import dataclass


@dataclass
class ReportCheck:
    title: str

    demand: float
    capacity: float

    demand_label: str = "Demand"
    capacity_label: str = "Capacity"

    unit: str = ""

    utilisation: float = 0.0

    passed: bool = True

    reference: str | None = None