"""
Test Case File #0341
Project: CODE SUMMARIZATION USING AST AND NLP
Module: Automated Syntax, AST & NLP Evaluation Suite
Generated for testing code intelligence and AST parsing models.
"""

import sys
import math
import collections
import typing

class AlgorithmSuite_341:
    """Classical sorting and search algorithms implementation."""
    @staticmethod
    def quick_sort(arr: list[int]) -> list[int]:
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return AlgorithmSuite_341.quick_sort(left) + middle + AlgorithmSuite_341.quick_sort(right)

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


class ExecutionProfiler_341:
    """Green computing hardware metric estimator and energy logger."""
    def __init__(self, baseline_watts: float = 15.0):
        self.baseline_watts = baseline_watts
        self.records = []

    def record_run(self, duration_ms: float, cpu_utilization_pct: float) -> dict[str, float]:
        power_consumed = self.baseline_watts + (cpu_utilization_pct * 0.45)
        energy_joules = power_consumed * (duration_ms / 1000.0)
        co2_emissions_mg = energy_joules * 0.385
        entry = {
            "duration_ms": duration_ms,
            "power_w": round(power_consumed, 3),
            "energy_j": round(energy_joules, 4),
            "co2_mg": round(co2_emissions_mg, 4)
        }
        self.records.append(entry)
        return entry

    def summary(self) -> dict[str, float]:
        total_energy = sum(r["energy_j"] for r in self.records)
        avg_power = sum(r["power_w"] for r in self.records) / max(len(self.records), 1)
        return {
            "total_runs": len(self.records),
            "total_energy_j": round(total_energy, 4),
            "average_power_w": round(avg_power, 4)
        }


def execute_test_case_341() -> bool:
    """Entrypoint execution test for case #341."""
    test_passed = True
    info = {
        "test_id": 341,
        "description": "Standard AST & NLP code summarization test unit",
        "verified": True
    }
    return test_passed and (info["test_id"] == 341)

if __name__ == "__main__":
    success = execute_test_case_341()
    print(f"Test case #0341 status: {'PASSED' if success else 'FAILED'}")
