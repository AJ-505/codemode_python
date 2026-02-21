"""
Main benchmark runner to compare Regular Agent vs Code Mode Agent.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

from agents import AgentFactory
from sandbox.executor import CodeExecutor
from tools import (
    get_tools,
    get_tool_schemas,
    get_code_mode_api_compact,
    get_state,
    load_mcp_tools_from_file,
    mcp_tools_to_anthropic_schemas,
    mcp_tools_to_code_mode_api,
)

try:
    from test_scenarios import get_scenarios, get_scenario_by_id, validate_scenario_result
except ImportError:
    from tests.test_scenarios import get_scenarios, get_scenario_by_id, validate_scenario_result


def _estimate_tokens_from_text(text: str) -> int:
    """
    Lightweight prompt token estimate.
    Approximation: 1 token ~= 4 chars for English/JSON-heavy payloads.
    """
    return max(1, len(text) // 4)


class Benchmark:
    """Benchmark runner for comparing agents."""

    def __init__(self, model: str = "claude", api_keys: Optional[Dict[str, str]] = None, mcp_tools: Optional[List[Dict[str, Any]]] = None):
        self.model = model
        self.api_keys = api_keys or {}
        self.tools = get_tools()

        if mcp_tools:
            self.tool_schemas = mcp_tools_to_anthropic_schemas(mcp_tools)
            self.code_mode_api = mcp_tools_to_code_mode_api(mcp_tools)
        else:
            self.tool_schemas = get_tool_schemas()
            self.code_mode_api = get_code_mode_api_compact()

        required_key_env = AgentFactory.get_required_api_key_env(model)
        if model not in self.api_keys:
            raise ValueError(
                f"API key for {model} not provided. "
                f"Please set {required_key_env} in environment or pass via api_keys"
            )
        self.api_key = self.api_keys[model]

    def _build_prompt_footprint_metrics(self) -> Dict[str, Any]:
        regular_schema_text = json.dumps(self.tool_schemas, separators=(",", ":"), ensure_ascii=False)
        code_mode_api_text = self.code_mode_api
        return {
            "regular_tools_prompt_chars": len(regular_schema_text),
            "regular_tools_prompt_tokens_est": _estimate_tokens_from_text(regular_schema_text),
            "codemode_api_prompt_chars": len(code_mode_api_text),
            "codemode_api_prompt_tokens_est": _estimate_tokens_from_text(code_mode_api_text),
        }

    def _extract_sandbox_metrics(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        executions = agent_result.get("code_executions", [])
        sandbox_runs = []
        total_tool_calls = 0
        for execution in executions:
            execution_result = execution.get("execution_result", {})
            if isinstance(execution_result, dict) and "sandbox" in execution_result:
                sandbox_runs.append(execution_result["sandbox"])
                total_tool_calls += len(execution_result.get("tool_calls", []))

        if not sandbox_runs:
            return {}

        compile_times = [x.get("compile_ms", 0.0) for x in sandbox_runs]
        execution_times = [x.get("execution_ms", 0.0) for x in sandbox_runs]
        total_times = [x.get("total_ms", 0.0) for x in sandbox_runs]
        return {
            "runs": len(sandbox_runs),
            "total_tool_calls": total_tool_calls,
            "avg_compile_ms": sum(compile_times) / len(compile_times),
            "avg_execution_ms": sum(execution_times) / len(execution_times),
            "avg_total_ms": sum(total_times) / len(total_times),
        }

    def run_single_test(self, agent_type: str, query: str, scenario_id: Optional[int] = None) -> Dict[str, Any]:
        state = get_state()
        state.reset()
        start_time = time.time()

        try:
            if agent_type == "regular":
                agent = AgentFactory.create_agent(
                    model=self.model,
                    mode="regular",
                    api_key=self.api_key,
                    tools=self.tools,
                    tool_schemas=self.tool_schemas,
                )
            else:
                agent = AgentFactory.create_agent(
                    model=self.model,
                    mode="codemode",
                    api_key=self.api_key,
                    tools=self.tools,
                    tools_api=self.code_mode_api,
                )

            result = agent.run(query, max_iterations=20)
            execution_time = time.time() - start_time
            final_state = state.get_summary()

            validation = None
            if scenario_id:
                validation = validate_scenario_result(scenario_id, final_state)

            payload = {
                **result,
                "execution_time": execution_time,
                "agent_type": agent_type,
                "final_state": final_state,
                "validation": validation,
            }

            if agent_type == "codemode":
                payload["sandbox_metrics"] = self._extract_sandbox_metrics(result)

            return payload
        except Exception as exc:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(exc),
                "execution_time": execution_time,
                "agent_type": agent_type,
            }

    def run_benchmark(self, scenarios: Optional[List[Dict[str, Any]]] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        if scenarios is None:
            scenarios = get_scenarios()

        if limit:
            scenarios = scenarios[:limit]

        results = {"regular_agent": [], "codemode_agent": []}
        model_info = AgentFactory.get_model_info(self.model)

        print("=" * 80)
        print("BENCHMARK: Regular Agent vs Code Mode Agent")
        print(f"Model: {model_info['name']}")
        print("=" * 80)
        print()

        for test_case in scenarios:
            print(f"Scenario {test_case['id']}: {test_case['name']}")
            print(f"Description: {test_case['description']}")
            print(f"Query: {test_case['query'][:120]}...")
            print("-" * 80)

            print("Running Regular Agent...")
            regular_result = self.run_single_test("regular", test_case["query"], test_case["id"])
            results["regular_agent"].append(
                {
                    "test_id": test_case["id"],
                    "name": test_case["name"],
                    "query": test_case["query"],
                    "description": test_case["description"],
                    **regular_result,
                }
            )
            print(f"  Time: {regular_result['execution_time']:.2f}s")
            print(f"  Iterations: {regular_result.get('iterations', 'N/A')}")
            print(f"  Input tokens: {regular_result.get('input_tokens', 'N/A')}")
            print(f"  Output tokens: {regular_result.get('output_tokens', 'N/A')}")
            if regular_result.get("validation"):
                val = regular_result["validation"]
                print(f"  Validation: {'PASS' if val['valid'] else 'FAIL'} ({val['passed']}/{val['total_checks']} checks)")
            print()

            print("Running Code Mode Agent...")
            time.sleep(2 + random.uniform(0, 1))
            codemode_result = self.run_single_test("codemode", test_case["query"], test_case["id"])
            results["codemode_agent"].append(
                {
                    "test_id": test_case["id"],
                    "name": test_case["name"],
                    "query": test_case["query"],
                    "description": test_case["description"],
                    **codemode_result,
                }
            )
            print(f"  Time: {codemode_result['execution_time']:.2f}s")
            print(f"  Iterations: {codemode_result.get('iterations', 'N/A')}")
            print(f"  Input tokens: {codemode_result.get('input_tokens', 'N/A')}")
            print(f"  Output tokens: {codemode_result.get('output_tokens', 'N/A')}")
            if codemode_result.get("sandbox_metrics"):
                sm = codemode_result["sandbox_metrics"]
                print(
                    "  Sandbox: "
                    f"{sm.get('runs', 0)} runs, "
                    f"avg compile {sm.get('avg_compile_ms', 0):.2f}ms, "
                    f"avg exec {sm.get('avg_execution_ms', 0):.2f}ms"
                )
            if codemode_result.get("validation"):
                val = codemode_result["validation"]
                print(f"  Validation: {'PASS' if val['valid'] else 'FAIL'} ({val['passed']}/{val['total_checks']} checks)")
            print()
            print("=" * 80)
            print()

            if test_case != scenarios[-1]:
                print("Waiting to avoid rate limits...")
                time.sleep(3 + random.uniform(0, 2))
                print()

        summary = self._calculate_summary(results)
        self._print_summary(summary)

        return {
            "model": self.model,
            "model_info": model_info,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "results": results,
            "summary": summary,
            "prompt_footprint": self._build_prompt_footprint_metrics(),
        }

    def _calculate_summary(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}

        for agent_type in ["regular_agent", "codemode_agent"]:
            agent_results = results[agent_type]
            successful = [r for r in agent_results if r.get("success", False)]
            validated = [r for r in agent_results if r.get("validation")]
            validation_passed = [r for r in validated if r.get("validation", {}).get("valid", False)]

            if not successful:
                summary[agent_type] = {
                    "total_tests": len(agent_results),
                    "successful_tests": 0,
                    "validated_tests": len(validated),
                    "validation_passed": len(validation_passed),
                    "validation_rate": 0.0,
                }
                continue

            payload: Dict[str, Any] = {
                "total_tests": len(agent_results),
                "successful_tests": len(successful),
                "validated_tests": len(validated),
                "validation_passed": len(validation_passed),
                "validation_rate": len(validation_passed) / len(validated) if validated else 0.0,
                "avg_execution_time": sum(r["execution_time"] for r in successful) / len(successful),
                "avg_iterations": sum(r.get("iterations", 0) for r in successful) / len(successful),
                "total_input_tokens": sum(r.get("input_tokens", 0) for r in successful),
                "total_output_tokens": sum(r.get("output_tokens", 0) for r in successful),
                "avg_input_tokens": sum(r.get("input_tokens", 0) for r in successful) / len(successful),
                "avg_output_tokens": sum(r.get("output_tokens", 0) for r in successful) / len(successful),
            }

            if agent_type == "codemode_agent":
                sandbox_rows = [r.get("sandbox_metrics") for r in successful if r.get("sandbox_metrics")]
                executed_code = [r for r in successful if len(r.get("code_executions", [])) > 0]
                payload["executed_code_tests"] = len(executed_code)
                payload["executed_code_rate"] = len(executed_code) / len(successful) if successful else 0.0
                if sandbox_rows:
                    payload["avg_sandbox_compile_ms"] = sum(x.get("avg_compile_ms", 0) for x in sandbox_rows) / len(sandbox_rows)
                    payload["avg_sandbox_execution_ms"] = sum(x.get("avg_execution_ms", 0) for x in sandbox_rows) / len(sandbox_rows)
                    payload["avg_sandbox_total_ms"] = sum(x.get("avg_total_ms", 0) for x in sandbox_rows) / len(sandbox_rows)
                    payload["avg_sandbox_tool_calls"] = sum(x.get("total_tool_calls", 0) for x in sandbox_rows) / len(sandbox_rows)

            summary[agent_type] = payload

        return summary

    def _print_summary(self, summary: Dict[str, Any]):
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
            if stats["successful_tests"] > 0:
                print(f"  Avg Execution Time: {stats['avg_execution_time']:.2f}s")
                print(f"  Avg Iterations: {stats['avg_iterations']:.2f}")
                print(f"  Total Input Tokens: {stats['total_input_tokens']}")
                print(f"  Total Output Tokens: {stats['total_output_tokens']}")
                if agent_type == "codemode_agent" and "avg_sandbox_execution_ms" in stats:
                    print(f"  Avg Sandbox Compile: {stats['avg_sandbox_compile_ms']:.2f}ms")
                    print(f"  Avg Sandbox Exec: {stats['avg_sandbox_execution_ms']:.2f}ms")
                if agent_type == "codemode_agent" and "executed_code_tests" in stats:
                    print(
                        "  Executed Code: "
                        f"{stats['executed_code_tests']}/{stats['successful_tests']} "
                        f"({stats['executed_code_rate']*100:.1f}%)"
                    )
            print()

        if summary["regular_agent"]["successful_tests"] > 0 and summary["codemode_agent"]["successful_tests"] > 0:
            print("Comparison:")
            time_diff = (
                (summary["codemode_agent"]["avg_execution_time"] - summary["regular_agent"]["avg_execution_time"])
                / summary["regular_agent"]["avg_execution_time"]
                * 100
            )
            token_diff = (
                (summary["codemode_agent"]["total_input_tokens"] + summary["codemode_agent"]["total_output_tokens"])
                - (summary["regular_agent"]["total_input_tokens"] + summary["regular_agent"]["total_output_tokens"])
            )
            print(f"  Code Mode time vs Regular: {time_diff:+.1f}%")
            print(f"  Token difference (Code Mode - Regular): {token_diff:+d}")
            print()

    def run_security_evaluation(self) -> Dict[str, Any]:
        """Run sandbox jailbreak checks."""
        executor = CodeExecutor(self.tools)
        return executor.run_security_evaluation()

    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None, output_dir: str = "results"):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        final_name = filename or f"benchmark_results_{self.model}.json"
        file_path = output_path / final_name
        file_path.write_text(json.dumps(results, indent=2))
        print(f"Results saved to {file_path}")


def _collect_api_keys_from_env() -> Dict[str, str]:
    api_keys: Dict[str, str] = {}
    for model in AgentFactory.get_supported_models():
        env_name = AgentFactory.get_required_api_key_env(model)
        value = os.getenv(env_name)
        if value:
            api_keys[model] = value
    return api_keys


def _run_single_model(
    model: str,
    api_keys: Dict[str, str],
    scenarios: Optional[List[Dict[str, Any]]],
    limit: Optional[int],
    output_dir: str,
    run_security_eval: bool,
    mcp_tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    benchmark = Benchmark(model=model, api_keys=api_keys, mcp_tools=mcp_tools)
    results = benchmark.run_benchmark(scenarios=scenarios, limit=limit)

    if run_security_eval:
        print("Running security evaluation...")
        security = benchmark.run_security_evaluation()
        print(f"Security pass rate: {security['passed']}/{security['total']} ({security['pass_rate']*100:.1f}%)")
        results["security_evaluation"] = security

    benchmark.save_results(results, output_dir=output_dir)
    return results


def main():
    parser = argparse.ArgumentParser(description="Run Code Mode benchmark")
    parser.add_argument("--limit", type=int, help="Limit number of scenarios to run")
    parser.add_argument("--scenario", type=int, help="Run only a specific scenario ID")
    parser.add_argument(
        "--model",
        type=str,
        default="claude",
        choices=AgentFactory.get_supported_models(),
        help="Model key to use for benchmark",
    )
    parser.add_argument(
        "--run-latest",
        action="store_true",
        help="Run the latest-model suite (opus_4_6, gpt_5_1, gpt_5_2, glm_5, gemini_3_pro)",
    )
    parser.add_argument("--security-eval", action="store_true", help="Run sandbox jailbreak checks after benchmark")
    parser.add_argument("--output-dir", type=str, default="results", help="Directory to store results JSON")
    parser.add_argument(
        "--mcp-tools-file",
        type=str,
        help="Optional MCP tools JSON file to translate into benchmark schemas/API prompts",
    )
    parser.add_argument(
        "--print-translated-api",
        action="store_true",
        help="Print the translated Code Mode API from --mcp-tools-file and exit",
    )
    args = parser.parse_args()

    load_dotenv()

    mcp_tools = None
    if args.mcp_tools_file:
        mcp_tools = load_mcp_tools_from_file(args.mcp_tools_file)
        if args.print_translated_api:
            print(mcp_tools_to_code_mode_api(mcp_tools))
            return

    api_keys = _collect_api_keys_from_env()

    scenarios = None
    if args.scenario:
        scenario = get_scenario_by_id(args.scenario)
        if scenario:
            scenarios = [scenario]
        else:
            print(f"Error: Scenario {args.scenario} not found")
            return

    if args.run_latest:
        latest_models = AgentFactory.get_latest_models()
        runnable_models = [m for m in latest_models if m in api_keys]
        if not runnable_models:
            print("Error: no API keys found for latest suite models.")
            print("Set one or more of these env vars:")
            for model in latest_models:
                print(f"  {AgentFactory.get_required_api_key_env(model)}  ({model})")
            return

        suite_results = {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "models_run": runnable_models,
            "runs": {},
        }
        for model in runnable_models:
            print()
            print("#" * 80)
            print(f"RUNNING MODEL: {model}")
            print("#" * 80)
            run_result = _run_single_model(
                model=model,
                api_keys=api_keys,
                scenarios=scenarios,
                limit=args.limit,
                output_dir=args.output_dir,
                run_security_eval=args.security_eval,
                mcp_tools=mcp_tools,
            )
            suite_results["runs"][model] = run_result

        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        suite_file = output_path / f"benchmark_results_latest_suite_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        suite_file.write_text(json.dumps(suite_results, indent=2))
        print(f"\nSuite results saved to {suite_file}")
        return

    if args.model not in api_keys:
        required_env = AgentFactory.get_required_api_key_env(args.model)
        print(f"Error: {required_env} not found in environment")
        print("Please add your API key to .env")
        print(f"  {required_env}=your_key_here")
        return

    _run_single_model(
        model=args.model,
        api_keys=api_keys,
        scenarios=scenarios,
        limit=args.limit,
        output_dir=args.output_dir,
        run_security_eval=args.security_eval,
        mcp_tools=mcp_tools,
    )


if __name__ == "__main__":
    main()
