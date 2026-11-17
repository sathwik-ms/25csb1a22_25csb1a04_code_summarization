"""
polyglot/cpp_pure_parser.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pure-Python AST Parser and Grammar Analyzer for C++ source code.
Acts as a zero-dependency fallback engine when native Tree-sitter binaries
are unavailable or blocked by system security policies.

Provides:
  - CppPureNode: Compatible with Tree-sitter Node interface (.type, .text, .children, .start_point).
  - CppPureTree: Root container with root_node and error flags.
  - CppPureParser: Tokenizes and parses C++ syntax into a hierarchical AST,
    including functions, classes, preprocessor includes, control branches,
    declarations, expressions, calls, and returns.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional, Tuple


class CppPoint:
    __slots__ = ("row", "column")

    def __init__(self, row: int, column: int) -> None:
        self.row = row
        self.column = column

    def __repr__(self) -> str:
        return f"Point(row={self.row}, column={self.column})"


class CppPureNode:
    """
    Standardized C++ AST node mimicking Tree-sitter Node interface.
    Compatible with cpp_pdg_extractor, cpp_security_auditor, green_computing, and agent_controller.
    """

    __slots__ = (
        "type",
        "text",
        "children",
        "start_point",
        "end_point",
        "field_name",
        "is_error",
        "is_missing",
        "has_error",
    )

    def __init__(
        self,
        ntype: str,
        text: bytes | str,
        children: Optional[List[CppPureNode]] = None,
        start_row: int = 0,
        start_col: int = 0,
        end_row: int = 0,
        end_col: int = 0,
        field_name: str = "",
        is_error: bool = False,
        is_missing: bool = False,
    ) -> None:
        self.type = ntype
        if isinstance(text, bytes):
            self.text = text
        else:
            self.text = text.encode("utf-8", errors="replace")
        self.children = children or []
        self.start_point = CppPoint(start_row, start_col)
        self.end_point = CppPoint(end_row, end_col)
        self.field_name = field_name
        self.is_error = is_error
        self.is_missing = is_missing
        self.has_error = is_error or is_missing or any(c.has_error for c in self.children)

    @property
    def child_count(self) -> int:
        return len(self.children)

    def child_by_field_name(self, name: str) -> Optional[CppPureNode]:
        for c in self.children:
            if c.field_name == name:
                return c
        return None

    def __repr__(self) -> str:
        return f"<{self.type} '{self.text.decode('utf-8', errors='ignore')[:30]}'>"


class CppPureTree:
    """Tree-sitter compatible Tree container."""

    def __init__(self, root_node: CppPureNode) -> None:
        self.root_node = root_node

    @property
    def has_error(self) -> bool:
        return self.root_node.has_error


class CppPureParser:
    """
    Pure-Python parser producing structured C++ ASTs.
    """

    def parse(self, code_bytes_or_str: bytes | str) -> CppPureTree:
        if isinstance(code_bytes_or_str, bytes):
            code_str = code_bytes_or_str.decode("utf-8", errors="replace")
        else:
            code_str = str(code_bytes_or_str)

        lines = code_str.splitlines()
        root_children: List[CppPureNode] = []

        i = 0
        n = len(lines)

        while i < n:
            raw_line = lines[i]
            line = raw_line.strip()
            row = i

            # 1. Blank lines or pure comments
            if not line:
                i += 1
                continue
            if line.startswith("//") or line.startswith("/*"):
                comment_node = CppPureNode("comment", raw_line, start_row=row, end_row=row)
                root_children.append(comment_node)
                i += 1
                continue

            # 2. Preprocessor directives (#include, #define)
            if line.startswith("#"):
                inc_match = re.match(r"#include\s*(<[^>]+>|\"[^\"]+\")", line)
                ptype = "preproc_include" if inc_match else "preproc_directive"
                node = CppPureNode(ptype, raw_line, start_row=row, end_row=row)
                root_children.append(node)
                i += 1
                continue

            # 3. Using / namespace
            if line.startswith("using ") or line.startswith("namespace "):
                node = CppPureNode("using_declaration", raw_line, start_row=row, end_row=row)
                root_children.append(node)
                i += 1
                continue

            # 4. Function definitions (e.g. void process(const char* s) { ... }, int main() { ... })
            func_sig_match = re.match(
                r"^([\w:*&<>\s]+?)\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*(\{)?",
                line
            )
            # Ensure it's not a control statement like if, for, while, switch
            if func_sig_match and func_sig_match.group(2) not in ("if", "for", "while", "switch", "catch"):
                ret_type = func_sig_match.group(1).strip()
                func_name = func_sig_match.group(2).strip()
                params_str = func_sig_match.group(3).strip()
                has_open_brace = bool(func_sig_match.group(4))

                # Collect function body between { and matching }
                body_lines: List[str] = []
                body_start_row = row
                brace_count = 0
                started = False

                j = i
                while j < n:
                    cur_line = lines[j]
                    for char in cur_line:
                        if char == "{":
                            brace_count += 1
                            started = True
                        elif char == "}":
                            brace_count -= 1
                    body_lines.append(cur_line)
                    if started and brace_count <= 0:
                        j += 1
                        break
                    j += 1

                func_full_text = "\n".join(body_lines)
                end_row = j - 1

                # Build function children
                name_node = CppPureNode("identifier", func_name, start_row=row, field_name="name")
                
                # Parameters
                param_nodes: List[CppPureNode] = []
                if params_str:
                    for p in params_str.split(","):
                        p = p.strip()
                        if p:
                            p_id_match = re.search(r"([a-zA-Z_]\w*)$", p)
                            p_id = p_id_match.group(1) if p_id_match else p
                            param_nodes.append(CppPureNode("parameter_declaration", p, [
                                CppPureNode("identifier", p_id, field_name="name")
                            ]))

                param_list_node = CppPureNode("parameter_list", f"({params_str})", param_nodes)
                declarator_node = CppPureNode("function_declarator", f"{func_name}({params_str})", [name_node, param_list_node])

                # Parse body statements
                body_statements = self._parse_compound_statement(body_lines, body_start_row)
                compound_node = CppPureNode("compound_statement", func_full_text, body_statements, start_row=body_start_row, end_row=end_row, field_name="body")

                func_node = CppPureNode(
                    "function_definition",
                    func_full_text,
                    [declarator_node, compound_node],
                    start_row=row,
                    end_row=end_row
                )
                root_children.append(func_node)
                i = j
                continue

            # 5. Standalone statements or declarations at root level
            stmt_node = self._parse_single_statement(raw_line, row)
            root_children.append(stmt_node)
            i += 1

        root = CppPureNode("translation_unit", code_str, root_children, start_row=0, end_row=max(0, n - 1))
        return CppPureTree(root)

    def _parse_compound_statement(self, lines: List[str], start_row: int) -> List[CppPureNode]:
        """Parses statements inside a { ... } body into structured nodes."""
        statements: List[CppPureNode] = []
        i = 0
        n = len(lines)

        while i < n:
            raw = lines[i]
            line = raw.strip()
            row = start_row + i

            if not line or line in ("{", "}"):
                i += 1
                continue
            if line.startswith("//"):
                i += 1
                continue

            # Strip leading { or trailing }
            clean_stmt = line.lstrip("{").rstrip("}").strip()
            if not clean_stmt:
                i += 1
                continue

            # Control: If Statement
            if clean_stmt.startswith("if ") or clean_stmt.startswith("if("):
                if_node, lines_consumed = self._parse_if_block(lines, i, start_row)
                statements.append(if_node)
                i += lines_consumed
                continue

            # Control: For Statement / For-Range Loop
            if clean_stmt.startswith("for ") or clean_stmt.startswith("for("):
                for_node, lines_consumed = self._parse_loop_block("for_statement", lines, i, start_row)
                statements.append(for_node)
                i += lines_consumed
                continue

            # Control: While Statement
            if clean_stmt.startswith("while ") or clean_stmt.startswith("while("):
                while_node, lines_consumed = self._parse_loop_block("while_statement", lines, i, start_row)
                statements.append(while_node)
                i += lines_consumed
                continue

            # Return Statement
            if clean_stmt.startswith("return"):
                ret_node = CppPureNode("return_statement", clean_stmt, start_row=row, end_row=row)
                # extract returned identifier
                ret_val = re.sub(r"^return\s*", "", clean_stmt).rstrip(";")
                if ret_val:
                    for id_m in re.finditer(r"\b[a-zA-Z_]\w*\b", ret_val):
                        ret_node.children.append(CppPureNode("identifier", id_m.group(0), start_row=row))
                statements.append(ret_node)
                i += 1
                continue

            # Generic single statement (call, assign, declaration)
            stmt_node = self._parse_single_statement(clean_stmt, row)
            statements.append(stmt_node)
            i += 1

        return statements

    def _parse_if_block(self, lines: List[str], line_idx: int, base_row: int) -> Tuple[CppPureNode, int]:
        raw_header = lines[line_idx].strip()
        row = base_row + line_idx
        cond_match = re.search(r"if\s*\((.*?)\)", raw_header)
        cond_text = cond_match.group(1) if cond_match else "condition"

        cond_node = CppPureNode("condition_clause", f"({cond_text})", start_row=row)
        for id_m in re.finditer(r"\b[a-zA-Z_]\w*\b", cond_text):
            cond_node.children.append(CppPureNode("identifier", id_m.group(0), start_row=row))

        # Collect nested lines
        block_lines, count = self._collect_block(lines, line_idx)
        inner_stmts = self._parse_compound_statement(block_lines[1:] if len(block_lines) > 1 else block_lines, row)
        body_node = CppPureNode("compound_statement", "\n".join(block_lines), inner_stmts, start_row=row, end_row=row + count - 1, field_name="consequence")

        if_node = CppPureNode("if_statement", "\n".join(block_lines), [cond_node, body_node], start_row=row, end_row=row + count - 1)
        return if_node, max(1, count)

    def _parse_loop_block(self, loop_type: str, lines: List[str], line_idx: int, base_row: int) -> Tuple[CppPureNode, int]:
        raw_header = lines[line_idx].strip()
        row = base_row + line_idx
        header_match = re.search(r"(?:for|while)\s*\((.*?)\)", raw_header)
        header_text = header_match.group(1) if header_match else "header"

        cond_node = CppPureNode("condition_clause", f"({header_text})", start_row=row)
        for id_m in re.finditer(r"\b[a-zA-Z_]\w*\b", header_text):
            cond_node.children.append(CppPureNode("identifier", id_m.group(0), start_row=row))

        block_lines, count = self._collect_block(lines, line_idx)
        inner_stmts = self._parse_compound_statement(block_lines[1:] if len(block_lines) > 1 else block_lines, row)
        body_node = CppPureNode("compound_statement", "\n".join(block_lines), inner_stmts, start_row=row, end_row=row + count - 1, field_name="body")

        loop_node = CppPureNode(loop_type, "\n".join(block_lines), [cond_node, body_node], start_row=row, end_row=row + count - 1)
        return loop_node, max(1, count)

    def _collect_block(self, lines: List[str], start_idx: int) -> Tuple[List[str], int]:
        """Collects statements belonging to a block starting at start_idx."""
        res = []
        brace_count = 0
        started = False
        j = start_idx
        n = len(lines)

        while j < n:
            l = lines[j]
            res.append(l)
            for c in l:
                if c == "{":
                    brace_count += 1
                    started = True
                elif c == "}":
                    brace_count -= 1
            if started and brace_count <= 0:
                return res, (j - start_idx + 1)
            # If no brace was used on single line:
            if not started and ";" in l:
                return res, (j - start_idx + 1)
            j += 1

        return res, max(1, len(res))

    def _parse_single_statement(self, stmt: str, row: int) -> CppPureNode:
        clean = stmt.strip()

        # Variable Declaration (e.g. char buffer[16];, int total = 0;)
        decl_match = re.match(r"^(const\s+)?(char|int|float|double|size_t|bool|std::string|std::vector<[^>]+>|auto)\s+([a-zA-Z_]\w*)(?:\[(\d*)\])?(?:\s*=\s*(.*))?;?", clean)
        if decl_match:
            var_name = decl_match.group(3)
            init_val = decl_match.group(5) or ""
            id_node = CppPureNode("identifier", var_name, start_row=row, field_name="declarator")
            init_node = CppPureNode("init_declarator", clean, [id_node], start_row=row)
            if init_val:
                for id_m in re.finditer(r"\b[a-zA-Z_]\w*\b", init_val):
                    init_node.children.append(CppPureNode("identifier", id_m.group(0), start_row=row))
            return CppPureNode("declaration", clean, [init_node], start_row=row, end_row=row)

        # Call expressions: func_name(arg1, arg2...)
        call_match = re.search(r"\b([a-zA-Z_]\w*(?:::[\w]+)?)\s*\(([^;]*)\)", clean)
        if call_match and not clean.startswith(("if", "for", "while", "switch")):
            func_name = call_match.group(1)
            args_str = call_match.group(2)
            func_node = CppPureNode("identifier", func_name, start_row=row, field_name="function")
            arg_nodes = []
            for arg in args_str.split(","):
                arg = arg.strip()
                if arg:
                    for id_m in re.finditer(r"\b[a-zA-Z_]\w*\b", arg):
                        arg_nodes.append(CppPureNode("identifier", id_m.group(0), start_row=row))

            arg_list = CppPureNode("argument_list", f"({args_str})", arg_nodes, start_row=row)
            call_node = CppPureNode("call_expression", clean, [func_node, arg_list], start_row=row, end_row=row)
            return CppPureNode("expression_statement", clean, [call_node], start_row=row, end_row=row)

        # Assignment expression (e.g. total += i * factor;)
        assign_match = re.match(r"^([a-zA-Z_]\w*)\s*(\+=|-=|\*=|/=|%=|=)\s*(.*);?", clean)
        if assign_match:
            lhs = assign_match.group(1)
            rhs = assign_match.group(3)
            lhs_node = CppPureNode("identifier", lhs, start_row=row, field_name="left")
            rhs_node = CppPureNode("identifier", rhs, start_row=row, field_name="right")
            for id_m in re.finditer(r"\b[a-zA-Z_]\w*\b", rhs):
                rhs_node.children.append(CppPureNode("identifier", id_m.group(0), start_row=row))
            assign_node = CppPureNode("assignment_expression", clean, [lhs_node, rhs_node], start_row=row)
            return CppPureNode("expression_statement", clean, [assign_node], start_row=row, end_row=row)

        # Default fallback expression statement
        return CppPureNode("expression_statement", clean, start_row=row, end_row=row)
