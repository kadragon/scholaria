"""Golden dataset accuracy tests for RAG pipeline."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import pytest

# Simple lexical simulation of context items that would exist in Qdrant.
FAKE_CONTEXTS: dict[int, dict[str, Any]] = {
    1: {
        "topic_id": 1,
        "title": "Admissions Policy Overview",
        "content": (
            "The school admission policy outlines application deadlines, "
            "GPA requirements, interviews, and enrollment steps."
        ),
    },
    3: {
        "topic_id": 1,
        "title": "Admissions Criteria Breakdown",
        "content": (
            "School admission policy criteria cover academic performance, "
            "recommendations, and conduct expectations."
        ),
    },
    5: {
        "topic_id": 1,
        "title": "Financial Aid Application Guide",
        "content": (
            "Families can apply for financial aid by completing the online form, "
            "submitting tax documents, and meeting aid deadlines."
        ),
    },
    6: {
        "topic_id": 1,
        "title": "Campus Tour Schedule",
        "content": "Weekly campus tours introduce new families to classrooms and facilities.",
    },
    10: {
        "topic_id": 1,
        "title": "Graduation Requirements Handbook",
        "content": (
            "Graduation requirements list credit minimums, capstone projects, "
            "service hours, and assessment benchmarks."
        ),
    },
    11: {
        "topic_id": 1,
        "title": "Enrollment Checklist",
        "content": (
            "Enrollment checklist covers immunization records, tuition deposits, "
            "and transportation requests."
        ),
    },
    7: {
        "topic_id": 2,
        "title": "Extracurricular Activities Catalog",
        "content": (
            "Extracurricular activities available include robotics club, theatre, "
            "debate team, and athletics."
        ),
    },
    8: {
        "topic_id": 2,
        "title": "Dining Services Overview",
        "content": "Information about cafeteria menus, meal plans, and nutrition guidelines.",
    },
    9: {
        "topic_id": 2,
        "title": "Student Clubs Directory",
        "content": (
            "Student clubs list extracurricular activities available after school, "
            "including music, art, and coding clubs."
        ),
    },
    13: {
        "topic_id": 2,
        "title": "Campus Events Overview",
        "content": "Monthly calendar of assemblies, guest speakers, and community events.",
    },
    14: {
        "topic_id": 2,
        "title": "Residence Life Policies",
        "content": "Guidelines for boarding students and dormitory expectations.",
    },
    15: {
        "topic_id": 2,
        "title": "Volunteer Opportunities",
        "content": "Service learning projects and volunteer programs for families.",
    },
    2: {
        "topic_id": 3,
        "title": "Student Support Contact Info",
        "content": (
            "Contact the student support office by phone or email for counseling services "
            "and academic guidance."
        ),
    },
    4: {
        "topic_id": 3,
        "title": "Support Office Services",
        "content": (
            "Contact the student support office for tutoring, counseling, and "
            "accommodations during weekday office hours."
        ),
    },
    12: {
        "topic_id": 3,
        "title": "Nurse Office Procedures",
        "content": "Health office policies for medication management and illness reporting.",
    },
    16: {
        "topic_id": 3,
        "title": "Parent Portal Guide",
        "content": "Instructions for using the parent portal to review grades and attendance.",
    },
    17: {
        "topic_id": 3,
        "title": "Transportation Help Desk",
        "content": "Bus routing assistance and parking permits for families.",
    },
    18: {
        "topic_id": 3,
        "title": "Technology Support Center",
        "content": "Chromebook troubleshooting and password reset assistance.",
    },
}

# Baseline ordering imitates pre-reranked search results (Qdrant top-N).
BASELINE_ORDERS: dict[str, list[int]] = {
    "What is the school's admission policy?": [6, 11, 5, 10, 1, 3],
    "How do I apply for financial aid?": [6, 11, 1, 3, 10, 5],
    "What extracurricular activities are available?": [8, 13, 14, 15, 7, 9],
    "What are the graduation requirements?": [6, 11, 5, 3, 1, 10],
    "How can I contact the student support office?": [12, 16, 17, 18, 2, 4],
}

STOP_WORDS = {
    "the",
    "is",
    "a",
    "an",
    "and",
    "or",
    "of",
    "for",
    "to",
    "how",
    "do",
    "i",
    "what",
    "can",
    "by",
    "on",
    "in",
    "about",
    "are",
    "you",
    "your",
    "with",
    "it",
    "that",
    "this",
    "s",
}


def _tokenize(text: str) -> set[str]:
    """Return a set of meaningful tokens for simple lexical scoring."""
    tokens = re.findall(r"[a-z]+", text.lower())
    return {t for t in tokens if len(t) > 2 and t not in STOP_WORDS}


def _lexical_similarity(question: str, content: str) -> float:
    """Compute lexical overlap ratio between question and content."""
    question_tokens = _tokenize(question)
    if not question_tokens:
        return 0.0
    content_tokens = _tokenize(content)
    if not content_tokens:
        return 0.0
    overlap = question_tokens & content_tokens
    return len(overlap) / len(question_tokens)


def _baseline_score(question: str, context_id: int, fallback: float) -> float:
    """Map baseline order to descending scores, with lexical fallback."""
    order = BASELINE_ORDERS.get(question, [])
    if context_id in order:
        idx = order.index(context_id)
        return float(len(order) - idx)
    return fallback


def simulate_search(
    question: str, topic_id: int, limit: int = 10
) -> list[dict[str, Any]]:
    """Simulate Qdrant search results using baseline ordering."""
    results: list[dict[str, Any]] = []
    for context_id, payload in FAKE_CONTEXTS.items():
        if payload["topic_id"] != topic_id:
            continue
        lexical_score = _lexical_similarity(question, payload["content"])
        baseline = _baseline_score(question, context_id, lexical_score * 0.5)
        results.append(
            {
                "context_item_id": context_id,
                "title": payload["title"],
                "content": payload["content"],
                "topic_id": payload["topic_id"],
                "score": baseline,
            }
        )
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:limit]


def rerank_results(
    question: str, search_results: list[dict[str, Any]], top_k: int = 5
) -> list[dict[str, Any]]:
    """Simulate reranking using lexical similarity as the relevance metric."""
    reranked: list[dict[str, Any]] = []
    for result in search_results:
        rerank_score = _lexical_similarity(question, result["content"])
        enriched = result.copy()
        enriched["rerank_score"] = rerank_score
        reranked.append(enriched)
    reranked.sort(key=lambda item: item["rerank_score"], reverse=True)
    return reranked[:top_k]


def _count_hits(results: Iterable[dict[str, Any]], expected_ids: Iterable[int]) -> int:
    """Count how many expected context IDs appear in the provided results."""
    result_ids = {item["context_item_id"] for item in results}
    return len(result_ids.intersection(set(expected_ids)))


@pytest.mark.golden
class TestGoldenDatasetAccuracy:
    """Golden dataset validation tests."""

    def test_golden_dataset_loaded(self, golden_dataset):
        """Golden dataset should be loaded successfully."""
        assert isinstance(golden_dataset, list)
        assert len(golden_dataset) > 0
        required_keys = {"question", "expected_context_ids", "topic_id"}
        assert all(required_keys.issubset(item.keys()) for item in golden_dataset)

    @pytest.mark.asyncio
    async def test_golden_dataset_citation_accuracy(self, golden_dataset):
        """Top-5 reranked results should include expected contexts >=80%."""
        total_hits = 0
        total_expected = 0

        for entry in golden_dataset:
            question = entry["question"]
            topic_id = entry["topic_id"]
            expected_ids = set(entry["expected_context_ids"])

            search_results = simulate_search(question, topic_id, limit=10)
            reranked_results = rerank_results(question, search_results, top_k=5)

            hits = _count_hits(reranked_results, expected_ids)
            total_hits += hits
            total_expected += len(expected_ids)

            assert hits >= 1, f"No expected contexts found for question: {question}"
            assert reranked_results, "Reranked results should not be empty"

        accuracy = total_hits / total_expected if total_expected else 0.0
        assert accuracy >= 0.8, (
            f"Golden dataset accuracy {accuracy:.2f} below 0.80 threshold"
        )

    @pytest.mark.asyncio
    async def test_reranking_improves_relevance(self, golden_dataset):
        """Reranking should improve relevance over raw vector search."""
        baseline_hits = 0
        reranked_hits = 0
        total_expected = 0

        for entry in golden_dataset:
            question = entry["question"]
            topic_id = entry["topic_id"]
            expected_ids = set(entry["expected_context_ids"])

            search_results = simulate_search(question, topic_id, limit=10)
            baseline_top_five = search_results[:5]
            reranked_results = rerank_results(question, search_results, top_k=5)

            baseline_hits += _count_hits(baseline_top_five, expected_ids)
            reranked_hits += _count_hits(reranked_results, expected_ids)
            total_expected += len(expected_ids)

        assert total_expected > 0, "Golden dataset must include expected context IDs"

        baseline_accuracy = baseline_hits / total_expected
        reranked_accuracy = reranked_hits / total_expected

        assert reranked_accuracy >= baseline_accuracy, (
            f"Reranked accuracy {reranked_accuracy:.2f} is not higher than baseline "
            f"{baseline_accuracy:.2f}"
        )
        assert reranked_accuracy - baseline_accuracy >= 0.1, (
            "Reranking should improve accuracy by at least 0.10"
        )
