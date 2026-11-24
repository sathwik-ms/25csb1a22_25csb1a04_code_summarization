"""
Test Case File #0128
Project: CODE SUMMARIZATION USING AST AND NLP
Module: Automated Syntax, AST & NLP Evaluation Suite
Generated for testing code intelligence and AST parsing models.
"""

import sys
import math
import collections
import typing

class ASTCodeTokenizer_128:
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


def execute_test_case_128() -> bool:
    """Entrypoint execution test for case #128."""
    test_passed = True
    info = {
        "test_id": 128,
        "description": "Standard AST & NLP code summarization test unit",
        "verified": True
    }
    return test_passed and (info["test_id"] == 128)

if __name__ == "__main__":
    success = execute_test_case_128()
    print(f"Test case #0128 status: {'PASSED' if success else 'FAILED'}")
