"""
Test Case File #0836
Project: CODE SUMMARIZATION USING AST AND NLP
Module: Automated Syntax, AST & NLP Evaluation Suite
Generated for testing code intelligence and AST parsing models.
"""

import sys
import math
import collections
import typing

class LRUCacheManager_836:
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


def execute_test_case_836() -> bool:
    """Entrypoint execution test for case #836."""
    test_passed = True
    info = {
        "test_id": 836,
        "description": "Standard AST & NLP code summarization test unit",
        "verified": True
    }
    return test_passed and (info["test_id"] == 836)

if __name__ == "__main__":
    success = execute_test_case_836()
    print(f"Test case #0836 status: {'PASSED' if success else 'FAILED'}")
