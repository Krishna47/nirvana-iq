#!/usr/bin/env python3
"""CLI for Nirvana IQ enterprise-rag version ladder demos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from pipelines.registry import get_pipeline, list_versions  # noqa: E402
from shared.contracts import run_pipeline  # noqa: E402
from shared.corpus import load_questions  # noqa: E402


def cmd_list(_: argparse.Namespace) -> None:
    for version in list_versions():
        print(version)


def cmd_ask(args: argparse.Namespace) -> None:
    pipeline = get_pipeline(args.version)
    result = run_pipeline(pipeline, args.question)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return
    print(f"version: {result.version}")
    print(f"latency_ms: {result.latency_ms:.1f}")
    print(f"citations: {', '.join(result.citations) or '(none)'}")
    print(f"notes: {result.notes}")
    print("---")
    print(result.answer)


def cmd_eval(args: argparse.Namespace) -> None:
    """Smoke eval: citation overlap with expected_sources (not full answer scoring)."""
    pipeline = get_pipeline(args.version)
    questions = load_questions()
    hits = 0
    total = 0
    rows: list[dict] = []

    for item in questions:
        result = run_pipeline(pipeline, item["question"])
        expected = set(item.get("expected_sources") or [])
        got = set(result.citations)
        overlap = expected & got
        total += 1
        if expected and overlap:
            hits += 1
        rows.append(
            {
                "id": item["id"],
                "citation_hit": bool(overlap),
                "expected_sources": sorted(expected),
                "citations": result.citations,
                "latency_ms": round(result.latency_ms, 1),
            }
        )

    summary = {
        "version": args.version,
        "citation_hit_rate": (hits / total) if total else 0.0,
        "n": total,
        "rows": rows,
    }
    print(json.dumps(summary, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nirvana IQ enterprise-rag CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    list_p = sub.add_parser("list", help="List pipeline versions")
    list_p.set_defaults(func=cmd_list)

    ask_p = sub.add_parser("ask", help="Ask one question via a pipeline version")
    ask_p.add_argument("--version", default="v1_basic_rag")
    ask_p.add_argument("--question", required=True)
    ask_p.add_argument("--json", action="store_true")
    ask_p.set_defaults(func=cmd_ask)

    eval_p = sub.add_parser("eval", help="Run citation smoke eval on questions.json")
    eval_p.add_argument("--version", default="v1_basic_rag")
    eval_p.set_defaults(func=cmd_eval)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
