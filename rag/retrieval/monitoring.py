from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from django.core.cache import cache


class OpenAIUsageMonitor:
    """Monitor and optimize OpenAI API usage."""

    def __init__(self) -> None:
        """Initialize the usage monitor."""
        self.cache_prefix = "openai_usage"

    def reset_metrics(self) -> None:
        """Reset all usage metrics."""
        cache.delete(f"{self.cache_prefix}:embeddings")
        cache.delete(f"{self.cache_prefix}:chat_completions")
        cache.delete(f"{self.cache_prefix}:requests")

    def track_embedding_usage(self, tokens: int, model: str) -> None:
        """Track embedding API usage."""
        metrics = cache.get(
            f"{self.cache_prefix}:embeddings", {"calls": 0, "tokens": 0, "models": {}}
        )

        metrics["calls"] += 1
        metrics["tokens"] += tokens
        metrics["models"][model] = metrics["models"].get(model, 0) + 1

        cache.set(f"{self.cache_prefix}:embeddings", metrics, 3600)  # 1 hour

    def track_chat_completion_usage(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> None:
        """Track chat completion API usage."""
        total_tokens = prompt_tokens + completion_tokens

        metrics = cache.get(
            f"{self.cache_prefix}:chat_completions",
            {
                "calls": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "models": {},
            },
        )

        metrics["calls"] += 1
        metrics["prompt_tokens"] += prompt_tokens
        metrics["completion_tokens"] += completion_tokens
        metrics["total_tokens"] += total_tokens
        metrics["models"][model] = metrics["models"].get(model, 0) + 1

        cache.set(f"{self.cache_prefix}:chat_completions", metrics, 3600)  # 1 hour

    def track_request_timestamp(self, api_type: str) -> None:
        """Track request timestamps for rate limiting detection."""
        current_time = time.time()

        # Get existing timestamps (keep only last hour)
        cutoff_time = current_time - 3600  # 1 hour ago
        timestamps = cache.get(f"{self.cache_prefix}:requests:{api_type}", [])

        # Filter out old timestamps and add new one
        timestamps = [ts for ts in timestamps if ts > cutoff_time]
        timestamps.append(current_time)

        cache.set(f"{self.cache_prefix}:requests:{api_type}", timestamps, 3600)

    def get_metrics(self) -> dict[str, Any]:
        """Get current usage metrics."""
        embeddings = cache.get(f"{self.cache_prefix}:embeddings", {})
        chat_completions = cache.get(f"{self.cache_prefix}:chat_completions", {})

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
        # Check recent request patterns
        current_time = time.time()

        # Check embeddings rate (3000 RPM for text-embedding-3-small)
        embedding_timestamps = cache.get(f"{self.cache_prefix}:requests:embeddings", [])
        recent_embeddings = [
            ts
            for ts in embedding_timestamps
            if ts > current_time - 60  # last minute
        ]

        if len(recent_embeddings) > 2500:  # 80% of limit
            return True

        # Check chat completions rate (10000 RPM for gpt-4o-mini)
        chat_timestamps = cache.get(
            f"{self.cache_prefix}:requests:chat_completions", []
        )
        recent_chat = [
            ts
            for ts in chat_timestamps
            if ts > current_time - 60  # last minute
        ]

        if len(recent_chat) > 8000:  # 80% of limit
            return True

        return False

    def get_recent_request_count(self, api_type: str, minutes: int = 1) -> int:
        """Get count of recent requests for an API type."""
        current_time = time.time()
        cutoff_time = current_time - (minutes * 60)

        timestamps = cache.get(f"{self.cache_prefix}:requests:{api_type}", [])
        recent_timestamps = [ts for ts in timestamps if ts > cutoff_time]

        return len(recent_timestamps)
