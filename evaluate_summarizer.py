"""
evaluate_summarizer.py
======================
Evaluates the code summarization pipeline against reference summaries
using BLEU (n-gram precision with brevity penalty) and ROUGE-L (longest
common subsequence) metrics across 20 canonical Python algorithms.

Works standalone with pure-Python metric implementations (or standard nltk /
rouge-score if installed) so evaluation runs deterministically in any environment.

Usage:
    python evaluate_summarizer.py
"""

from __future__ import annotations

import collections
import json
import math
import re
import sys
from typing import Dict, List, Tuple

from model_pipeline import CodeSummarizer
from pdg_extractor import extract_pdg_context

# ── 20 Reference Benchmark Pairs (CodeSearchNet Style) ────────────────────────
BENCHMARK_PAIRS = [
    {
        "id": 1,
        "name": "addition",
        "code": "def add(a, b):\n    return a + b",
        "reference": "Returns the sum of two numbers a and b.",
    },
    {
        "id": 2,
        "name": "reverse_string",
        "code": "def reverse_string(s):\n    return s[::-1]",
        "reference": "Reverses a string using slice notation.",
    },
    {
        "id": 3,
        "name": "is_palindrome",
        "code": "def is_palindrome(s):\n    return s == s[::-1]",
        "reference": "Checks if a string is a palindrome.",
    },
    {
        "id": 4,
        "name": "factorial",
        "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        "reference": "Calculates the factorial of n recursively.",
    },
    {
        "id": 5,
        "name": "flatten_list",
        "code": "def flatten(lst):\n    return [item for sublist in lst for item in sublist]",
        "reference": "Flattens a two dimensional list into a single list.",
    },
    {
        "id": 6,
        "name": "fibonacci",
        "code": "def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
        "reference": "Generates the nth Fibonacci number iteratively.",
    },
    {
        "id": 7,
        "name": "binary_search",
        "code": "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1",
        "reference": "Performs binary search on a sorted list to find target index.",
    },
    {
        "id": 8,
        "name": "is_prime",
        "code": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
        "reference": "Determines whether an integer is prime.",
    },
    {
        "id": 9,
        "name": "gcd",
        "code": "def gcd(a, b):\n    while b:\n        a, b = b, a % b\n    return a",
        "reference": "Computes the greatest common divisor of two integers.",
    },
    {
        "id": 10,
        "name": "count_vowels",
        "code": "def count_vowels(s):\n    return sum(1 for ch in s.lower() if ch in 'aeiou')",
        "reference": "Counts the number of vowels in a string.",
    },
    {
        "id": 11,
        "name": "find_max",
        "code": "def find_max(numbers):\n    if not numbers:\n        return None\n    m = numbers[0]\n    for x in numbers[1:]:\n        if x > m:\n            m = x\n    return m",
        "reference": "Finds the maximum value in an iterable of numbers.",
    },
    {
        "id": 12,
        "name": "merge_dicts",
        "code": "def merge_dicts(d1, d2):\n    res = d1.copy()\n    res.update(d2)\n    return res",
        "reference": "Merges two dictionaries into a single dictionary.",
    },
    {
        "id": 13,
        "name": "clamp",
        "code": "def clamp(val, low, high):\n    return max(low, min(val, high))",
        "reference": "Restricts a numerical value within specified low and high bounds.",
    },
    {
        "id": 14,
        "name": "remove_duplicates",
        "code": "def remove_duplicates(seq):\n    seen = set()\n    return [x for x in seq if not (x in seen or seen.add(x))]",
        "reference": "Removes duplicate elements while preserving initial ordering.",
    },
    {
        "id": 15,
        "name": "calculate_discount",
        "code": "def calculate_discount(price, is_member):\n    discount = 0.1 * price if is_member else 0\n    return price - discount",
        "reference": "Calculates discounted final price for member status.",
    },
    {
        "id": 16,
        "name": "to_camel_case",
        "code": "def to_camel(s):\n    parts = s.split('_')\n    return parts[0] + ''.join(p.capitalize() for p in parts[1:])",
        "reference": "Converts snake case string to camel case.",
    },
    {
        "id": 17,
        "name": "chunk_list",
        "code": "def chunk(lst, n):\n    return [lst[i:i+n] for i in range(0, len(lst), n)]",
        "reference": "Splits a list into smaller chunks of size n.",
    },
    {
        "id": 18,
        "name": "celsius_to_fahrenheit",
        "code": "def c_to_f(c):\n    return (c * 9/5) + 32",
        "reference": "Converts temperature from Celsius to Fahrenheit.",
    },
    {
        "id": 19,
        "name": "read_json_file",
        "code": "def read_json(path):\n    import json\n    with open(path, 'r', encoding='utf-8') as f:\n        return json.load(f)",
        "reference": "Loads and deserializes JSON content from a file path.",
    },
    {
        "id": 20,
        "name": "safe_divide",
        "code": "def safe_divide(a, b, default=0.0):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return default",
        "reference": "Safely divides two numbers returning default value on division by zero.",
    },
]


