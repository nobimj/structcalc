import ast
from dataclasses import dataclass
from typing import Any

import sympy as sp
from sympy.printing.latex import LatexPrinter


# ==========================================================
# Metadata
# ==========================================================

@dataclass(frozen=True)
class Meta:
    kind: str
    children: tuple[Any, ...]
    func: Any = None
    source: str = ""


# ==========================================================
# Matrix helpers
# ==========================================================

def is_matrix_value(v):
    return isinstance(v, sp.MatrixBase) or (
        isinstance(v, (list, tuple))
        and len(v) > 0
        and all(isinstance(row, (list, tuple)) for row in v)
    )


def to_matrix(v):
    if isinstance(v, sp.MatrixBase):
        return sp.ImmutableDenseMatrix(v)

    return sp.ImmutableDenseMatrix(v)


def shape_of(v):
    return to_matrix(v).shape


def exact_value(v):
    if is_matrix_value(v):
        return to_matrix(v)

    if isinstance(v, float):
        return sp.Rational(str(v))

    return sp.sympify(v)


def display_value(v):
    if is_matrix_value(v):
        return to_matrix(v)

    return sp.sympify(str(v))


def clean_number(expr, sig=12):
    n = sp.N(expr, sig)

    try:
        f = float(n)

        if abs(f - round(f)) < 1e-10:
            return str(int(round(f)))

        return f"{f:.{sig}g}"

    except Exception:
        return sp.latex(n)


# ==========================================================
# Ordered SymPy Builder
# ==========================================================

class OrderedSympyBuilder(ast.NodeVisitor):
    def __init__(self, source: str, values=None, namespace=None):
        self.source = source
        self.values = values or {}
        self.namespace = dict(namespace or {})
        self.meta = {}

        self.matrix_shapes = {
            name: shape_of(value)
            for name, value in self.values.items()
            if is_matrix_value(value)
        }

    def remember(self, expr, meta):
        self.meta[id(expr)] = meta
        return expr

    def build(self):
        tree = ast.parse(self.source, mode="eval")
        return self.visit(tree.body)

    def src(self, node):
        return ast.get_source_segment(self.source, node) or ""

    def is_matrix_expr(self, expr):
        return (
            getattr(expr, "is_Matrix", False)
            or isinstance(expr, sp.MatrixExpr)
            or isinstance(expr, sp.MatrixBase)
        )

    def visit_Name(self, node):
        name = node.id

        constants = {
            "pi": sp.pi,
            "E": sp.E,
            "oo": sp.oo,
            "True": sp.true,
            "False": sp.false,
        }

        if name in self.matrix_shapes:
            rows, cols = self.matrix_shapes[name]
            return sp.MatrixSymbol(name, rows, cols)

        if name in self.namespace:
            return self.namespace[name]

        if name in constants:
            return constants[name]

        return sp.Symbol(name)

    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            return sp.true if node.value else sp.false

        if isinstance(node.value, int):
            return sp.Integer(node.value)

        if isinstance(node.value, float):
            return sp.Float(str(node.value))

        raise ValueError(f"Unsupported constant: {node.value!r}")

    def visit_Tuple(self, node):
        return tuple(self.visit(e) for e in node.elts)

    def visit_UnaryOp(self, node):
        x = self.visit(node.operand)

        if isinstance(node.op, ast.USub):
            expr = sp.Mul(sp.Integer(-1), x, evaluate=False)
            return self.remember(expr, Meta("neg", (x,), source=self.src(node)))

        if isinstance(node.op, ast.UAdd):
            return x

        raise ValueError(f"Unsupported unary operator: {ast.dump(node.op)}")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        left_matrix = self.is_matrix_expr(left)
        right_matrix = self.is_matrix_expr(right)
        matrix_operation = left_matrix or right_matrix

        if isinstance(node.op, ast.Add):
            if matrix_operation:
                expr = sp.MatAdd(left, right, evaluate=False)
            else:
                expr = sp.Add(left, right, evaluate=False)
            kind = "add"

        elif isinstance(node.op, ast.Sub):
            if matrix_operation:
                expr = sp.MatAdd(left, -right, evaluate=False)
            else:
                expr = sp.Add(
                    left,
                    sp.Mul(-1, right, evaluate=False),
                    evaluate=False,
                )
            kind = "sub"

        elif isinstance(node.op, ast.Mult):
            if matrix_operation:
                expr = sp.MatMul(left, right, evaluate=False)
            else:
                expr = sp.Mul(left, right, evaluate=False)
            kind = "mul"

        elif isinstance(node.op, ast.Div):
            expr = sp.Mul(
                left,
                sp.Pow(right, -1, evaluate=False),
                evaluate=False,
            )
            kind = "div"

        elif isinstance(node.op, ast.Pow):
            expr = sp.Pow(left, right, evaluate=False)
            kind = "pow"

        else:
            raise ValueError(f"Unsupported operator: {ast.dump(node.op)}")

        return self.remember(
            expr,
            Meta(kind, (left, right), source=self.src(node)),
        )

    def visit_Call(self, node):
        func = self.resolve_function(node.func)
        args = tuple(self.visit(a) for a in node.args)

        try:
            expr = func(*args, evaluate=False)
        except TypeError:
            expr = func(*args)

        return self.remember(
            expr,
            Meta("call", args, func=func, source=self.src(node)),
        )

    def resolve_function(self, node):
        if isinstance(node, ast.Name):
            name = node.id

            if name in self.namespace:
                return self.namespace[name]

            obj = getattr(sp, name, None)

            if callable(obj):
                return obj

            return sp.Function(name)

        if isinstance(node, ast.Attribute):
            name = node.attr
            obj = getattr(sp, name, None)

            if callable(obj):
                return obj

        raise ValueError(f"Unsupported function reference: {ast.dump(node)}")

    def generic_visit(self, node):
        raise ValueError(f"Unsupported syntax: {ast.dump(node)}")


