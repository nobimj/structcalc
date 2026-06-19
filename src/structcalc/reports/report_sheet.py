from dataclasses import dataclass, field, is_dataclass
from typing import Any

from structcalc.reports.components.expression import AutoExpression, Expression
from structcalc.reports.components.table import Table
from structcalc.reports.report_step import ReportStep

InputValue = float | tuple[float, str]
InputDefinition = dict[str, str]


@dataclass
class ReportCalculationSheet:
    inputs: dict[str, float] = field(default_factory=dict)
    input_table: Table = field(
        default_factory=lambda: Table(
            title="Inputs",
            columns=["Parameter", "Symbol", "Value"],
        )
    )
    header: dict[str, str] = field(default_factory=dict)
    footer: dict[str, str] = field(default_factory=dict)
    steps: list[ReportStep] = field(default_factory=list)
    final_values: dict[str, float] = field(default_factory=dict)
    final_values_table: Table = field(
        default_factory=lambda: Table(
            title="Final Values",
            columns=["Parameter", "Symbol", "Value"],
        )
    )
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def values(self) -> dict[str, float]:
        return {**self.inputs, **self.final_values}

    def set_input(
        self,
        name: str,
        value: float,
        unit: str = "",
        label: str = "",
        display_symbol: str | None = None,
    ) -> None:
        self.inputs[name] = value

        self.input_table.add_row(
            {
                "Parameter": label or name,
                "Symbol": display_symbol or name,
                "Value": self._value_with_unit(value, unit),
            }
        )

    def set_inputs(self, values: dict[str, InputValue]) -> None:
        for name, value in values.items():
            if isinstance(value, tuple):
                number, unit = value
                self.set_input(name, number, unit)
                continue

            self.set_input(name, value)

    def set_inputs_from_dataclass(
        self,
        inputs: object,
        input_definitions: dict[str, InputDefinition],
    ) -> None:
        if not is_dataclass(inputs):
            raise TypeError("inputs must be a dataclass instance.")

        for field_name, definition in input_definitions.items():
            value = getattr(inputs, field_name)
            symbol = definition.get("symbol", field_name)
            display_symbol = definition.get("display_symbol", symbol)
            label = definition.get("label", field_name)
            unit = definition.get("unit", "")

            self.set_input(
                symbol,
                value,
                unit=unit,
                label=label,
                display_symbol=display_symbol,
            )

    def set_header(self, values: dict[str, str]) -> None:
        self.header.update(values)

    def set_footer(self, values: dict[str, str]) -> None:
        self.footer.update(values)

    def set_metadata(self, values: dict[str, object]) -> None:
        self.metadata.update(values)

    def set_final_value(
        self,
        name: str,
        value: float,
        unit: str = "",
        label: str = "",
        symbol: str = "",
    ) -> None:
        self.final_values[name] = value

        self.final_values_table.add_row(
            {
                "Parameter": label or name,
                "Symbol": symbol or name,
                "Value": self._value_with_unit(value, unit),
            }
        )

    def _value_with_unit(self, value: float, unit: str = "") -> str:
        if unit:
            return f"{value} {unit}"

        return f"{value}"

    def add_component_step(
        self,
        title: str,
        component: Any,
        variable: str | None = None,
        metadata: str | dict[str, object] | None = None,
        text_before: str = "",
        text_after: str = "",
    ) -> float | None:
        return self.add_step(
            variable=variable,
            metadata=metadata,
            title=title,
            text_before=text_before,
            component=component,
            text_after=text_after,
        )

    def add_expression_step(
        self,
        variable: str,
        title: str,
        lhs: str,
        formula: str,
        values: dict[str, float] | None = None,
        unit: str = "",
        precision: int = 3,
        reference: str = "",
        metadata: str | dict[str, object] | None = None,
        text_before: str = "",
        text_after: str = "",
    ) -> float:
        return self.add_step(
            variable=variable,
            metadata=metadata,
            title=title,
            text_before=text_before,
            component=Expression(
                AutoExpression(lhs, formula, **(values or self.values)),
                unit=unit,
                precision=precision,
                reference=reference,
            ),
            text_after=text_after,
        )

    def add_step(
        self,
        variable: str | None,
        metadata: str | dict[str, object] | None,
        title: str,
        text_before: str,
        component: Any,
        text_after: str,
    ) -> float | None:
        self.steps.append(
            ReportStep(
                metadata=metadata,
                title=title,
                text_before=text_before,
                component=component,
                text_after=text_after,
            )
        )

        if variable is None:
            return None

        value = getattr(component, "value", None)

        if value is None:
            raise ValueError(
                f"Step '{title}' cannot store variable '{variable}' because "
                "its component has no value."
            )

        self.set_final_value(
            variable,
            value,
            unit=getattr(component, "unit", ""),
            label=self._title_without_number(title),
            symbol=getattr(getattr(component, "auto_expression", None), "lhs", variable),
        )
        return value

    def _title_without_number(self, title: str) -> str:
        prefix, separator, rest = title.partition(" ")
        prefix = prefix.rstrip(".")

        if separator and all(part.isdigit() for part in prefix.split(".")):
            return rest

        return title
