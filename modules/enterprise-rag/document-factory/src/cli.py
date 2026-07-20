#!/usr/bin/env python3
"""CLI: plan → generate → validate → manifest → questions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT.parent))

from src.config_loader import load_generation_config  # noqa: E402
from src.generator import generate_corpus  # noqa: E402
from src.manifest import write_manifest  # noqa: E402
from src.planner import write_plans  # noqa: E402
from src.questions import draft_gold_questions  # noqa: E402
from src.status import corpus_status  # noqa: E402
from src.validator import validate_corpus  # noqa: E402


def cmd_plan(args: argparse.Namespace) -> None:
    gen = load_generation_config()
    n = args.n
    if n is None:
        n = int(gen["default_gold_n"] if args.corpus == "gold" else gen["default_scale_n"])
    seed = args.seed if args.seed is not None else int(gen["default_seed"])
    path = write_plans(args.corpus, n=n, seed=seed)
    print(json.dumps({"corpus": args.corpus, "n": n, "seed": seed, "plans": str(path)}, indent=2))


def cmd_generate(args: argparse.Namespace) -> None:
    gen = load_generation_config()
    concurrency = args.concurrency
    if concurrency is None:
        concurrency = int(gen.get("default_concurrency") or 3)
    result = generate_corpus(
        args.corpus,
        model=args.model,
        concurrency=concurrency,
        resume=not args.no_resume,
        limit=args.limit,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2))


def cmd_validate(args: argparse.Namespace) -> None:
    result = validate_corpus(args.corpus)
    print(json.dumps(result, indent=2))
    if result["failed"] or result["missing"]:
        raise SystemExit(1)


def cmd_manifest(args: argparse.Namespace) -> None:
    path = write_manifest(args.corpus)
    print(json.dumps({"corpus": args.corpus, "manifest": str(path)}, indent=2))


def cmd_questions(_: argparse.Namespace) -> None:
    path = draft_gold_questions()
    print(json.dumps({"questions": str(path)}, indent=2))


def cmd_status(args: argparse.Namespace) -> None:
    print(json.dumps(corpus_status(args.corpus), indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nirvana IQ document factory")
    sub = parser.add_subparsers(dest="command", required=True)

    plan_p = sub.add_parser("plan", help="Write document plans JSONL")
    plan_p.add_argument("--corpus", choices=["gold", "scale"], required=True)
    plan_p.add_argument("--n", type=int, default=None)
    plan_p.add_argument("--seed", type=int, default=None)
    plan_p.set_defaults(func=cmd_plan)

    gen_p = sub.add_parser("generate", help="LLM-generate markdown from plans")
    gen_p.add_argument("--corpus", choices=["gold", "scale"], required=True)
    gen_p.add_argument("--model", default=None)
    gen_p.add_argument("--concurrency", type=int, default=None)
    gen_p.add_argument("--limit", type=int, default=None, help="Only first N plans")
    gen_p.add_argument("--dry-run", action="store_true")
    gen_p.add_argument("--no-resume", action="store_true")
    gen_p.set_defaults(func=cmd_generate)

    val_p = sub.add_parser("validate", help="Validate required facts in generated docs")
    val_p.add_argument("--corpus", choices=["gold", "scale"], required=True)
    val_p.set_defaults(func=cmd_validate)

    man_p = sub.add_parser("manifest", help="Write documents.jsonl (+ gold JSON)")
    man_p.add_argument("--corpus", choices=["gold", "scale"], required=True)
    man_p.set_defaults(func=cmd_manifest)

    q_p = sub.add_parser("questions", help="Draft gold evaluation questions")
    q_p.set_defaults(func=cmd_questions)

    st_p = sub.add_parser("status", help="Show corpus progress counts")
    st_p.add_argument("--corpus", choices=["gold", "scale"], required=True)
    st_p.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