# ==========================================================
# Ordered LaTeX Printer
# ==========================================================

class OrderedLatexPrinter(LatexPrinter):
    def __init__(self, meta=None, substitutions=None, **settings):
        self.meta = meta or {}
        self.substitutions = substitutions or {}
        self._plain_printer = LatexPrinter(settings)
        super().__init__(settings)

    def m(self, expr):
        return self.meta.get(id(expr))

    def _print(self, expr, **kwargs):
        meta = self.m(expr)

        if meta and meta.kind == "call" and getattr(expr, "is_Function", False):
            rendered = self._try_print_function_call(expr, meta)

            if rendered is not None:
                return rendered

        return super()._print(expr, **kwargs)

    def _try_print_function_call(self, expr, meta):
        if any(isinstance(a, tuple) for a in meta.children):
            return None

        placeholders = [
            sp.Symbol(f"HCARG{i}")
            for i in range(len(meta.children))
        ]

        try:
            shell_expr = meta.func(*placeholders, evaluate=False)
        except TypeError:
            try:
                shell_expr = meta.func(*placeholders)
            except Exception:
                return None
        except Exception:
            return None

        shell = self._plain_printer.doprint(shell_expr)

        for placeholder, actual in zip(placeholders, meta.children):
            shell = shell.replace(
                self._plain_printer.doprint(placeholder),
                self._print_arg(actual),
            )

        return shell

    def _print_arg(self, arg):
        if isinstance(arg, tuple):
            return (
                r"\left("
                + ", ".join(self._print_arg(a) for a in arg)
                + r"\right)"
            )

        return self._print(arg)
    def name_to_latex(self, name):
        greek = {
            "sigma": r"\sigma",
            "phi": r"\phi",
            "gamma": r"\gamma",
            "theta": r"\theta",
            "alpha": r"\alpha",
            "beta": r"\beta",
            "delta": r"\delta",
            "epsilon": r"\epsilon",
        }

        # Superscript first: M__Ed___max -> M__Ed + max
        if "___" in name:
            name, sup = name.split("___", 1)
        else:
            sup = None

        # Subscript second: M__Ed -> M + Ed
        if "__" in name:
            base, sub = name.split("__", 1)
        else:
            base, sub = name, None

        base = greek.get(base, base)

        out = base

        if sub:
            out += rf"_{{{sub}}}"

        if sup:
            out += rf"^{{{sup}}}"

        return out  


    def _print_Symbol(self, expr, **kwargs):
        if expr in self.substitutions:
            return self._print(self.substitutions[expr])

        return self.name_to_latex(str(expr))

    def _print_MatrixSymbol(self, expr, **kwargs):
        if expr in self.substitutions:
            return self._print(self.substitutions[expr])

        return self.name_to_latex(str(expr))

    def _paren(self, s):
        return r"\left(" + s + r"\right)"

    def _symbol_is_substituted(self, expr):
        return (
            isinstance(expr, (sp.Symbol, sp.MatrixSymbol))
            and expr in self.substitutions
        )

    def _child(self, expr, parent=None, side=None):
        s = self._print_arg(expr)

        if self._symbol_is_substituted(expr):
            if parent == "mul" and side != "first":
                return self._paren(s)

            if parent == "pow" and side == "base":
                return self._paren(s)

        if isinstance(expr, (sp.Add, sp.MatAdd)) and parent in {"mul", "pow", "sub"}:
            return self._paren(s)

        return s

    def _print_Add(self, expr, order=None):
        meta = self.m(expr)

        if meta and meta.kind in {"add", "sub"}:
            left, right = meta.children
            op = " + " if meta.kind == "add" else " - "

            return (
                self._child(left, meta.kind, "left")
                + op
                + self._child(right, meta.kind, "right")
            )

        return super()._print_Add(expr, order=order)

    def _print_MatAdd(self, expr):
        meta = self.m(expr)

        if meta and meta.kind in {"add", "sub"}:
            left, right = meta.children
            op = " + " if meta.kind == "add" else " - "

            return (
                self._child(left, meta.kind, "left")
                + op
                + self._child(right, meta.kind, "right")
            )

        return super()._print_MatAdd(expr)

    def _print_Mul(self, expr):
        meta = self.m(expr)

        if meta and meta.kind == "mul":
            left, right = meta.children

            return self._mul_join(
                self._child(left, "mul", "first"),
                self._child(right, "mul", "right"),
            )

        if meta and meta.kind == "div":
            left, right = meta.children

            return (
                r"\frac{"
                + self._print_arg(left)
                + "}{"
                + self._print_arg(right)
                + "}"
            )

        if meta and meta.kind == "neg":
            (child,) = meta.children
            return "-" + self._child(child, "neg", "right")

        return super()._print_Mul(expr)


    def _mul_join(self, left, right):
        # In substitution step, show explicit multiplication
        if self.substitutions:
            return left + r" \times " + right

        # In symbolic step, keep compact engineering notation
        if left.endswith(("i", "}", ")")):
            return left + r"\," + right

        return left + right
    def _print_MatMul(self, expr):
        meta = self.m(expr)

        if meta and meta.kind == "mul":
            left, right = meta.children
            return (
                self._child(left, "mul", "first")
                + r"\,"
                + self._child(right, "mul", "right")
            )

        return super()._print_MatMul(expr)

    def _print_Pow(self, expr):
        meta = self.m(expr)

        if meta and meta.kind == "pow":
            base, exponent = meta.children

            return (
                self._child(base, "pow", "base")
                + "^{"
                + self._print_arg(exponent)
                + "}"
            )

        return super()._print_Pow(expr)


