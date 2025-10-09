"""
Main benchmark runner to compare Regular Agent vs Code Mode Agent.
"""

import os
import json
import time
from dotenv import load_dotenv
from typing import List, Dict, Any
import random

from agents import AgentFactory
from tools import get_tools, get_tool_schemas, get_code_mode_api, get_state
from test_scenarios import get_scenarios, validate_scenario_result


class Benchmark:
    """Benchmark runner for comparing agents."""

    def __init__(self, model: str = "claude", api_keys: dict = None):
        """
        Initialize the benchmark.

        Args:
            model: Model to use ("claude" or "gemini")
            api_keys: Dictionary of API keys for different models
        """
        self.model = model
        self.api_keys = api_keys or {}
        self.tools = get_tools()
        self.tool_schemas = get_tool_schemas()
        self.code_mode_api = get_code_mode_api()

        # Get the required API key
        required_key_env = AgentFactory.get_required_api_key_env(model)
        if model not in self.api_keys:
            raise ValueError(
                f"API key for {model} not provided. "
                f"Please set {required_key_env} in environment or pass via api_keys"
            )
        self.api_key = self.api_keys[model]

    def run_single_test(self, agent_type: str, query: str, scenario_id: int = None) -> Dict[str, Any]:
        """
        Run a single test with the specified agent.

        Args:
            agent_type: 'regular' or 'codemode'
            query: The test query
            scenario_id: Optional scenario ID for validation

        Returns:
            Test result dictionary
        """
        # Reset state before each test
        state = get_state()
        state.reset()

        start_time = time.time()

        try:
            # Create agent using factory
            if agent_type == "regular":
                agent = AgentFactory.create_agent(
                    model=self.model,
                    mode="regular",
                    api_key=self.api_key,
                    tools=self.tools,
                    tool_schemas=self.tool_schemas
                )
            else:
                agent = AgentFactory.create_agent(
                    model=self.model,
                    mode="codemode",
                    api_key=self.api_key,
                    tools=self.tools,
                    tools_api=self.code_mode_api
                )

            # Use higher max_iterations for complex scenarios (20 to handle edge cases)
            result = agent.run(query, max_iterations=20)
            execution_time = time.time() - start_time

            # Get final state
            final_state = state.get_summary()

            # Validate state if scenario_id is provided
            validation = None
            if scenario_id:
                validation = validate_scenario_result(scenario_id, final_state)

            return {
                **result,
                "execution_time": execution_time,
                "agent_type": agent_type,
                "final_state": final_state,
                "validation": validation
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "agent_type": agent_type
            }

    def run_benchmark(self, scenarios: List[Dict[str, Any]] = None, limit: int = None) -> Dict[str, Any]:
        """
        Run the full benchmark.

        Args:
            scenarios: List of test scenarios (uses get_scenarios() if None)
            limit: Optional limit on number of scenarios to run

        Returns:
            Benchmark results
        """
        if scenarios is None:
            scenarios = get_scenarios()

        if limit:
            scenarios = scenarios[:limit]

        results = {
            "regular_agent": [],
            "codemode_agent": []
        }

        model_info = AgentFactory.get_model_info(self.model)
        print("=" * 80)
        print(f"BENCHMARK: Regular Agent vs Code Mode Agent")
        print(f"Model: {model_info['name']}")
        print("=" * 80)
        print()

        for test_case in scenarios:
            print(f"Scenario {test_case['id']}: {test_case['name']}")
            print(f"Description: {test_case['description']}")
            print(f"Query: {test_case['query'][:100]}...")
            print("-" * 80)

            # Test Regular Agent
            print("Running Regular Agent...")
            regular_result = self.run_single_test("regular", test_case['query'], test_case['id'])
            results["regular_agent"].append({
                "test_id": test_case['id'],
                "name": test_case['name'],
                "query": test_case['query'],
                "description": test_case['description'],
                **regular_result
            })
            print(f"  Time: {regular_result['execution_time']:.2f}s")
            print(f"  Iterations: {regular_result.get('iterations', 'N/A')}")
            print(f"  Input tokens: {regular_result.get('input_tokens', 'N/A')}")
            print(f"  Output tokens: {regular_result.get('output_tokens', 'N/A')}")

            # Print validation results
            if regular_result.get('validation'):
                val = regular_result['validation']
                print(f"  Validation: {'✓ PASS' if val['valid'] else '✗ FAIL'} ({val['passed']}/{val['total_checks']} checks)")
            print()

            # Test Code Mode Agent
            print("Running Code Mode Agent...")
            # Add delay to avoid rate limits (with jitter to prevent synchronized requests)
            time.sleep(2 + random.uniform(0, 1))
            codemode_result = self.run_single_test("codemode", test_case['query'], test_case['id'])
            results["codemode_agent"].append({
                "test_id": test_case['id'],
                "name": test_case['name'],
                "query": test_case['query'],
                "description": test_case['description'],
                **codemode_result
            })
            print(f"  Time: {codemode_result['execution_time']:.2f}s")
            print(f"  Iterations: {codemode_result.get('iterations', 'N/A')}")
            print(f"  Input tokens: {codemode_result.get('input_tokens', 'N/A')}")
            print(f"  Output tokens: {codemode_result.get('output_tokens', 'N/A')}")

            # Print validation results
            if codemode_result.get('validation'):
                val = codemode_result['validation']
                print(f"  Validation: {'✓ PASS' if val['valid'] else '✗ FAIL'} ({val['passed']}/{val['total_checks']} checks)")
            print()
            print("=" * 80)
            print()

            # Add delay between scenarios to avoid rate limits
            if test_case != scenarios[-1]:  # Don't delay after last scenario
                print("Waiting to avoid rate limits...")
                time.sleep(3 + random.uniform(0, 2))
                print()

        # Calculate summary statistics
        summary = self._calculate_summary(results)
        self._print_summary(summary)

        return {
            "results": results,
            "summary": summary
        }

    def _calculate_summary(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        summary = {}

        for agent_type in ["regular_agent", "codemode_agent"]:
            agent_results = results[agent_type]
            successful = [r for r in agent_results if r.get("success", False)]

            # Calculate validation stats
            validated = [r for r in agent_results if r.get("validation")]
            validation_passed = [r for r in validated if r.get("validation", {}).get("valid", False)]

            if successful:
                summary[agent_type] = {
                    "total_tests": len(agent_results),
                    "successful_tests": len(successful),
                    "validated_tests": len(validated),
                    "validation_passed": len(validation_passed),
                    "validation_rate": len(validation_passed) / len(validated) if validated else 0,
                    "avg_execution_time": sum(r["execution_time"] for r in successful) / len(successful),
                    "avg_iterations": sum(r.get("iterations", 0) for r in successful) / len(successful),
                    "total_input_tokens": sum(r.get("input_tokens", 0) for r in successful),
                    "total_output_tokens": sum(r.get("output_tokens", 0) for r in successful),
                    "avg_input_tokens": sum(r.get("input_tokens", 0) for r in successful) / len(successful),
                    "avg_output_tokens": sum(r.get("output_tokens", 0) for r in successful) / len(successful),
                }
            else:
                summary[agent_type] = {
                    "total_tests": len(agent_results),
                    "successful_tests": 0,
                    "validated_tests": len(validated),
                    "validation_passed": len(validation_passed),
                    "validation_rate": 0,
                }

        return summary

    def _print_summary(self, summary: Dict[str, Any]):
        """Print benchmark summary."""
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()

        for agent_type, stats in summary.items():
            agent_name = "Regular Agent" if agent_type == "regular_agent" else "Code Mode Agent"
            print(f"{agent_name}:")
            print(f"  Successful: {stats['successful_tests']}/{stats['total_tests']}")
            print(f"  Validation: {stats['validation_passed']}/{stats['validated_tests']} passed ({stats['validation_rate']*100:.1f}%)")

            if stats['successful_tests'] > 0:
                print(f"  Avg Execution Time: {stats['avg_execution_time']:.2f}s")
                print(f"  Avg Iterations: {stats['avg_iterations']:.2f}")
                print(f"  Total Input Tokens: {stats['total_input_tokens']}")
                print(f"  Total Output Tokens: {stats['total_output_tokens']}")
                print(f"  Avg Input Tokens: {stats['avg_input_tokens']:.2f}")
                print(f"  Avg Output Tokens: {stats['avg_output_tokens']:.2f}")

            print()

        # Compare performance
        if summary["regular_agent"]["successful_tests"] > 0 and summary["codemode_agent"]["successful_tests"] > 0:
            print("Comparison:")

            time_diff = ((summary["codemode_agent"]["avg_execution_time"] - summary["regular_agent"]["avg_execution_time"])
                        / summary["regular_agent"]["avg_execution_time"] * 100)
            print(f"  Code Mode is {time_diff:+.1f}% vs Regular in execution time")

            token_diff = ((summary["codemode_agent"]["total_input_tokens"] + summary["codemode_agent"]["total_output_tokens"]) -
                         (summary["regular_agent"]["total_input_tokens"] + summary["regular_agent"]["total_output_tokens"]))
            print(f"  Token difference: {token_diff:+d} (Code Mode vs Regular)")

            print()

    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save benchmark results to a file."""
        if filename is None:
            filename = f"benchmark_results_{self.model}.json"

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run Code Mode benchmark")
    parser.add_argument("--limit", type=int, help="Limit number of scenarios to run")
    parser.add_argument("--scenario", type=int, help="Run only a specific scenario ID")
    parser.add_argument(
        "--model",
        type=str,
        default="claude",
        choices=AgentFactory.get_supported_models(),
        help="Model to use for benchmark"
    )
    args = parser.parse_args()

    load_dotenv()

    # Get API keys for all supported models
    api_keys = {}
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    if claude_key:
        api_keys["claude"] = claude_key

    gemini_key = os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        api_keys["gemini"] = gemini_key

    # Check if the required key is available
    if args.model not in api_keys:
        required_env = AgentFactory.get_required_api_key_env(args.model)
        print(f"Error: {required_env} not found in environment")
        print(f"Please create a .env file with your API key:")
        print(f"  {required_env}=your_key_here")
        return

    try:
        benchmark = Benchmark(model=args.model, api_keys=api_keys)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Select scenarios
    scenarios = None
    if args.scenario:
        from test_scenarios import get_scenario_by_id
        scenario = get_scenario_by_id(args.scenario)
        if scenario:
            scenarios = [scenario]
        else:
            print(f"Error: Scenario {args.scenario} not found")
            return

    results = benchmark.run_benchmark(scenarios=scenarios, limit=args.limit)

    # Save results
    benchmark.save_results(results)


if __name__ == "__main__":
    main()
