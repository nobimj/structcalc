from dataclasses import dataclass, field

import sympy as sp

from structcalc.common.settings import DEFAULT_PRECISION
from structcalc.reports.report_auto_expression import (
    AutoExpression,
    OrderedLatexPrinter,
)


@dataclass
class Expression:
    auto_expression: AutoExpression
    unit: str = ""
    precision: int = DEFAULT_PRECISION
    reference: str = ""
    kind: str = field(default="expression", init=False)

    value: float = field(init=False)
    formula: str = field(init=False)
    substitution: str = field(init=False)
    result: str = field(init=False)

    def __post_init__(self) -> None:
        self.value = float(self.auto_expression.result())
        self.formula = rf"{self.auto_expression.lhs} = {self.auto_expression.latex(False)}"
        self.substitution = (
            rf"{self.auto_expression.lhs} = {self._substitution_latex()}"
        )
        self.result = (
            rf"{self.auto_expression.lhs} = {self._format_number(self.value)}"
            f"{self._unit_latex()}"
        )

    def _substitution_latex(self) -> str:
        # Use Symbols for formatted numbers so LaTeX keeps trailing zeros.
        substitutions = {
            symbol: sp.Symbol(self._format_number(value))
            for symbol, value in self.auto_expression.calc_subs.items()
        }

        printer = OrderedLatexPrinter(
            self.auto_expression.meta,
            substitutions=substitutions,
            mul_symbol="",
        )

        return printer.doprint(self.auto_expression.sympy)

    def _format_number(self, value: float) -> str:
        return f"{float(value):.{self.precision}f}"

    def _unit_latex(self) -> str:
        if not self.unit:
            return ""

        return rf"\ \text{{{self.unit}}}"

    @property
    def formula_latex(self) -> str:
        return self.formula

    @property
    def substitution_latex(self) -> str:
        return self.substitution

    @property
    def result_latex(self) -> str:
        return self.result


ReportExpression = Expression

__all__ = ["AutoExpression", "Expression", "ReportExpression"]
