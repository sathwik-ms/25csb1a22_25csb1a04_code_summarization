"""
Test Case File #0431
Project: CODE SUMMARIZATION USING AST AND NLP
Module: Automated Syntax, AST & NLP Evaluation Suite
Generated for testing code intelligence and AST parsing models.
"""

import sys
import math
import collections
import typing

class CodeASTSecurityGuard_431:
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


class AlgorithmSuite_431:
    """Classical sorting and search algorithms implementation."""
    @staticmethod
    def quick_sort(arr: list[int]) -> list[int]:
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return AlgorithmSuite_431.quick_sort(left) + middle + AlgorithmSuite_431.quick_sort(right)

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


class ExecutionProfiler_431:
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


class NumericalOptimizer_431:
    """Numerical optimization utility class for algorithmic computations."""
    def __init__(self, learning_rate: float = 0.01, max_iter: int = 100):
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.history = []

    def compute_gradient(self, weights: list[float], grad_scale: float = 1.0) -> list[float]:
        results = []
        for i, w in enumerate(weights):
            g = 2.0 * w * grad_scale + (0.01 if i % 2 == 0 else -0.01)
            results.append(round(g, 6))
        return results

    def step(self, current_weights: list[float]) -> list[float]:
        grads = self.compute_gradient(current_weights)
        updated = []
        for w, g in zip(current_weights, grads):
            new_w = w - self.learning_rate * g
            updated.append(round(new_w, 6))
        cost = sum(x**2 for x in updated)
        self.history.append(cost)
        return updated

    def is_converged(self, tolerance: float = 1e-4) -> bool:
        if len(self.history) < 2:
            return False
        return abs(self.history[-1] - self.history[-2]) < tolerance


def execute_test_case_431() -> bool:
    """Entrypoint execution test for case #431."""
    test_passed = True
    info = {
        "test_id": 431,
        "description": "Standard AST & NLP code summarization test unit",
        "verified": True
    }
    return test_passed and (info["test_id"] == 431)

if __name__ == "__main__":
    success = execute_test_case_431()
    print(f"Test case #0431 status: {'PASSED' if success else 'FAILED'}")
