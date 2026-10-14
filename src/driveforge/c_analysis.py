from __future__ import annotations

from dataclasses import dataclass, field
import ast
import re
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True, slots=True)
class CMacro:
    name: str
    value: str | None
    path: str
    line: int
    active: bool


@dataclass(frozen=True, slots=True)
class CStructInitializer:
    type_name: str
    variable: str
    fields: dict[str, str]
    path: str
    line: int
    active: bool = True


@dataclass(slots=True)
class CSourceModel:
    path: str
    macros: list[CMacro] = field(default_factory=list)
    initializers: list[CStructInitializer] = field(default_factory=list)
    active_lines: set[int] = field(default_factory=set)

    def defined(self, name: str) -> bool:
        return any(item.name == name and item.active for item in self.macros)



def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def _eval_condition(expression: str, macros: dict[str, str | None]) -> bool:
    expr = expression.strip()
    expr = re.sub(r"defined\s*\(\s*([A-Za-z_]\w*)\s*\)", lambda m: "1" if m.group(1) in macros else "0", expr)
    expr = re.sub(r"defined\s+([A-Za-z_]\w*)", lambda m: "1" if m.group(1) in macros else "0", expr)
    for name, value in macros.items():
        replacement = value if value not in (None, "") else "1"
        # Only substitute simple object-like macro values. Function-like and
        # token-pasting macros are intentionally treated as unknown.
        if re.fullmatch(r"[0-9A-Fa-fxXuUlL()+\-*/%<>=!&|~\s]+", replacement):
            replacement = re.sub(r"(?<=\d)[uUlL]+\b", "", replacement)
            expr = re.sub(rf"\b{re.escape(name)}\b", replacement, expr)
    expr = expr.replace("&&", " and ").replace("||", " or ")
    expr = re.sub(r"!\s*(?!=)", " not ", expr)
    expr = re.sub(r"(?<=\d)[uUlL]+\b", "", expr)
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return False

    def evaluate(node: ast.AST) -> int | bool:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, bool)):
            return node.value
        if isinstance(node, ast.Name):
            # C preprocessors replace an undefined identifier with zero in an
            # #if expression. This also prevents a source file from injecting
            # arbitrary Python names into the evaluator.
            return 0
        if isinstance(node, ast.BoolOp):
            values = [bool(evaluate(item)) for item in node.values]
            return all(values) if isinstance(node.op, ast.And) else any(values)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.Not, ast.Invert, ast.USub, ast.UAdd)):
            value = evaluate(node.operand)
            if isinstance(node.op, ast.Not):
                return not bool(value)
            if isinstance(node.op, ast.Invert):
                return ~int(value)
            return -int(value) if isinstance(node.op, ast.USub) else int(value)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift)):
            left, right = int(evaluate(node.left)), int(evaluate(node.right))
            if isinstance(node.op, (ast.Div, ast.FloorDiv)):
                return left // right
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Mod): return left % right
            if isinstance(node.op, ast.BitAnd): return left & right
            if isinstance(node.op, ast.BitOr): return left | right
            if isinstance(node.op, ast.BitXor): return left ^ right
            if isinstance(node.op, ast.LShift): return left << right
            return left >> right
        if isinstance(node, ast.Compare):
            left = evaluate(node.left)
            for operator, comparator in zip(node.ops, node.comparators):
                right = evaluate(comparator)
                checks = {
                    ast.Eq: left == right, ast.NotEq: left != right,
                    ast.Lt: left < right, ast.LtE: left <= right,
                    ast.Gt: left > right, ast.GtE: left >= right,
                }
                result = next((value for kind, value in checks.items() if isinstance(operator, kind)), False)
                if not result:
                    return False
                left = right
            return True
        raise ValueError("unsupported preprocessor expression")

    try:
        return bool(evaluate(tree.body))
    except (TypeError, ValueError, ZeroDivisionError, OverflowError):
        return False


