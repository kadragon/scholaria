"""
Question suggestion service based on topic content.
"""

import logging
import re

from django.core.cache import cache

from rag.models import ContextItem, Topic

logger = logging.getLogger(__name__)


class QuestionSuggestionService:
    """Service for generating question suggestions based on topic content."""

    def __init__(self) -> None:
        """Initialize the question suggestion service."""
        self.cache_timeout = 3600  # 1 hour cache
        self.max_suggestions = 8
        self.max_content_length = 2000  # Limit content for processing

    def generate_questions_from_content(self, content: str) -> list[str]:
        """
        Generate questions from given content using pattern-based approach.

        Args:
            content: Text content to generate questions from

        Returns:
            List of generated questions
        """
        if not content or len(content.strip()) < 10:
            return []

        # Truncate content if too long
        if len(content) > self.max_content_length:
            content = content[: self.max_content_length] + "..."

        questions = []

        # Pattern-based question generation
        questions.extend(self._generate_what_questions(content))
        questions.extend(self._generate_how_questions(content))
        questions.extend(self._generate_why_questions(content))
        questions.extend(self._generate_when_questions(content))
        questions.extend(self._generate_definition_questions(content))

        # Remove duplicates and limit results
        unique_questions = list(
            dict.fromkeys(questions)
        )  # Preserve order while removing duplicates
        return unique_questions[:5]  # Limit to 5 questions per content piece

    def _generate_what_questions(self, content: str) -> list[str]:
        """Generate 'What is...' type questions."""
        questions = []

        # Look for definitions and key terms
        sentences = re.split(r"[.!?]+", content)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            # Look for "is a", "are", "means" patterns
            if re.search(
                r"\b(is a|are|means|refers to|defined as)\b", sentence, re.IGNORECASE
            ):
                # Extract the subject before these patterns
                match = re.search(
                    r"^([^.!?]*?)\s+(is a|are|means|refers to|defined as)",
                    sentence,
                    re.IGNORECASE,
                )
                if match:
                    subject = match.group(1).strip()
                    if len(subject) > 5 and len(subject) < 50:
                        questions.append(f"What {subject.lower()}?")

        return questions[:2]

    def _generate_how_questions(self, content: str) -> list[str]:
        """Generate 'How to...' type questions."""
        questions = []

        # Look for process-related content
        if re.search(
            r"\b(steps?|process|method|procedure|way to|how to)\b",
            content,
            re.IGNORECASE,
        ):
            # Extract main topics
            topics = self._extract_main_topics(content)
            for topic in topics[:2]:
                questions.append(f"How do you {topic.lower()}?")

        return questions

    def _generate_why_questions(self, content: str) -> list[str]:
        """Generate 'Why...' type questions."""
        questions = []

        # Look for causal or explanatory content
        if re.search(
            r"\b(because|since|due to|reason|cause|result)\b", content, re.IGNORECASE
        ):
            topics = self._extract_main_topics(content)
            if topics:
                questions.append(f"Why is {topics[0].lower()} important?")

        return questions[:1]

    def _generate_when_questions(self, content: str) -> list[str]:
        """Generate 'When...' type questions."""
        questions = []

        # Look for temporal content
        if re.search(
            r"\b(when|during|after|before|while|time)\b", content, re.IGNORECASE
        ):
            topics = self._extract_main_topics(content)
            if topics:
                questions.append(f"When do you use {topics[0].lower()}?")

        return questions[:1]

    def _generate_definition_questions(self, content: str) -> list[str]:
        """Generate definition-style questions."""
        questions = []

        # Look for technical terms (capitalized words, terms with numbers/symbols)
        terms = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", content)
        terms.extend(re.findall(r"\b\w*[0-9]\w*\b", content))

        for term in terms[:2]:
            if len(term) > 3 and len(term) < 30:
                questions.append(f"What is {term}?")

        return questions

    def _extract_main_topics(self, content: str) -> list[str]:
        """Extract main topics/subjects from content."""
        # Simple extraction of noun phrases
        words = content.split()
        topics = []

        for i, word in enumerate(words):
            if len(word) > 4 and word.isalpha():
                # Look for potential topics (nouns)
                if i < len(words) - 1 and words[i + 1].lower() in [
                    "is",
                    "are",
                    "can",
                    "will",
                    "should",
                ]:
                    topics.append(word)

        return topics[:3]

    def get_topic_suggestions(self, topic_id: int) -> list[str]:
        """
        Get question suggestions for a specific topic.

        Args:
            topic_id: ID of the topic to get suggestions for

        Returns:
            List of suggested questions
        """
        # Check cache first
        cache_key = f"question_suggestions_{topic_id}"
        cached_suggestions = cache.get(cache_key)
        if cached_suggestions:
            return cached_suggestions

        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            logger.warning(f"Topic {topic_id} not found")
            return []

        suggestions = []

        # Get all context items for the topic
        context_items = ContextItem.objects.filter(
            context__in=topic.contexts.filter(processing_status="COMPLETED")
        ).order_by("?")[:10]  # Random sample of up to 10 items

        for item in context_items:
            item_questions = self.generate_questions_from_content(item.content)
            suggestions.extend(item_questions)

            # Stop if we have enough suggestions
            if len(suggestions) >= self.max_suggestions:
                break

        # Remove duplicates and limit results
        unique_suggestions = list(dict.fromkeys(suggestions))
        final_suggestions = unique_suggestions[: self.max_suggestions]

        # Cache the results
        cache.set(cache_key, final_suggestions, self.cache_timeout)

        return final_suggestions
