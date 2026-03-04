"""
Observability helpers for benchmark traces, discrepancy analysis, and reports.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


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


def _tool_expected_vs_actual(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = tool_call.get("tool") or tool_call.get("name")
    kwargs = tool_call.get("kwargs_structured") or tool_call.get("input") or {}
    if not isinstance(kwargs, dict):
        kwargs = {}
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

    actual_tools_flat = [row.get("tool") for row in tool_rows if row.get("tool")]
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


def write_trace_artifacts(results: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    out = Path(output_dir)
    traces = out / "traces"
    traces.mkdir(parents=True, exist_ok=True)
    model = _safe_model_slug(results.get("model", "unknown"))
    trace_path = traces / f"{model}_codemode_trace.jsonl"

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


def generate_markdown_report(payload: Dict[str, Any], output_dir: str, report_name: Optional[str] = None) -> str:
    out = Path(output_dir)
    reports_dir = out / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = report_name or f"benchmark_report_{timestamp}.md"
    report_path = reports_dir / filename

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
    codemode_rows = payload.get("results", {}).get("codemode_agent", [])
    lines = [
        "# Benchmark Report",
        "",
        f"- Model: {payload.get('model')}",
        f"- Generated (UTC): {datetime.utcnow().isoformat()}Z",
        "",
        "## Summary",
        "",
        f"- Regular validation: {summary.get('regular_agent', {}).get('validation_passed', 0)}/{summary.get('regular_agent', {}).get('validated_tests', 0)}",
        f"- CodeMode validation: {summary.get('codemode_agent', {}).get('validation_passed', 0)}/{summary.get('codemode_agent', {}).get('validated_tests', 0)}",
        "",
        "## CodeMode Debug",
        "",
        "| Scenario | Iterations | Iteration Failures | Tool Discrepancies |",
        "|---|---:|---:|---:|",
    ]
    for row in codemode_rows:
        obs = row.get("observability", {})
        lines.append(
            "| "
            f"{row.get('test_id')} - {row.get('name')} | "
            f"{row.get('iterations', 0)} | "
            f"{obs.get('iteration_failures', 0)} | "
            f"{obs.get('tool_discrepancy_count', 0)} |"
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)