def _tokenize(text: str) -> List[str]:
    return [token.lower() for token in re.findall(r"\w+", text)]


def compute_bleu(reference: str, hypothesis: str, max_n: int = 4) -> float:
    """
    Computes sentence BLEU with additive smoothing and brevity penalty.
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    if not hyp_tokens:
        return 0.0
    if not ref_tokens:
        return 0.0

    # Brevity penalty
    c = len(hyp_tokens)
    r = len(ref_tokens)
    bp = 1.0 if c > r else math.exp(1 - (r / c))

    weights = [1.0 / max_n] * max_n
    precisions = []

    for n in range(1, max_n + 1):
        hyp_ngrams = collections.Counter(
            tuple(hyp_tokens[i : i + n]) for i in range(len(hyp_tokens) - n + 1)
        )
        ref_ngrams = collections.Counter(
            tuple(ref_tokens[i : i + n]) for i in range(len(ref_tokens) - n + 1)
        )

        overlap = sum(min(count, ref_ngrams.get(ng, 0)) for ng, count in hyp_ngrams.items())
        total = max(1, sum(hyp_ngrams.values()))

        # Additive smoothing
        smoothed_precision = (overlap + 1.0) / (total + 1.0)
        precisions.append(smoothed_precision)

    log_sum = sum(w * math.log(p) for w, p in zip(weights, precisions))
    return round(bp * math.exp(log_sum), 4)


def compute_rouge_l(reference: str, hypothesis: str) -> float:
    """
    Computes ROUGE-L F1 score based on Longest Common Subsequence (LCS).
    """
    ref_tokens = _tokenize(reference)
    hyp_tokens = _tokenize(hypothesis)

    if not ref_tokens or not hyp_tokens:
        return 0.0

    m, n = len(ref_tokens), len(hyp_tokens)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    lcs = dp[m][n]
    precision = lcs / n
    recall = lcs / m

    if precision + recall == 0:
        return 0.0

    f1 = (2 * precision * recall) / (precision + recall)
    return round(f1, 4)


def run_evaluation() -> Dict:
    print("=" * 80)
    print("  CODE SUMMARIZATION NLP EVALUATION BENCHMARK (20 SAMPLES)")
    print("=" * 80)

    summarizer = CodeSummarizer()
    results = []

    header = f"{'#':<3} {'Function Name':<20} {'BLEU':<8} {'ROUGE-L':<9} {'Generated Summary Preview'}"
    print(header)
    print("-" * 80)

    for item in BENCHMARK_PAIRS:
        pdg_ctx = extract_pdg_context(item["code"])
        summary = summarizer.generate_summary(item["code"], pdg_ctx).strip()

        bleu = compute_bleu(item["reference"], summary)
        rouge_l = compute_rouge_l(item["reference"], summary)

        preview = (summary.replace("\n", " ")[:45] + "...") if len(summary) > 45 else summary
        print(f"{item['id']:<3} {item['name']:<20} {bleu:<8.4f} {rouge_l:<9.4f} {preview}")

        results.append({
            "id": item["id"],
            "name": item["name"],
            "bleu": bleu,
            "rouge_l": rouge_l,
            "reference": item["reference"],
            "generated": summary,
        })

    avg_bleu = sum(r["bleu"] for r in results) / len(results)
    avg_rouge = sum(r["rouge_l"] for r in results) / len(results)

    print("-" * 80)
    print(f"BENCHMARK AVERAGE:  BLEU = {avg_bleu:.4f}  |  ROUGE-L = {avg_rouge:.4f}")
    print("=" * 80)

    report_payload = {
        "status": "success",
        "sample_count": len(results),
        "mean_bleu": round(avg_bleu, 4),
        "mean_rouge_l": round(avg_rouge, 4),
        "samples": results,
    }

    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)

    print("✅ Benchmark complete. Full breakdown saved to evaluation_results.json\n")
    return report_payload


if __name__ == "__main__":
    run_evaluation()
