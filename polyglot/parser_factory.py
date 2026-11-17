"""
polyglot/parser_factory.py
━━━━━━━━━━━━━━━━━━━━━━━━━━
Unified Parser Factory supporting Python and C++.
Provides standardized AST parsing, error detection, and node exploration.
Supports Tree-sitter when native binaries are available, with a resilient
pure-Python C++ grammar engine fallback.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List, Optional, Union

try:
    import tree_sitter
    from tree_sitter import Language, Parser, Tree, Node
    import tree_sitter_cpp
    import tree_sitter_python
    _TREE_SITTER_AVAILABLE = True
except (ImportError, Exception):
    _TREE_SITTER_AVAILABLE = False
    tree_sitter = None
    Language = None
    Parser = None
    Tree = None
    Node = None

from polyglot.language_detector import SupportedLanguage, detect_language
from polyglot.cpp_pure_parser import CppPureParser, CppPureTree, CppPureNode


@dataclass
class SyntaxDiagnostic:
    line: int
    column: int
    message: str
    node_type: str


@dataclass
class ParsedAST:
    """Standardized result of a polyglot parse operation."""
    language: SupportedLanguage
    source_bytes: bytes
    tree: Optional[Any]  # Tree-sitter Tree or CppPureTree
    root_node: Optional[Any]  # Tree-sitter root Node or CppPureNode
    is_valid: bool
    diagnostics: List[SyntaxDiagnostic]

    @property
    def has_errors(self) -> bool:
        return not self.is_valid or len(self.diagnostics) > 0


class ParserFactory:
    """
    Thread-safe factory managing parsers for Python and C++.
    Supports native Tree-sitter and zero-dependency CppPureParser fallback.
    """

    _cpp_language: Optional[Any] = None
    _python_language: Optional[Any] = None

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_language(cls, lang: Union[SupportedLanguage, str]) -> Any:
        if not _TREE_SITTER_AVAILABLE:
            raise RuntimeError("tree-sitter libraries are not installed or blocked.")

        norm = lang.value if isinstance(lang, SupportedLanguage) else str(lang).lower()

        if norm in ("cpp", "c++", "c"):
            if cls._cpp_language is None:
                cls._cpp_language = Language(tree_sitter_cpp.language())
            return cls._cpp_language

        if norm in ("python", "py"):
            if cls._python_language is None:
                cls._python_language = Language(tree_sitter_python.language())
            return cls._python_language

        raise ValueError(f"Unsupported language: {lang}")

    @classmethod
    def create_parser(cls, lang: Union[SupportedLanguage, str]) -> Any:
        ts_lang = cls.get_language(lang)
        return Parser(ts_lang)

    @classmethod
    def parse(
        cls, 
        code: Union[str, bytes], 
        language: Optional[Union[SupportedLanguage, str]] = None,
        filename: Optional[str] = None
    ) -> ParsedAST:
        """
        Parse source code into a normalized ParsedAST instance.
        If language is not provided, it is auto-detected via language_detector.
        """
        source_str = code if isinstance(code, str) else code.decode("utf-8", errors="replace")
        source_bytes = code.encode("utf-8") if isinstance(code, str) else code

        if language is None:
            detected = detect_language(source_str, filename=filename)
            lang_enum = detected if detected != SupportedLanguage.UNKNOWN else SupportedLanguage.PYTHON
        elif isinstance(language, str):
            lang_enum = SupportedLanguage(language.lower())
        else:
            lang_enum = language

        # ── C++ Pure-Python Fallback or Native Tree-sitter ──
        if lang_enum == SupportedLanguage.CPP:
            if _TREE_SITTER_AVAILABLE:
                try:
                    parser = cls.create_parser(lang_enum)
                    tree = parser.parse(source_bytes)
                    root = tree.root_node
                    diagnostics: List[SyntaxDiagnostic] = []
                    cls._collect_syntax_errors(root, diagnostics)
                    return ParsedAST(
                        language=lang_enum,
                        source_bytes=source_bytes,
                        tree=tree,
                        root_node=root,
                        is_valid=(not root.has_error and len(diagnostics) == 0),
                        diagnostics=diagnostics
                    )
                except Exception:
                    pass

            # Pure-Python C++ Parser Engine
            pure_parser = CppPureParser()
            pure_tree = pure_parser.parse(source_str)
            diagnostics = cls._diagnose_cpp_syntax(source_str)
            is_valid = len(diagnostics) == 0

            return ParsedAST(
                language=lang_enum,
                source_bytes=source_bytes,
                tree=pure_tree,
                root_node=pure_tree.root_node,
                is_valid=is_valid,
                diagnostics=diagnostics
            )

        # ── Python Parsing ──
        if not _TREE_SITTER_AVAILABLE:
            return ParsedAST(
                language=lang_enum,
                source_bytes=source_bytes,
                tree=None,
                root_node=None,
                is_valid=False,
                diagnostics=[SyntaxDiagnostic(line=1, column=0, message="tree-sitter not installed", node_type="error")]
            )

        try:
            parser = cls.create_parser(lang_enum)
            tree = parser.parse(source_bytes)
            root = tree.root_node
            diagnostics = []
            cls._collect_syntax_errors(root, diagnostics)
            return ParsedAST(
                language=lang_enum,
                source_bytes=source_bytes,
                tree=tree,
                root_node=root,
                is_valid=(not root.has_error and len(diagnostics) == 0),
                diagnostics=diagnostics
            )
        except Exception as e:
            return ParsedAST(
                language=lang_enum,
                source_bytes=source_bytes,
                tree=None,
                root_node=None,
                is_valid=False,
                diagnostics=[SyntaxDiagnostic(line=1, column=0, message=str(e), node_type="error")]
            )

    @classmethod
    def _diagnose_cpp_syntax(cls, code: str) -> List[SyntaxDiagnostic]:
        """Diagnoses C++ missing semicolons, unmatched braces, etc."""
        diagnostics: List[SyntaxDiagnostic] = []
        lines = code.splitlines()

        # Check unmatched braces
        open_braces = 0
        open_parens = 0
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("#"):
                continue

            for char in stripped:
                if char == "{":
                    open_braces += 1
                elif char == "}":
                    open_braces -= 1
                elif char == "(":
                    open_parens += 1
                elif char == ")":
                    open_parens -= 1

            # Semicolon check on statements
            # Exclude preprocessor, control headers, labels, braces, empty lines
            if (
                not stripped.endswith(";")
                and not stripped.endswith("{")
                and not stripped.endswith("}")
                and not stripped.endswith(":")
                and not stripped.endswith(",")
                and not stripped.startswith(("#", "//", "/*", "*", "public", "private", "protected"))
            ):
                # Is it an assignment, declaration, or call?
                if (
                    re.match(r"^(int|char|double|float|bool|auto|size_t|std::\w+)\s+[a-zA-Z_]", stripped)
                    or re.match(r"^[a-zA-Z_]\w*\s*(\+=|-=|\*=|/=|%=|=)", stripped)
                    or re.match(r"^return\b", stripped)
                    or re.search(r"\b(strcpy|strcat|system|printf|cout)\s*\(", stripped)
                ):
                    diagnostics.append(
                        SyntaxDiagnostic(
                            line=idx + 1,
                            column=len(line),
                            message=f"Missing semicolon ';' at line {idx + 1}",
                            node_type=";"
                        )
                    )

        if open_braces != 0:
            diagnostics.append(
                SyntaxDiagnostic(
                    line=len(lines),
                    column=0,
                    message=f"Unmatched curly braces (difference: {open_braces})",
                    node_type="}" if open_braces > 0 else "{"
                )
            )

        return diagnostics

    @classmethod
    def _collect_syntax_errors(cls, node: Any, diagnostics: List[SyntaxDiagnostic]) -> None:
        """Iterative traversal collecting syntax ERROR and MISSING nodes."""
        if not node:
            return

        stack = [node]
        while stack:
            curr = stack.pop()
            if getattr(curr, 'is_error', False) or getattr(curr, 'is_missing', False):
                row = getattr(curr.start_point, 'row', 0)
                col = getattr(curr.start_point, 'column', 0)
                diagnostics.append(
                    SyntaxDiagnostic(
                        line=row + 1,
                        column=col,
                        message=f"Syntax defect '{curr.type}' detected at line {row + 1}",
                        node_type=curr.type
                    )
                )
            for child in getattr(curr, 'children', []):
                if getattr(child, 'has_error', False) or getattr(child, 'is_error', False) or getattr(child, 'is_missing', False):
                    stack.append(child)
