from __future__ import annotations

import time
from datetime import datetime
from threading import Lock
from typing import Any


class OpenAIUsageMonitor:
    """Monitor and optimize OpenAI API usage."""

    def __init__(self) -> None:
        """Initialize the usage monitor."""
        self._lock = Lock()
        self._reset()

    def _reset(self) -> None:
        self._metrics: dict[str, Any] = {
            "embeddings": {"calls": 0, "tokens": 0, "models": {}},
            "chat_completions": {
                "calls": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "models": {},
            },
            "requests": {},
        }

    def reset_metrics(self) -> None:
        """Reset all usage metrics."""
        with self._lock:
            self._reset()

    def track_embedding_usage(self, tokens: int, model: str) -> None:
        """Track embedding API usage."""
        with self._lock:
            metrics = self._metrics["embeddings"]
            metrics["calls"] += 1
            metrics["tokens"] += tokens
            metrics["models"][model] = metrics["models"].get(model, 0) + 1

    def track_chat_completion_usage(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> None:
        """Track chat completion API usage."""
        total_tokens = prompt_tokens + completion_tokens

        with self._lock:
            metrics = self._metrics["chat_completions"]
            metrics["calls"] += 1
            metrics["prompt_tokens"] += prompt_tokens
            metrics["completion_tokens"] += completion_tokens
            metrics["total_tokens"] += total_tokens
            metrics["models"][model] = metrics["models"].get(model, 0) + 1

    def track_request_timestamp(self, api_type: str) -> None:
        """Track request timestamps for rate limiting detection."""
        current_time = time.time()

        with self._lock:
            cutoff_time = current_time - 3600  # 1 hour ago
            requests = self._metrics["requests"].setdefault(api_type, [])
            requests[:] = [ts for ts in requests if ts > cutoff_time]
            requests.append(current_time)

    def get_metrics(self) -> dict[str, Any]:
        """Get current usage metrics."""
        with self._lock:
            embeddings = self._metrics["embeddings"].copy()
            embeddings["models"] = embeddings["models"].copy()
            chat_completions = self._metrics["chat_completions"].copy()
            chat_completions["models"] = chat_completions["models"].copy()

        return {
            "embeddings": embeddings,
            "chat_completions": chat_completions,
            "timestamp": datetime.now().isoformat(),
        }

    def get_cost_breakdown(self) -> dict[str, float]:
        """Calculate cost breakdown for current usage."""
        metrics = self.get_metrics()

        # OpenAI pricing (approximate, as of 2024)
        pricing = {
            "text-embedding-3-small": 0.00002 / 1000,  # per token
            "text-embedding-3-large": 0.00013 / 1000,  # per token
            "gpt-4o-mini": {
                "prompt": 0.00015 / 1000,  # per token
                "completion": 0.0006 / 1000,  # per token
            },
            "gpt-4o": {
                "prompt": 0.0025 / 1000,  # per token
                "completion": 0.01 / 1000,  # per token
            },
        }

        costs = {"embeddings": 0.0, "chat_completions": 0.0, "total": 0.0}

        # Calculate embedding costs
        embeddings = metrics.get("embeddings", {})
        if "tokens" in embeddings:
            for model, count in embeddings.get("models", {}).items():
                if model in pricing:
                    token_share = count / embeddings.get("calls", 1)
                    model_tokens = embeddings["tokens"] * token_share
                    costs["embeddings"] += model_tokens * pricing[model]

        # Calculate chat completion costs
        chat_completions = metrics.get("chat_completions", {})
        if "prompt_tokens" in chat_completions:
            for model, count in chat_completions.get("models", {}).items():
                if model in pricing and isinstance(pricing[model], dict):
                    call_share = count / chat_completions.get("calls", 1)
                    prompt_tokens = chat_completions["prompt_tokens"] * call_share
                    completion_tokens = (
                        chat_completions["completion_tokens"] * call_share
                    )

                    model_pricing = pricing[model]
                    if isinstance(model_pricing, dict):
                        costs["chat_completions"] += (
                            prompt_tokens * model_pricing["prompt"]
                            + completion_tokens * model_pricing["completion"]
                        )

        costs["total"] = costs["embeddings"] + costs["chat_completions"]
        return costs

    def get_optimization_recommendations(self) -> list[str]:
        """Generate optimization recommendations based on usage patterns."""
        metrics = self.get_metrics()
        recommendations = []

        # Check embedding usage
        embeddings = metrics.get("embeddings", {})
        if embeddings.get("calls", 0) > 50:
            recommendations.append(
                "Consider implementing embedding caching to reduce API calls"
            )

        if embeddings.get("tokens", 0) > 10000:
            recommendations.append(
                "Consider using batch embedding generation for better efficiency"
            )

        # Check chat completion usage
        chat_completions = metrics.get("chat_completions", {})
        if chat_completions.get("calls", 0) > 20:
            recommendations.append(
                "Consider implementing query result caching to reduce chat completion calls"
            )

        avg_prompt_tokens = chat_completions.get("prompt_tokens", 0) / max(
            chat_completions.get("calls", 1), 1
        )
        if avg_prompt_tokens > 1500:
            recommendations.append(
                "Consider optimizing prompt length to reduce token usage"
            )

        avg_completion_tokens = chat_completions.get("completion_tokens", 0) / max(
            chat_completions.get("calls", 1), 1
        )
        if avg_completion_tokens > 800:
            recommendations.append(
                "Consider reducing max_tokens setting to control response length"
            )

        # Cost-based recommendations
        costs = self.get_cost_breakdown()
        if costs["total"] > 1.0:  # $1 threshold
            recommendations.append(
                "High API costs detected - review usage patterns and caching strategies"
            )

        return recommendations

    def check_rate_limits(self) -> bool:
        """Check if we're approaching rate limits."""
        current_time = time.time()
        one_minute_ago = current_time - 60

        with self._lock:
            embedding_requests = [
                ts
                for ts in self._metrics["requests"].get("embeddings", [])
                if ts > one_minute_ago
            ]
            chat_requests = [
                ts
                for ts in self._metrics["requests"].get("chat_completions", [])
                if ts > one_minute_ago
            ]

        if len(embedding_requests) > 2500:  # 80% of limit
            return True

        if len(chat_requests) > 8000:  # 80% of limit
            return True

        return False

    def get_recent_request_count(self, api_type: str, minutes: int = 1) -> int:
        """Get count of recent requests for an API type."""
        cutoff_time = time.time() - (minutes * 60)

        with self._lock:
            timestamps = self._metrics["requests"].get(api_type, [])
            recent = [ts for ts in timestamps if ts > cutoff_time]

        return len(recent)
