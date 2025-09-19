"""Performance benchmarking utilities for RAG system."""

from __future__ import annotations

import concurrent.futures
import statistics
import time
from typing import Any, TypedDict

import psutil

from rag.retrieval.rag import RAGService


class SingleQueryResult(TypedDict):
    """Result structure for single query performance test."""

    response_time: float
    success: bool
    error: str | None


class ConcurrentQueryResult(TypedDict):
    """Result structure for concurrent query performance test."""

    query: str
    response_time: float
    success: bool
    error: str | None


class LoadTestResult(TypedDict):
    """Result structure for load test performance."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    response_times: list[float]


class MemoryUsageResult(TypedDict):
    """Result structure for memory usage measurement."""

    baseline_memory_mb: float
    peak_memory_mb: float
    memory_delta_mb: float


class PerformanceReport(TypedDict):
    """Comprehensive performance report structure."""

    summary: dict[str, Any]
    requirements_met: dict[str, bool]
    detailed_results: dict[str, Any]
    recommendations: list[str]


class PerformanceBenchmark:
    """Performance benchmarking utilities for RAG system."""

    def __init__(self) -> None:
        """Initialize performance benchmark."""
        self.three_second_threshold = 3.0

    def measure_response_time(
        self, rag_service: RAGService, query: str, topic_ids: list[int]
    ) -> float:
        """Measure response time for a single RAG query."""
        start_time = time.time()

        try:
            rag_service.query(query=query, topic_ids=topic_ids)
            return time.time() - start_time
        except Exception:
            # Return time even if query failed to measure system overhead
            return time.time() - start_time

    def run_single_query_benchmark(
        self, rag_service: RAGService, query: str, topic_ids: list[int]
    ) -> SingleQueryResult:
        """Run benchmark for a single query and return detailed results."""
        start_time = time.time()
        error = None
        success = True

        try:
            rag_service.query(query=query, topic_ids=topic_ids)
        except Exception as e:
            success = False
            error = str(e)

        response_time = time.time() - start_time

        return {
            "response_time": response_time,
            "success": success,
            "error": error,
        }

    def run_concurrent_benchmark(
        self,
        rag_service: RAGService,
        queries: list[str],
        topic_ids: list[int],
        concurrent_users: int = 3,
    ) -> list[ConcurrentQueryResult]:
        """Run concurrent queries to test system under multi-user load."""

        def execute_query(query: str) -> ConcurrentQueryResult:
            start_time = time.time()
            success = True
            error = None

            try:
                rag_service.query(query=query, topic_ids=topic_ids)
            except Exception as e:
                success = False
                error = str(e)

            response_time = time.time() - start_time

            return {
                "query": query,
                "response_time": response_time,
                "success": success,
                "error": error,
            }

        # Use ThreadPoolExecutor to simulate concurrent users
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrent_users
        ) as executor:
            # Submit all queries concurrently
            future_to_query = {
                executor.submit(execute_query, query): query for query in queries
            }

            results = []
            for future in concurrent.futures.as_completed(future_to_query):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Handle any executor-level errors
                    query = future_to_query[future]
                    results.append(
                        {
                            "query": query,
                            "response_time": 0.0,
                            "success": False,
                            "error": str(e),
                        }
                    )

        return results

    def run_load_test(
        self,
        rag_service: RAGService,
        query: str,
        topic_ids: list[int],
        num_requests: int = 50,
        duration_seconds: int = 30,
    ) -> LoadTestResult:
        """Run sustained load test to measure system performance under stress."""
        response_times: list[float] = []
        successful_requests = 0
        failed_requests = 0
        start_test_time = time.time()

        def execute_single_request() -> tuple[float, bool]:
            start_time = time.time()
            try:
                rag_service.query(query=query, topic_ids=topic_ids)
                return time.time() - start_time, True
            except Exception:
                return time.time() - start_time, False

        # Run requests for specified duration or until num_requests is reached
        request_count = 0
        while (
            request_count < num_requests
            and (time.time() - start_test_time) < duration_seconds
        ):
            response_time, success = execute_single_request()
            response_times.append(response_time)

            if success:
                successful_requests += 1
            else:
                failed_requests += 1

            request_count += 1

        total_test_time = time.time() - start_test_time
        total_requests = len(response_times)

        # Calculate statistics
        avg_response_time = statistics.mean(response_times) if response_times else 0.0

        # Calculate percentiles safely
        if len(response_times) >= 2:
            sorted_times = sorted(response_times)
            p95_index = int(0.95 * len(sorted_times))
            p99_index = int(0.99 * len(sorted_times))
            p95_response_time = sorted_times[min(p95_index, len(sorted_times) - 1)]
            p99_response_time = sorted_times[min(p99_index, len(sorted_times) - 1)]
        elif response_times:
            # If only one data point, use it for both percentiles
            p95_response_time = response_times[0]
            p99_response_time = response_times[0]
        else:
            p95_response_time = 0.0
            p99_response_time = 0.0
        requests_per_second = (
            total_requests / total_test_time if total_test_time > 0 else 0.0
        )

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time,
            "requests_per_second": requests_per_second,
            "response_times": response_times,
        }

    def measure_memory_usage(
        self, rag_service: RAGService, query: str, topic_ids: list[int]
    ) -> MemoryUsageResult:
        """Measure memory usage during RAG query execution."""
        process = psutil.Process()

        # Get baseline memory usage
        baseline_memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB

        # Execute query and monitor peak memory
        peak_memory = baseline_memory

        try:
            # Monitor memory during query execution
            rag_service.query(query=query, topic_ids=topic_ids)

            # Sample memory usage (simplified approach)
            current_memory = process.memory_info().rss / (1024 * 1024)
            peak_memory = max(peak_memory, current_memory)

        except Exception:
            # Still measure memory even if query fails
            current_memory = process.memory_info().rss / (1024 * 1024)
            peak_memory = max(peak_memory, current_memory)

        memory_delta = peak_memory - baseline_memory

        return {
            "baseline_memory_mb": baseline_memory,
            "peak_memory_mb": peak_memory,
            "memory_delta_mb": memory_delta,
        }

    def run_benchmarks(
        self,
        rag_service: RAGService,
        test_queries: list[str],
        topic_ids: list[int],
        include_load_test: bool = True,
        include_memory_test: bool = True,
    ) -> dict[str, Any]:
        """Run comprehensive performance benchmarks."""
        results: dict[str, Any] = {}

        # Single query benchmark
        if test_queries:
            single_result = self.run_single_query_benchmark(
                rag_service, test_queries[0], topic_ids
            )
            results["single_query"] = single_result

        # Concurrent queries benchmark
        if len(test_queries) >= 3:
            concurrent_results = self.run_concurrent_benchmark(
                rag_service, test_queries[:3], topic_ids, concurrent_users=3
            )
            results["concurrent_queries"] = {
                "results": concurrent_results,
                "avg_response_time": statistics.mean(
                    [r["response_time"] for r in concurrent_results]
                ),
                "max_response_time": max(
                    [r["response_time"] for r in concurrent_results]
                ),
                "success_rate": sum([1 for r in concurrent_results if r["success"]])
                / len(concurrent_results),
            }

        # Load test (optional, can be resource intensive)
        if include_load_test and test_queries:
            load_results = self.run_load_test(
                rag_service,
                test_queries[0],
                topic_ids,
                num_requests=20,
                duration_seconds=10,
            )
            results["load_test"] = load_results

        # Memory usage test
        if include_memory_test and test_queries:
            memory_results = self.measure_memory_usage(
                rag_service, test_queries[0], topic_ids
            )
            results["memory_usage"] = memory_results

        return results

    def generate_performance_report(
        self, benchmark_results: dict[str, Any]
    ) -> PerformanceReport:
        """Generate comprehensive performance report from benchmark results."""
        summary: dict[str, Any] = {}
        requirements_met: dict[str, bool] = {}
        recommendations: list[str] = []

        # Analyze single query performance
        single_query = benchmark_results.get("single_query", {})
        single_response_time = single_query.get("response_time", float("inf"))
        single_success = single_query.get("success", False)

        summary["single_query_response_time"] = single_response_time
        summary["single_query_success"] = single_success

        # Check 3-second requirement for single queries
        three_second_met = (
            single_response_time < self.three_second_threshold and single_success
        )
        requirements_met["three_second_response_time"] = three_second_met
        summary["response_time_requirement_met"] = three_second_met

        if not three_second_met:
            recommendations.append(
                f"Single query response time ({single_response_time:.2f}s) exceeds 3-second requirement"
            )

        # Analyze concurrent performance
        concurrent_data = benchmark_results.get("concurrent_queries", {})
        if concurrent_data:
            concurrent_avg = concurrent_data.get("avg_response_time", float("inf"))
            concurrent_max = concurrent_data.get("max_response_time", float("inf"))
            concurrent_success_rate = concurrent_data.get("success_rate", 0.0)

            summary["concurrent_avg_response_time"] = concurrent_avg
            summary["concurrent_max_response_time"] = concurrent_max
            summary["concurrent_success_rate"] = concurrent_success_rate

            concurrent_performance_ok = (
                concurrent_avg < self.three_second_threshold
                and concurrent_success_rate > 0.95
            )
            requirements_met["concurrent_user_support"] = concurrent_performance_ok

            if not concurrent_performance_ok:
                recommendations.append(
                    f"Concurrent performance needs improvement: avg={concurrent_avg:.2f}s, "
                    f"success_rate={concurrent_success_rate:.2%}"
                )

        # Analyze load test performance
        load_data = benchmark_results.get("load_test", {})
        if load_data:
            load_avg = load_data.get("avg_response_time", float("inf"))
            load_p95 = load_data.get("p95_response_time", float("inf"))
            load_rps = load_data.get("requests_per_second", 0.0)
            load_success_rate = load_data.get("successful_requests", 0) / load_data.get(
                "total_requests", 1
            )

            summary["load_avg_response_time"] = load_avg
            summary["load_p95_response_time"] = load_p95
            summary["load_requests_per_second"] = load_rps
            summary["load_success_rate"] = load_success_rate

            if load_p95 >= self.three_second_threshold:
                recommendations.append(
                    f"95th percentile response time ({load_p95:.2f}s) approaches 3-second limit"
                )

        # Analyze memory usage
        memory_data = benchmark_results.get("memory_usage", {})
        if memory_data:
            memory_delta = memory_data.get("memory_delta_mb", 0.0)
            peak_memory = memory_data.get("peak_memory_mb", 0.0)

            summary["memory_delta_mb"] = memory_delta
            summary["peak_memory_mb"] = peak_memory

            # Consider memory efficient if delta is reasonable
            memory_efficient = memory_delta < 100.0  # Less than 100MB increase
            requirements_met["memory_efficiency"] = memory_efficient

            if not memory_efficient:
                recommendations.append(
                    f"Memory usage increase ({memory_delta:.1f}MB) may indicate memory leaks"
                )

        # Calculate overall performance score
        requirement_scores = [1.0 if met else 0.0 for met in requirements_met.values()]
        overall_score = (
            statistics.mean(requirement_scores) if requirement_scores else 0.0
        )
        summary["overall_performance_score"] = overall_score

        # Identify bottlenecks
        bottlenecks = []
        if single_response_time > 2.0:
            bottlenecks.append("Single query latency")
        if concurrent_data and concurrent_data.get("avg_response_time", 0) > 2.5:
            bottlenecks.append("Concurrent query handling")
        if load_data and load_data.get("p95_response_time", 0) > 2.5:
            bottlenecks.append("Load handling capacity")

        summary["bottlenecks_identified"] = bottlenecks

        # Add general recommendations
        if overall_score < 0.8:
            recommendations.append(
                "Consider implementing caching to improve response times"
            )
            recommendations.append("Review database query optimization opportunities")
            recommendations.append("Consider scaling external API connections")

        return {
            "summary": summary,
            "requirements_met": requirements_met,
            "detailed_results": benchmark_results,
            "recommendations": recommendations,
        }
