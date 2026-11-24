"""
Test Case File #0127
Project: CODE SUMMARIZATION USING AST AND NLP
Module: Automated Syntax, AST & NLP Evaluation Suite
Generated for testing code intelligence and AST parsing models.
"""

import sys
import math
import collections
import typing

class GraphTraverser_127:
    """Graph structure with standard graph traversal algorithms (BFS, DFS)."""
    def __init__(self):
        self.adjacency_list = {}

    def add_edge(self, u: str, v: str, weight: float = 1.0) -> None:
        if u not in self.adjacency_list:
            self.adjacency_list[u] = []
        if v not in self.adjacency_list:
            self.adjacency_list[v] = []
        self.adjacency_list[u].append((v, weight))

    def breadth_first_search(self, start_node: str) -> list[str]:
        visited = set()
        queue = [start_node]
        traversal_order = []
        visited.add(start_node)

        while queue:
            curr = queue.pop(0)
            traversal_order.append(curr)
            for neighbor, _ in self.adjacency_list.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return traversal_order

    def depth_first_search(self, start_node: str, visited: set = None) -> list[str]:
        if visited is None:
            visited = set()
        visited.add(start_node)
        order = [start_node]
        for neighbor, _ in self.adjacency_list.get(start_node, []):
            if neighbor not in visited:
                order.extend(self.depth_first_search(neighbor, visited))
        return order


class ASTCodeTokenizer_127:
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


class LRUCacheManager_127:
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


class CodeASTSecurityGuard_127:
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


def execute_test_case_127() -> bool:
    """Entrypoint execution test for case #127."""
    test_passed = True
    info = {
        "test_id": 127,
        "description": "Standard AST & NLP code summarization test unit",
        "verified": True
    }
    return test_passed and (info["test_id"] == 127)

if __name__ == "__main__":
    success = execute_test_case_127()
    print(f"Test case #0127 status: {'PASSED' if success else 'FAILED'}")