def active_preprocessed_lines(
    text: str,
    predefined: dict[str, str | None] | None = None,
    *,
    assume_unknown_ifdef: bool = False,
) -> tuple[list[str], dict[str, str | None]]:
    """Return lines active under a small, deterministic C preprocessor model.

    ``assume_unknown_ifdef`` is useful for inventory discovery when compiler
    defines are unavailable: feature-gated source is retained for candidate
    search, while explicit ``#if 0`` branches remain disabled.
    """
    macros = dict(predefined or {})
    lines = _strip_comments(text).splitlines()
    output = [""] * len(lines)
    stack: list[tuple[bool, bool]] = []  # (parent active, branch already selected)
    active = True
    for index, line in enumerate(lines):
        directive = re.match(r"^\s*#\s*(\w+)(?:\s+(.*?))?\s*$", line)
        if directive:
            command, argument = directive.group(1), (directive.group(2) or "").strip()
            if command in {"if", "ifdef", "ifndef"}:
                parent = active
                condition = (
                    _eval_condition(argument, macros) if command == "if"
                    else (argument in macros or assume_unknown_ifdef) if command == "ifdef"
                    else (argument not in macros or assume_unknown_ifdef)
                )
                stack.append((parent, parent and condition))
                active = parent and condition
            elif command == "elif" and stack:
                parent, selected = stack[-1]
                condition = _eval_condition(argument, macros)
                active = parent and not selected and condition
                stack[-1] = (parent, selected or condition)
            elif command == "else" and stack:
                parent, selected = stack[-1]
                active = parent and not selected
                stack[-1] = (parent, True)
            elif command == "endif" and stack:
                stack.pop()
                active = all(parent and selected for parent, selected in stack) if stack else True
            elif command == "define" and active:
                match = re.match(r"([A-Za-z_]\w*)(?:\s+(.*))?$", argument)
                if match:
                    macros[match.group(1)] = match.group(2) or None
            elif command == "undef" and active:
                macros.pop(argument, None)
            continue
        if active:
            output[index] = line
    return output, macros


class CSourceAnalyzer:
    """Dependency-free semantic scanner with an optional tree-sitter compatible boundary.

    It resolves preprocessor branches before extracting definitions and designated
    initializers. This avoids the common regex failure where disabled vendor code
    becomes a false reference candidate. A future tree-sitter backend can implement
    the same model contract without changing planner consumers.
    """

    def __init__(self, predefined: dict[str, str | None] | None = None) -> None:
        self.predefined = predefined or {}

    def parse(self, path: str | Path, text: str | None = None) -> CSourceModel:
        source = Path(path)
        content = source.read_text(encoding="utf-8", errors="replace") if text is None else text
        active, macros = active_preprocessed_lines(content, self.predefined)
        model = CSourceModel(path=source.as_posix(), active_lines={i + 1 for i, value in enumerate(active) if value})
        original_lines = _strip_comments(content).splitlines()
        for index, line in enumerate(original_lines, 1):
            match = re.match(r"^\s*#\s*define\s+([A-Za-z_]\w*)(?:\s+(.*))?$", line)
            if match:
                model.macros.append(CMacro(match.group(1), match.group(2), source.as_posix(), index, match.group(1) in macros))
        joined = "\n".join(active)
        # Handles static/global arrays and single designated struct instances.
        pattern = re.compile(
            r"(?P<type>[A-Za-z_]\w*(?:\s+[A-Za-z_]\w*)*)\s+(?P<var>[A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*=\s*\{(?P<body>.*?)\}\s*;",
            re.S,
        )
        for match in pattern.finditer(joined):
            fields: dict[str, str] = {}
            for item in re.finditer(r"\.([A-Za-z_]\w*)\s*=\s*([^,}]+)", match.group("body")):
                fields[item.group(1)] = item.group(2).strip()
            if not fields:
                continue
            line = joined[: match.start()].count("\n") + 1
            model.initializers.append(CStructInitializer(match.group("type").strip(), match.group("var"), fields, source.as_posix(), line))
        return model

    def parse_many(self, files: Iterable[str | Path]) -> list[CSourceModel]:
        return [self.parse(path) for path in files]


