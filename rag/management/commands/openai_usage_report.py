from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand

from rag.retrieval.monitoring import OpenAIUsageMonitor


class Command(BaseCommand):
    """Django management command to generate OpenAI API usage reports."""

    help = (
        "Generate OpenAI API usage report with costs and optimization recommendations"
    )

    def add_arguments(self, parser: Any) -> None:
        """Add command line arguments."""
        parser.add_argument(
            "--format",
            choices=["text", "json"],
            default="text",
            help="Output format (default: text)",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset usage metrics after generating report",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the management command."""
        monitor = OpenAIUsageMonitor()

        # Get usage metrics
        metrics = monitor.get_metrics()
        costs = monitor.get_cost_breakdown()
        recommendations = monitor.get_optimization_recommendations()

        if options["format"] == "json":
            self._output_json(metrics, costs, recommendations)
        else:
            self._output_text(metrics, costs, recommendations)

        # Reset metrics if requested
        if options["reset"]:
            monitor.reset_metrics()
            self.stdout.write(self.style.SUCCESS("Usage metrics have been reset."))

    def _output_text(
        self,
        metrics: dict[str, Any],
        costs: dict[str, float],
        recommendations: list[str],
    ) -> None:
        """Output report in human-readable text format."""
        self.stdout.write(self.style.SUCCESS("OpenAI API Usage Report"))
        self.stdout.write("=" * 50)

        # Embeddings usage
        embeddings = metrics.get("embeddings", {})
        if embeddings:
            self.stdout.write("\n📊 Embeddings API Usage:")
            self.stdout.write(f"  • Total calls: {embeddings.get('calls', 0)}")
            self.stdout.write(f"  • Total tokens: {embeddings.get('tokens', 0):,}")

            models = embeddings.get("models", {})
            if models:
                self.stdout.write("  • Models used:")
                for model, count in models.items():
                    self.stdout.write(f"    - {model}: {count} calls")

        # Chat completions usage
        chat_completions = metrics.get("chat_completions", {})
        if chat_completions:
            self.stdout.write("\n💬 Chat Completions API Usage:")
            self.stdout.write(f"  • Total calls: {chat_completions.get('calls', 0)}")
            self.stdout.write(
                f"  • Prompt tokens: {chat_completions.get('prompt_tokens', 0):,}"
            )
            self.stdout.write(
                f"  • Completion tokens: {chat_completions.get('completion_tokens', 0):,}"
            )
            self.stdout.write(
                f"  • Total tokens: {chat_completions.get('total_tokens', 0):,}"
            )

            models = chat_completions.get("models", {})
            if models:
                self.stdout.write("  • Models used:")
                for model, count in models.items():
                    self.stdout.write(f"    - {model}: {count} calls")

        # Cost breakdown
        if any(costs.values()):
            self.stdout.write("\n💰 Cost Breakdown (Estimated):")
            self.stdout.write(f"  • Embeddings: ${costs.get('embeddings', 0):.4f}")
            self.stdout.write(
                f"  • Chat Completions: ${costs.get('chat_completions', 0):.4f}"
            )
            self.stdout.write(f"  • Total: ${costs.get('total', 0):.4f}")

        # Rate limiting check
        monitor = OpenAIUsageMonitor()
        if monitor.check_rate_limits():
            self.stdout.write(
                self.style.WARNING("\n⚠️  Rate limiting threshold approached!")
            )

        # Optimization recommendations
        if recommendations:
            self.stdout.write("\n🚀 Optimization Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                self.stdout.write(f"  {i}. {rec}")
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "\n✅ No optimization recommendations - usage looks good!"
                )
            )

        self.stdout.write(f"\n📅 Report generated: {metrics.get('timestamp', 'N/A')}")

    def _output_json(
        self,
        metrics: dict[str, Any],
        costs: dict[str, float],
        recommendations: list[str],
    ) -> None:
        """Output report in JSON format."""
        report = {
            "metrics": metrics,
            "costs": costs,
            "recommendations": recommendations,
            "rate_limit_warning": OpenAIUsageMonitor().check_rate_limits(),
        }

        self.stdout.write(json.dumps(report, indent=2))
