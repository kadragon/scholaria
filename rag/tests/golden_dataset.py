"""Golden dataset for RAG system quality validation."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, TypedDict

from rag.retrieval.rag import RAGService


class GoldenTestCase(TypedDict):
    """Structure for a golden test case."""

    question: str
    expected_keywords: list[str]
    expected_topics: list[str]
    difficulty: str  # "easy", "medium", "hard"
    category: str
    description: str


class ValidationResult(TypedDict):
    """Structure for validation result."""

    question: str
    answer: str
    keyword_score: float
    relevance_score: float
    passed: bool
    response_time: float


class QualityReport(TypedDict):
    """Structure for quality validation report."""

    overall_score: float
    test_results: list[ValidationResult]
    summary: dict[str, Any]


class GoldenDataset:
    """Manages golden dataset for RAG quality validation."""

    def __init__(self) -> None:
        """Initialize golden dataset."""
        self._test_cases: list[GoldenTestCase] = []
        self._load_default_dataset()

    def _load_default_dataset(self) -> None:
        """Load the default golden dataset."""
        # Comprehensive test cases covering various ML topics and difficulties
        self._test_cases = [
            # Fundamentals - Easy
            {
                "question": "What are neural networks?",
                "expected_keywords": [
                    "neural networks",
                    "computational models",
                    "nodes",
                    "neurons",
                    "layers",
                    "connections",
                    "weights",
                ],
                "expected_topics": ["neural networks", "machine learning"],
                "difficulty": "easy",
                "category": "fundamentals",
                "description": "Basic definition of neural networks",
            },
            {
                "question": "What is supervised learning?",
                "expected_keywords": [
                    "supervised learning",
                    "labeled data",
                    "training data",
                    "mapping",
                    "classification",
                    "regression",
                ],
                "expected_topics": ["supervised learning", "machine learning"],
                "difficulty": "easy",
                "category": "fundamentals",
                "description": "Basic definition of supervised learning",
            },
            {
                "question": "What is deep learning?",
                "expected_keywords": [
                    "deep learning",
                    "neural networks",
                    "multiple layers",
                    "hidden layers",
                    "feature representations",
                    "computer vision",
                    "natural language processing",
                ],
                "expected_topics": ["deep learning", "neural networks"],
                "difficulty": "easy",
                "category": "fundamentals",
                "description": "Basic definition of deep learning",
            },
            # Algorithms - Medium
            {
                "question": "How does backpropagation work in neural networks?",
                "expected_keywords": [
                    "backpropagation",
                    "gradient",
                    "weights",
                    "error",
                    "training",
                    "optimization",
                    "chain rule",
                ],
                "expected_topics": ["neural networks", "training", "algorithms"],
                "difficulty": "medium",
                "category": "algorithms",
                "description": "Understanding backpropagation algorithm",
            },
            {
                "question": "What is gradient descent and how is it used in machine learning?",
                "expected_keywords": [
                    "gradient descent",
                    "optimization",
                    "loss function",
                    "parameters",
                    "learning rate",
                    "iterative",
                    "minimize",
                ],
                "expected_topics": ["optimization", "training", "algorithms"],
                "difficulty": "medium",
                "category": "algorithms",
                "description": "Understanding gradient descent optimization",
            },
            {
                "question": "Explain the difference between batch, mini-batch, and stochastic gradient descent",
                "expected_keywords": [
                    "batch",
                    "mini-batch",
                    "stochastic",
                    "gradient descent",
                    "batch size",
                    "convergence",
                    "noise",
                ],
                "expected_topics": ["optimization", "training"],
                "difficulty": "medium",
                "category": "algorithms",
                "description": "Comparing different gradient descent variants",
            },
            # Applications - Medium to Hard
            {
                "question": "How are neural networks used in computer vision?",
                "expected_keywords": [
                    "computer vision",
                    "convolutional",
                    "CNN",
                    "image",
                    "feature detection",
                    "visual patterns",
                ],
                "expected_topics": [
                    "computer vision",
                    "neural networks",
                    "applications",
                ],
                "difficulty": "medium",
                "category": "applications",
                "description": "Neural networks in computer vision applications",
            },
            {
                "question": "What are the key challenges in training deep neural networks?",
                "expected_keywords": [
                    "vanishing gradients",
                    "exploding gradients",
                    "overfitting",
                    "underfitting",
                    "regularization",
                    "initialization",
                    "depth",
                ],
                "expected_topics": ["deep learning", "training", "challenges"],
                "difficulty": "hard",
                "category": "algorithms",
                "description": "Challenges in deep learning training",
            },
            # Evaluation - Medium
            {
                "question": "How do you evaluate machine learning models?",
                "expected_keywords": [
                    "evaluation",
                    "accuracy",
                    "precision",
                    "recall",
                    "F1-score",
                    "cross-validation",
                    "overfitting",
                    "metrics",
                ],
                "expected_topics": ["evaluation", "model assessment"],
                "difficulty": "medium",
                "category": "fundamentals",
                "description": "Model evaluation techniques and metrics",
            },
            {
                "question": "What is cross-validation and why is it important?",
                "expected_keywords": [
                    "cross-validation",
                    "k-fold",
                    "validation",
                    "overfitting",
                    "generalization",
                    "test set",
                    "performance estimation",
                ],
                "expected_topics": ["evaluation", "validation"],
                "difficulty": "medium",
                "category": "fundamentals",
                "description": "Understanding cross-validation techniques",
            },
            # Advanced Topics - Hard
            {
                "question": "Explain the architecture and training process of transformers in NLP",
                "expected_keywords": [
                    "transformers",
                    "attention",
                    "self-attention",
                    "encoder",
                    "decoder",
                    "NLP",
                    "language models",
                ],
                "expected_topics": ["transformers", "NLP", "attention"],
                "difficulty": "hard",
                "category": "applications",
                "description": "Advanced transformer architecture",
            },
            {
                "question": "What are generative adversarial networks and how do they work?",
                "expected_keywords": [
                    "GAN",
                    "generative",
                    "adversarial",
                    "generator",
                    "discriminator",
                    "game theory",
                    "minimax",
                ],
                "expected_topics": ["GAN", "generative models"],
                "difficulty": "hard",
                "category": "applications",
                "description": "Understanding GANs architecture and training",
            },
        ]

    def load_dataset(self, file_path: Path | None = None) -> None:
        """Load dataset from file."""
        if file_path and file_path.exists():
            with file_path.open() as f:
                data = json.load(f)
                self._test_cases = data["test_cases"]
        else:
            self._load_default_dataset()

    def get_test_cases(
        self,
        category: str | None = None,
        difficulty: str | None = None,
        max_cases: int | None = None,
    ) -> list[GoldenTestCase]:
        """Get test cases with optional filtering."""
        cases = self._test_cases

        if category:
            cases = [case for case in cases if case["category"] == category]

        if difficulty:
            cases = [case for case in cases if case["difficulty"] == difficulty]

        if max_cases:
            cases = cases[:max_cases]

        return cases

    def save_dataset(self, file_path: Path) -> None:
        """Save current dataset to file."""
        data = {"test_cases": self._test_cases}
        with file_path.open("w") as f:
            json.dump(data, f, indent=2)


def validate_rag_quality(
    rag_service: RAGService,
    topic_ids: list[int],
    max_test_cases: int | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    keyword_threshold: float = 0.3,
    relevance_threshold: float = 0.7,
) -> QualityReport:
    """Validate RAG system quality using golden dataset."""
    dataset = GoldenDataset()
    test_cases = dataset.get_test_cases(
        category=category, difficulty=difficulty, max_cases=max_test_cases
    )

    results: list[ValidationResult] = []
    total_response_time = 0.0

    for case in test_cases:
        start_time = time.time()

        try:
            # Query the RAG system
            rag_result = rag_service.query(query=case["question"], topic_ids=topic_ids)
            response_time = time.time() - start_time
            total_response_time += response_time

            answer = rag_result.get("answer", "")

            # Calculate keyword score
            keyword_score = _calculate_keyword_score(answer, case["expected_keywords"])

            # Calculate relevance score (simplified - based on presence of sources)
            sources = rag_result.get("sources", [])
            relevance_score = min(1.0, len(sources) / 3.0)  # Normalize to max 3 sources

            # Determine if test passed
            passed = (
                keyword_score >= keyword_threshold
                and relevance_score >= relevance_threshold
            )

            result: ValidationResult = {
                "question": case["question"],
                "answer": answer,
                "keyword_score": keyword_score,
                "relevance_score": relevance_score,
                "passed": passed,
                "response_time": response_time,
            }

        except Exception as e:
            # Handle errors gracefully
            response_time = time.time() - start_time
            total_response_time += response_time

            result = {
                "question": case["question"],
                "answer": f"Error: {str(e)}",
                "keyword_score": 0.0,
                "relevance_score": 0.0,
                "passed": False,
                "response_time": response_time,
            }

        results.append(result)

    # Calculate overall metrics
    passed_tests = sum(1 for r in results if r["passed"])
    total_tests = len(results)
    overall_score = passed_tests / total_tests if total_tests > 0 else 0.0
    avg_response_time = total_response_time / total_tests if total_tests > 0 else 0.0

    # Create quality report
    report: QualityReport = {
        "overall_score": overall_score,
        "test_results": results,
        "summary": {
            "total_test_cases": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "avg_response_time": avg_response_time,
            "keyword_threshold": keyword_threshold,
            "relevance_threshold": relevance_threshold,
        },
    }

    return report


def _calculate_keyword_score(answer: str, expected_keywords: list[str]) -> float:
    """Calculate keyword match score."""
    if not answer or not expected_keywords:
        return 0.0

    answer_lower = answer.lower()
    matched_keywords = 0

    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            matched_keywords += 1

    return matched_keywords / len(expected_keywords)
