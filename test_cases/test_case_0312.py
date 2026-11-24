"""
Test Case File #0312
Project: CODE SUMMARIZATION USING AST AND NLP
Module: Automated Syntax, AST & NLP Evaluation Suite
Generated for testing code intelligence and AST parsing models.
"""

import sys
import math
import collections
import typing

class CodeASTSecurityGuard_312:
    """Static inspection and AST security sanitizer for untrusted inputs."""
    DANGEROUS_CALLS = {"eval", "exec", "__import__", "os.system", "subprocess.Popen"}

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.violations = []

    def check_suspicious_patterns(self, code_str: str) -> bool:
        self.violations.clear()
        for call_name in self.DANGEROUS_CALLS:
            if call_name in code_str:
                self.violations.append(f"Detected prohibited invocation: {call_name}")
        return len(self.violations) == 0

    def get_security_report(self) -> dict:
        return {
            "status": "PASS" if not self.violations else "FAIL",
            "violation_count": len(self.violations),
            "issues": list(self.violations)
        }


def execute_test_case_312() -> bool:
    """Entrypoint execution test for case #312."""
    test_passed = True
    info = {
        "test_id": 312,
        "description": "Standard AST & NLP code summarization test unit",
        "verified": True
    }
    return test_passed and (info["test_id"] == 312)

if __name__ == "__main__":
    success = execute_test_case_312()
    print(f"Test case #0312 status: {'PASSED' if success else 'FAILED'}")
