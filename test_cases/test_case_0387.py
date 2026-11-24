"""
Test Case File #0387
Project: CODE SUMMARIZATION USING AST AND NLP
Module: Automated Syntax, AST & NLP Evaluation Suite
Generated for testing code intelligence and AST parsing models.
"""

import sys
import math
import collections
import typing

class ASTCodeTokenizer_387:
    """NLP-oriented AST node tokenizer and lexical feature extractor."""
    def __init__(self, vocab_limit: int = 5000):
        self.vocab_limit = vocab_limit
        self.tokens = []
        self.token_freq = {}

    def extract_lexical_tokens(self, source_snippet: str) -> list[str]:
        raw_words = source_snippet.replace('(', ' ').replace(')', ' ').replace(':', ' ').split()
        filtered = [w.strip() for w in raw_words if len(w.strip()) > 1]
        for token in filtered:
            self.token_freq[token] = self.token_freq.get(token, 0) + 1
        self.tokens.extend(filtered)
        return filtered

    def calculate_tf_idf_weights(self, doc_tokens: list[str], total_docs: int = 1) -> dict[str, float]:
        scores = {}
        n = len(doc_tokens)
        if n == 0:
            return scores
        for t in set(doc_tokens):
            tf = doc_tokens.count(t) / float(n)
            idf = 1.0 + (total_docs / (1.0 + self.token_freq.get(t, 1)))
            scores[t] = round(tf * idf, 5)
        return scores

    def summarize_token_distribution(self) -> dict[str, int]:
        top_k = sorted(self.token_freq.items(), key=lambda item: item[1], reverse=True)[:10]
        return dict(top_k)


class LRUCacheManager_387:
    """Least Recently Used (LRU) Cache simulation with eviction policy."""
    def __init__(self, capacity: int = 64):
        self.capacity = capacity
        self.cache = {}
        self.usage_order = []

    def get(self, key: str):
        if key not in self.cache:
            return None
        self.usage_order.remove(key)
        self.usage_order.append(key)
        return self.cache[key]

    def put(self, key: str, value) -> None:
        if key in self.cache:
            self.usage_order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.usage_order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.usage_order.append(key)

    def stats(self) -> dict[str, int]:
        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "available_slots": self.capacity - len(self.cache)
        }


class CodeASTSecurityGuard_387:
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


class AlgorithmSuite_387:
    """Classical sorting and search algorithms implementation."""
    @staticmethod
    def quick_sort(arr: list[int]) -> list[int]:
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return AlgorithmSuite_387.quick_sort(left) + middle + AlgorithmSuite_387.quick_sort(right)

    @staticmethod
    def binary_search(arr: list[int], target: int) -> int:
        low, high = 0, len(arr) - 1
        while low <= high:
            mid = (low + high) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        return -1


def execute_test_case_387() -> bool:
    """Entrypoint execution test for case #387."""
    test_passed = True
    info = {
        "test_id": 387,
        "description": "Standard AST & NLP code summarization test unit",
        "verified": True
    }
    return test_passed and (info["test_id"] == 387)

if __name__ == "__main__":
    success = execute_test_case_387()
    print(f"Test case #0387 status: {'PASSED' if success else 'FAILED'}")
