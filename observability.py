"""
Observability helpers for benchmark traces, discrepancy analysis, and reports.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


TOOL_PARAM_ORDER: Dict[str, List[str]] = {
    "create_transaction": [
        "transaction_type",
        "category",
        "amount",
        "description",
        "account",
        "date",
        "tags",
    ],
    "create_invoice": ["client_name", "items", "due_days", "issue_date"],
    "update_invoice_status": ["invoice_id", "new_status"],
    "record_partial_payment": ["invoice_id", "amount"],
    "transfer_between_accounts": ["from_account", "to_account", "amount", "description"],
}


def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 2
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _parse_tool_result(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _tool_inputs(tool_name: Any, tool_call: Dict[str, Any]) -> Dict[str, Any]:
    kwargs = tool_call.get("kwargs_structured") or tool_call.get("input") or {}
    if isinstance(kwargs, dict):
        merged = dict(kwargs)
    else:
        merged = {}

    args = tool_call.get("args_structured") or []
    if not isinstance(args, list):
        return merged

    param_order = TOOL_PARAM_ORDER.get(str(tool_name), [])
    for index, value in enumerate(args):
        if index >= len(param_order):
            break
        merged.setdefault(param_order[index], value)
    return merged


def _tool_expected_vs_actual(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = tool_call.get("tool") or tool_call.get("name")
    if isinstance(tool_name, str) and tool_name.startswith("__toolfs_"):
        return {
            "tool": tool_name,
            "expected": {"discovery_event": True},
            "actual": {"discovery_event": True, "tool_success": tool_call.get("success", True)},
            "discrepancies": [],
            "ok": True,
        }
    kwargs = _tool_inputs(tool_name, tool_call)
    parsed = _parse_tool_result(tool_call.get("result") or tool_call.get("result_structured"))
    discrepancies: List[str] = []
    expected: Dict[str, Any] = {"tool": tool_name}
    actual: Dict[str, Any] = {"tool": tool_name, "tool_success": tool_call.get("success", True)}

    if parsed.get("error"):
        discrepancies.append(f"tool-returned-error:{parsed.get('error')}")

    if tool_name == "create_transaction":
        expected.update(
            {
                "transaction_type": kwargs.get("transaction_type"),
                "category": kwargs.get("category"),
                "amount": kwargs.get("amount"),
                "account": kwargs.get("account", "checking"),
                "state_delta.total_transactions": 1,
            }
        )
        tx = parsed.get("transaction") if isinstance(parsed.get("transaction"), dict) else {}
        actual.update(
            {
                "transaction_type": tx.get("type"),
                "category": tx.get("category"),
                "amount": tx.get("amount"),
                "account": tx.get("account"),
            }
        )
        if tx.get("type") != kwargs.get("transaction_type"):
            discrepancies.append("transaction_type_mismatch")
        if tx.get("account") != kwargs.get("account", "checking"):
            discrepancies.append("account_mismatch")
    elif tool_name == "create_invoice":
        expected.update(
            {
                "client_name": kwargs.get("client_name"),
                "items_count": len(kwargs.get("items", [])) if isinstance(kwargs.get("items"), list) else None,
                "state_delta.total_invoices": 1,
            }
        )
        invoice = parsed.get("invoice") if isinstance(parsed.get("invoice"), dict) else {}
        actual.update(
            {
                "client_name": invoice.get("client_name"),
                "items_count": len(invoice.get("items", [])) if isinstance(invoice.get("items"), list) else None,
            }
        )
        if expected["client_name"] != actual["client_name"]:
            discrepancies.append("client_name_mismatch")
    elif tool_name == "update_invoice_status":
        expected.update({"invoice_id": kwargs.get("invoice_id"), "new_status": kwargs.get("new_status")})
        actual.update({"invoice_id": parsed.get("invoice_id"), "new_status": parsed.get("new_status")})
        if expected["invoice_id"] != actual["invoice_id"]:
            discrepancies.append("invoice_id_mismatch")
        if expected["new_status"] != actual["new_status"]:
            discrepancies.append("invoice_status_mismatch")
    elif tool_name == "record_partial_payment":
        expected.update({"invoice_id": kwargs.get("invoice_id"), "payment_amount": kwargs.get("amount")})
        actual.update({"invoice_id": parsed.get("invoice_id"), "payment_amount": parsed.get("payment_amount")})
        if expected["invoice_id"] != actual["invoice_id"]:
            discrepancies.append("invoice_id_mismatch")
    elif tool_name == "transfer_between_accounts":
        expected.update(
            {
                "from_account": kwargs.get("from_account"),
                "to_account": kwargs.get("to_account"),
                "amount": kwargs.get("amount"),
                "state_delta.total_transactions": 2,
            }
        )
        actual.update(
            {
                "from_account": parsed.get("from_account"),
                "to_account": parsed.get("to_account"),
                "amount": parsed.get("amount"),
            }
        )
        if expected["from_account"] != actual["from_account"]:
            discrepancies.append("from_account_mismatch")
        if expected["to_account"] != actual["to_account"]:
            discrepancies.append("to_account_mismatch")
    else:
        expected.update({"generic_success": True})

    state_delta = tool_call.get("state_delta")
    if isinstance(state_delta, dict):
        actual["state_delta"] = state_delta
        if "state_delta.total_transactions" in expected:
            expected_txn_delta = expected["state_delta.total_transactions"]
            actual_txn_delta = state_delta.get("total_transactions")
            if expected_txn_delta != actual_txn_delta:
                discrepancies.append("state_total_transactions_delta_mismatch")
        if "state_delta.total_invoices" in expected:
            expected_invoice_delta = expected["state_delta.total_invoices"]
            actual_invoice_delta = state_delta.get("total_invoices")
            if expected_invoice_delta != actual_invoice_delta:
                discrepancies.append("state_total_invoices_delta_mismatch")

    return {
        "tool": tool_name,
        "expected": expected,
        "actual": actual,
        "discrepancies": discrepancies,
        "ok": len(discrepancies) == 0,
    }


def build_codemode_observability(scenario: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    expected_state = scenario.get("expected_state", {})
    code_executions = result.get("code_executions") or []
    expected_tool_flow = scenario.get("expected_tool_flow", [])
    tool_rows: List[Dict[str, Any]] = []
    failures = 0

    for execution_index, execution in enumerate(code_executions, start=1):
        execution_result = execution.get("execution_result", {})
        if not execution_result.get("success"):
            failures += 1
        for idx, tool_call in enumerate(execution_result.get("tool_calls", []), start=1):
            row = _tool_expected_vs_actual(tool_call)
            row["execution_index"] = execution_index
            row["call_index"] = idx
            tool_rows.append(row)

    expected_tools_flat = []
    for item in expected_tool_flow:
        tool_name = item.get("tool") if isinstance(item, dict) else None
        min_calls = item.get("min_calls", 1) if isinstance(item, dict) else 1
        if tool_name:
            expected_tools_flat.extend([tool_name] * int(min_calls))

    actual_tools_flat = [
        row.get("tool")
        for row in tool_rows
        if row.get("tool") and not str(row.get("tool")).startswith("__toolfs_")
    ]
    missing = []
    unexpected = []
    expected_counts: Dict[str, int] = {}
    actual_counts: Dict[str, int] = {}
    for tool_name in expected_tools_flat:
        expected_counts[tool_name] = expected_counts.get(tool_name, 0) + 1
    for tool_name in actual_tools_flat:
        actual_counts[tool_name] = actual_counts.get(tool_name, 0) + 1

    for tool_name, count in expected_counts.items():
        if actual_counts.get(tool_name, 0) < count:
            missing.append({"tool": tool_name, "expected_min": count, "actual": actual_counts.get(tool_name, 0)})
    for tool_name, count in actual_counts.items():
        if tool_name not in expected_counts:
            unexpected.append({"tool": tool_name, "actual": count})

    discrepancy_count = sum(len(row.get("discrepancies", [])) for row in tool_rows)
    return {
        "scenario_id": scenario.get("id"),
        "scenario_name": scenario.get("name"),
        "expected_state": expected_state,
        "expected_tool_flow": expected_tool_flow,
        "tool_trace": tool_rows,
        "iteration_failures": failures,
        "tool_discrepancy_count": discrepancy_count,
        "flow_discrepancies": {"missing_tools": missing, "unexpected_tools": unexpected},
    }


def _safe_model_slug(model: str) -> str:
    return model.replace("/", "_").replace(":", "_")


def _format_validation(row: Dict[str, Any]) -> str:
    val = row.get("validation") or {}
    if not val:
        return "N/A"
    status = "PASS" if val.get("valid") else "FAIL"
    return f"{status} ({val.get('passed', 0)}/{val.get('total_checks', 0)} checks)"


def _console_transcript_for_single_model(payload: Dict[str, Any]) -> str:
    model_name = payload.get("model_info", {}).get("name") or payload.get("model", "Unknown Model")
    regular_rows = {row.get("test_id"): row for row in payload.get("results", {}).get("regular_agent", [])}
    codemode_rows = {row.get("test_id"): row for row in payload.get("results", {}).get("codemode_agent", [])}
    scenario_ids = sorted(set(regular_rows.keys()) | set(codemode_rows.keys()))
    lines: List[str] = []

    lines.append("=" * 80)
    lines.append("BENCHMARK: Regular Agent vs Code Mode Agent")
    lines.append(f"Model: {model_name}")
    lines.append("=" * 80)
    lines.append("")

    for test_id in scenario_ids:
        reg = regular_rows.get(test_id, {})
        code = codemode_rows.get(test_id, {})
        name = reg.get("name") or code.get("name") or f"Scenario {test_id}"
        description = reg.get("description") or code.get("description") or ""
        query = reg.get("query") or code.get("query") or ""
        query_preview = (query[:120] + "...") if len(query) > 120 else query

        lines.append(f"Scenario {test_id}: {name}")
        lines.append(f"Description: {description}")
        lines.append(f"Query: {query_preview}")
        lines.append("-" * 80)
        lines.append("Running Regular Agent...")
        lines.append(f"  Time: {float(reg.get('execution_time', 0.0)):.2f}s")
        lines.append(f"  Iterations: {reg.get('iterations', 'N/A')}")
        lines.append(f"  Input tokens: {reg.get('input_tokens', 'N/A')}")
        lines.append(f"  Output tokens: {reg.get('output_tokens', 'N/A')}")
        lines.append(f"  Validation: {_format_validation(reg)}")
        if reg.get("error"):
            lines.append(f"  Error: {reg.get('error')}")
        lines.append("")
        lines.append("Running Code Mode Agent...")
        lines.append(f"  Time: {float(code.get('execution_time', 0.0)):.2f}s")
        lines.append(f"  Iterations: {code.get('iterations', 'N/A')}")
        lines.append(f"  Input tokens: {code.get('input_tokens', 'N/A')}")
        lines.append(f"  Output tokens: {code.get('output_tokens', 'N/A')}")
        sm = code.get("sandbox_metrics") or {}
        if sm:
            lines.append(
                "  Sandbox: "
                f"{sm.get('runs', 0)} runs, "
                f"avg compile {float(sm.get('avg_compile_ms', 0.0)):.2f}ms, "
                f"avg exec {float(sm.get('avg_execution_ms', 0.0)):.2f}ms"
            )
        obs = code.get("observability") or {}
        if obs:
            lines.append(
                "  Debug: "
                f"iteration_failures={obs.get('iteration_failures', 0)}, "
                f"tool_discrepancies={obs.get('tool_discrepancy_count', 0)}"
            )
        lines.append(f"  Validation: {_format_validation(code)}")
        if code.get("error"):
            lines.append(f"  Error: {code.get('error')}")
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

    summary = payload.get("summary", {})
    reg = summary.get("regular_agent", {})
    code = summary.get("codemode_agent", {})
    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Regular Agent:")
    lines.append(f"  Successful: {reg.get('successful_tests', 0)}/{reg.get('total_tests', 0)}")
    lines.append(
        f"  Validation: {reg.get('validation_passed', 0)}/{reg.get('validated_tests', 0)} passed ({float(reg.get('validation_rate', 0.0))*100:.1f}%)"
    )
    if reg.get("successful_tests", 0) > 0:
        lines.append(f"  Avg Execution Time: {float(reg.get('avg_execution_time', 0.0)):.2f}s")
        lines.append(f"  Avg Iterations: {float(reg.get('avg_iterations', 0.0)):.2f}")
        lines.append(f"  Total Input Tokens: {reg.get('total_input_tokens', 0)}")
        lines.append(f"  Total Output Tokens: {reg.get('total_output_tokens', 0)}")
    lines.append("")
    lines.append("Code Mode Agent:")
    lines.append(f"  Successful: {code.get('successful_tests', 0)}/{code.get('total_tests', 0)}")
    lines.append(
        f"  Validation: {code.get('validation_passed', 0)}/{code.get('validated_tests', 0)} passed ({float(code.get('validation_rate', 0.0))*100:.1f}%)"
    )
    if code.get("successful_tests", 0) > 0:
        lines.append(f"  Avg Execution Time: {float(code.get('avg_execution_time', 0.0)):.2f}s")
        lines.append(f"  Avg Iterations: {float(code.get('avg_iterations', 0.0)):.2f}")
        lines.append(f"  Total Input Tokens: {code.get('total_input_tokens', 0)}")
        lines.append(f"  Total Output Tokens: {code.get('total_output_tokens', 0)}")
        if "avg_sandbox_compile_ms" in code:
            lines.append(f"  Avg Sandbox Compile: {float(code.get('avg_sandbox_compile_ms', 0.0)):.2f}ms")
            lines.append(f"  Avg Sandbox Exec: {float(code.get('avg_sandbox_execution_ms', 0.0)):.2f}ms")
        if "executed_code_tests" in code:
            lines.append(
                f"  Executed Code: {code.get('executed_code_tests', 0)}/{code.get('successful_tests', 0)} ({float(code.get('executed_code_rate', 0.0))*100:.1f}%)"
            )
        if "total_iteration_failures" in code:
            lines.append(f"  Iteration Failures: {code.get('total_iteration_failures', 0)}")
            lines.append(f"  Tool Discrepancies: {code.get('total_tool_discrepancies', 0)}")
    lines.append("")

    if reg.get("successful_tests", 0) > 0 and code.get("successful_tests", 0) > 0 and float(reg.get("avg_execution_time", 0.0)) > 0:
        time_diff = ((float(code.get("avg_execution_time", 0.0)) - float(reg.get("avg_execution_time", 0.0))) / float(reg.get("avg_execution_time", 1.0))) * 100
        token_diff = (
            int(code.get("total_input_tokens", 0)) + int(code.get("total_output_tokens", 0))
            - int(reg.get("total_input_tokens", 0)) - int(reg.get("total_output_tokens", 0))
        )
        lines.append("Comparison:")
        lines.append(f"  Code Mode time vs Regular: {time_diff:+.1f}%")
        lines.append(f"  Token difference (Code Mode - Regular): {token_diff:+d}")
    return "\n".join(lines).rstrip() + "\n"


def write_trace_artifacts(results: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    out = Path(output_dir)
    traces = out / "traces"
    traces.mkdir(parents=True, exist_ok=True)
    model = _safe_model_slug(results.get("model", "unknown"))
    trace_path = _next_available_path(traces / f"{model}_codemode_trace.jsonl")

    lines = 0
    with trace_path.open("w", encoding="utf-8") as handle:
        for row in results.get("results", {}).get("codemode_agent", []):
            payload = {
                "test_id": row.get("test_id"),
                "name": row.get("name"),
                "success": row.get("success"),
                "iterations": row.get("iterations"),
                "iteration_trace": row.get("iteration_trace", []),
                "observability": row.get("observability", {}),
            }
            handle.write(json.dumps(payload) + "\n")
            lines += 1

    return {"codemode_trace_jsonl": str(trace_path), "rows": str(lines)}


def write_console_log(payload: Dict[str, Any], logs_dir: str = "logs", filename: Optional[str] = None) -> Optional[str]:
    if "results" not in payload:
        return None
    out = Path(logs_dir)
    out.mkdir(parents=True, exist_ok=True)
    model = payload.get("model", "benchmark")
    default_name = f"{model.replace('_', '-')}.txt"
    path = _next_available_path(out / (filename or default_name))
    path.write_text(_console_transcript_for_single_model(payload), encoding="utf-8")
    return str(path)


def generate_markdown_report(payload: Dict[str, Any], output_dir: str, report_name: Optional[str] = None) -> str:
    out = Path(output_dir)
    reports_dir = out / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    if report_name:
        filename = report_name
    else:
        if "runs" in payload:
            filename = f"benchmark_suite_report_{timestamp}.md"
        else:
            model_slug = _safe_model_slug(str(payload.get("model", "unknown")))
            filename = f"benchmark_report_{model_slug}_{timestamp}.md"
    report_path = _next_available_path(reports_dir / filename)

    if "runs" in payload:
        lines = [
            "# Benchmark Suite Report",
            "",
            f"- Generated (UTC): {datetime.utcnow().isoformat()}Z",
            "",
            "| Model | Regular Validation | CodeMode Validation | CodeMode Iteration Failures |",
            "|---|---:|---:|---:|",
        ]
        for model, run in payload.get("runs", {}).items():
            reg = run.get("summary", {}).get("regular_agent", {})
            code = run.get("summary", {}).get("codemode_agent", {})
            codemode_rows = run.get("results", {}).get("codemode_agent", [])
            iteration_failures = 0
            for row in codemode_rows:
                obs = row.get("observability", {})
                iteration_failures += int(obs.get("iteration_failures", 0))
            lines.append(
                "| "
                f"{model} | "
                f"{reg.get('validation_passed', 0)}/{reg.get('validated_tests', 0)} | "
                f"{code.get('validation_passed', 0)}/{code.get('validated_tests', 0)} | "
                f"{iteration_failures} |"
            )
        report_path.write_text("\n".join(lines), encoding="utf-8")
        return str(report_path)

    summary = payload.get("summary", {})
    reg = summary.get("regular_agent", {})
    code = summary.get("codemode_agent", {})
    regular_rows = payload.get("results", {}).get("regular_agent", [])
    codemode_rows = payload.get("results", {}).get("codemode_agent", [])
    codemode_by_id = {r.get("test_id"): r for r in codemode_rows}
    transcript = _console_transcript_for_single_model(payload)

    lines = [
        "# Benchmark Report",
        "",
        f"- Model: {payload.get('model_info', {}).get('name', payload.get('model'))}",
        f"- Model Key: `{payload.get('model')}`",
        f"- Generated (UTC): {datetime.utcnow().isoformat()}Z",
        "",
        "## Executive Summary",
        "",
        f"- Regular validation: {reg.get('validation_passed', 0)}/{reg.get('validated_tests', 0)} ({float(reg.get('validation_rate', 0.0))*100:.1f}%)",
        f"- Code Mode validation: {code.get('validation_passed', 0)}/{code.get('validated_tests', 0)} ({float(code.get('validation_rate', 0.0))*100:.1f}%)",
        f"- Avg execution time: Regular `{float(reg.get('avg_execution_time', 0.0)):.2f}s` vs Code Mode `{float(code.get('avg_execution_time', 0.0)):.2f}s`",
        f"- Total tokens: Regular `{int(reg.get('total_input_tokens', 0)) + int(reg.get('total_output_tokens', 0) )}` vs Code Mode `{int(code.get('total_input_tokens', 0)) + int(code.get('total_output_tokens', 0))}`",
        f"- Code Mode iteration failures: `{code.get('total_iteration_failures', 0)}`",
        f"- Code Mode tool discrepancies: `{code.get('total_tool_discrepancies', 0)}`",
        "",
        "## Scenario Breakdown",
        "",
        "| Scenario | Regular (time/iter/tokens) | Code Mode (time/iter/tokens) | Validation (R/C) |",
        "|---|---|---|---|",
    ]
    for reg_row in regular_rows:
        sid = reg_row.get("test_id")
        code_row = codemode_by_id.get(sid, {})
        reg_tokens = int(reg_row.get("input_tokens", 0)) + int(reg_row.get("output_tokens", 0))
        code_tokens = int(code_row.get("input_tokens", 0)) + int(code_row.get("output_tokens", 0))
        lines.append(
            f"| {sid} - {reg_row.get('name','')} | "
            f"{float(reg_row.get('execution_time', 0.0)):.2f}s / {reg_row.get('iterations','N/A')} / {reg_tokens} | "
            f"{float(code_row.get('execution_time', 0.0)):.2f}s / {code_row.get('iterations','N/A')} / {code_tokens} | "
            f"{_format_validation(reg_row)} / {_format_validation(code_row)} |"
        )

    lines.extend(
        [
            "",
            "## Code Mode Observability Highlights",
            "",
            "| Scenario | Iteration Failures | Tool Discrepancies | Missing Expected Tools |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in codemode_rows:
        obs = row.get("observability") or {}
        missing = len((obs.get("flow_discrepancies") or {}).get("missing_tools") or [])
        lines.append(
            f"| {row.get('test_id')} - {row.get('name','')} | "
            f"{obs.get('iteration_failures', 0)} | "
            f"{obs.get('tool_discrepancy_count', 0)} | "
            f"{missing} |"
        )

    lines.extend(
        [
            "",
            "## Console Transcript",
            "",
            "```text",
            transcript.rstrip(),
            "```",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)