# ==========================================================
# Main Calculation Object
# ==========================================================

class AutoExpression:
    def __init__(self, lhs, expression, namespace=None, **values):
        self.lhs = lhs
        self.source = expression

        builder = OrderedSympyBuilder(
            expression,
            values=values,
            namespace=namespace,
        )

        self.sympy = builder.build()
        self.meta = builder.meta

        self.calc_subs = {}
        self.display_subs = {}

        for name, value in values.items():
            if is_matrix_value(value):
                rows, cols = shape_of(value)
                key = sp.MatrixSymbol(name, rows, cols)
            else:
                key = sp.Symbol(name)

            self.calc_subs[key] = exact_value(value)
            self.display_subs[key] = display_value(value)

    def latex(self, substituted=False):
        printer = OrderedLatexPrinter(
            self.meta,
            substitutions=self.display_subs if substituted else {},
            mul_symbol="",
        )

        return printer.doprint(self.sympy)

    def result(self):
        return self.sympy.subs(self.calc_subs).doit()

    def report(self):
        return "\n".join(
            [
                rf"{self.lhs} = {self.latex(False)}",
                "=",
                rf"{self.lhs} = {self.latex(True)}",
                "=",
                rf"{self.lhs} = {sp.latex(self.result())}",
            ]
        )

    def report_latex(self):
        return rf"""
        \begin{{aligned}}
        {self.lhs} &= {self.latex(False)} \\[6pt]
        &= {self.latex(True)} \\[6pt]
        &= {sp.latex(self.result())}
        \end{{aligned}}
        """