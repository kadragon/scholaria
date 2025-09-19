"""Django management command to run performance benchmarks."""

from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from rag.models import Topic
from rag.retrieval.rag import RAGService
from rag.tests.performance_benchmarks import PerformanceBenchmark, PerformanceReport


class Command(BaseCommand):
    """Run performance benchmarks for the RAG system."""

    help = "Run performance benchmarks to validate < 3 second response time requirement"

    def add_arguments(self, parser: Any) -> None:
        """Add command line arguments."""
        parser.add_argument(
            "--topic-id",
            type=int,
            help="Topic ID to test against (defaults to first available topic)",
        )
        parser.add_argument(
            "--queries",
            nargs="+",
            default=[
                "What is machine learning?",
                "Explain neural networks",
                "How do algorithms work?",
            ],
            help="Test queries to run (space-separated)",
        )
        parser.add_argument(
            "--include-load-test",
            action="store_true",
            default=False,
            help="Include load testing (can be resource intensive)",
        )
        parser.add_argument(
            "--output-file",
            type=str,
            help="Save detailed results to JSON file",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            default=False,
            help="Show detailed output",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        # Get topic to test against
        topic_id = options.get("topic_id")
        topic: Topic
        if topic_id:
            try:
                topic = Topic.objects.get(id=topic_id)
                topic_ids = [topic.id]
            except Topic.DoesNotExist as e:
                raise CommandError(f"Topic with ID {topic_id} does not exist") from e
        else:
            # Use first available topic
            first_topic = Topic.objects.first()
            if first_topic is None:
                raise CommandError("No topics found in database")
            topic = first_topic
            topic_ids = [topic.id]

        if options["verbose"]:
            self.stdout.write(f"Running benchmarks against topic: {topic.name}")

        # Initialize benchmark and RAG service
        benchmark = PerformanceBenchmark()
        rag_service = RAGService()

        # Get test queries
        test_queries = options.get("queries", [])
        if not test_queries:
            test_queries = ["What is machine learning?"]

        if options["verbose"]:
            self.stdout.write(f"Test queries: {test_queries}")

        try:
            # Run benchmarks
            self.stdout.write(self.style.SUCCESS("Starting performance benchmarks..."))

            results = benchmark.run_benchmarks(
                rag_service=rag_service,
                test_queries=test_queries,
                topic_ids=topic_ids,
                include_load_test=options.get("include_load_test", False),
                include_memory_test=True,
            )

            # Generate performance report
            report = benchmark.generate_performance_report(results)

            # Display summary
            self._display_summary(report, options["verbose"])

            # Save detailed results if requested
            output_file = options.get("output_file")
            if output_file:
                self._save_results(report, output_file)
                self.stdout.write(
                    self.style.SUCCESS(f"Detailed results saved to {output_file}")
                )

        except Exception as e:
            raise CommandError(f"Benchmark failed: {str(e)}") from e

    def _display_summary(
        self, report: PerformanceReport, verbose: bool = False
    ) -> None:
        """Display benchmark summary."""
        summary = report["summary"]
        requirements = report["requirements_met"]

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("PERFORMANCE BENCHMARK RESULTS"))
        self.stdout.write("=" * 60)

        # Overall score
        score = summary.get("overall_performance_score", 0.0)
        score_style = (
            self.style.SUCCESS
            if score >= 0.8
            else self.style.WARNING
            if score >= 0.6
            else self.style.ERROR
        )
        self.stdout.write(f"Overall Performance Score: {score_style(f'{score:.1%}')}")

        # Response time requirements
        three_sec_met = requirements.get("three_second_response_time", False)
        three_sec_style = self.style.SUCCESS if three_sec_met else self.style.ERROR
        self.stdout.write(
            f"3-Second Requirement Met: {three_sec_style(str(three_sec_met))}"
        )

        # Single query performance
        single_time = summary.get("single_query_response_time", 0.0)
        single_style = self.style.SUCCESS if single_time < 3.0 else self.style.ERROR
        self.stdout.write(
            f"Single Query Response Time: {single_style(f'{single_time:.2f}s')}"
        )

        # Concurrent performance (if available)
        if "concurrent_avg_response_time" in summary:
            concurrent_time = summary["concurrent_avg_response_time"]
            concurrent_style = (
                self.style.SUCCESS if concurrent_time < 3.0 else self.style.ERROR
            )
            self.stdout.write(
                f"Concurrent Avg Response Time: {concurrent_style(f'{concurrent_time:.2f}s')}"
            )

        # Load test performance (if available)
        if "load_avg_response_time" in summary:
            load_avg = summary["load_avg_response_time"]
            load_p95 = summary.get("load_p95_response_time", 0.0)
            load_style = self.style.SUCCESS if load_p95 < 3.0 else self.style.WARNING
            self.stdout.write(
                f"Load Test Avg: {load_avg:.2f}s, P95: {load_style(f'{load_p95:.2f}s')}"
            )

        # Memory usage (if available)
        if "memory_delta_mb" in summary:
            memory_delta = summary["memory_delta_mb"]
            memory_style = (
                self.style.SUCCESS
                if memory_delta < 50
                else self.style.WARNING
                if memory_delta < 100
                else self.style.ERROR
            )
            self.stdout.write(
                f"Memory Usage Increase: {memory_style(f'{memory_delta:.1f}MB')}"
            )

        # Bottlenecks
        bottlenecks = summary.get("bottlenecks_identified", [])
        if bottlenecks:
            self.stdout.write(f"\n{self.style.WARNING('Bottlenecks Identified:')}")
            for bottleneck in bottlenecks:
                self.stdout.write(f"  - {bottleneck}")

        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            self.stdout.write(f"\n{self.style.WARNING('Recommendations:')}")
            for rec in recommendations:
                self.stdout.write(f"  - {rec}")

        if verbose:
            self.stdout.write(f"\n{self.style.SUCCESS('Detailed Requirements:')}")
            for requirement, met in requirements.items():
                status = self.style.SUCCESS("✓") if met else self.style.ERROR("✗")
                self.stdout.write(f"  {status} {requirement.replace('_', ' ').title()}")

    def _save_results(self, report: PerformanceReport, output_file: str) -> None:
        """Save detailed results to JSON file."""
        try:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2, default=str)
        except Exception as e:
            raise CommandError(f"Failed to save results: {str(e)}") from e
