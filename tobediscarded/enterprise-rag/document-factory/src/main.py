"""CLI entrypoint for the Nirvana Retail document factory."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .config_loader import FACTORY_ROOT, load_company_config, load_generation_config
from .generator import DocumentFactory
from .llm_client import LLMClient


def build_parser(defaults_documents: int, defaults_seed: int, defaults_concurrency: int) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate synthetic enterprise documents for Nirvana Retail Group.",
    )
    parser.add_argument("--documents", type=int, default=defaults_documents, help="Number of documents to plan/generate")
    parser.add_argument("--start-year", type=int, default=2020, help="Inclusive start year (2020-2026)")
    parser.add_argument("--end-year", type=int, default=2026, help="Inclusive end year (2020-2026)")
    parser.add_argument("--seed", type=int, default=defaults_seed, help="Deterministic planning seed")
    parser.add_argument(
        "--output",
        type=Path,
        default=FACTORY_ROOT / "output",
        help="Output directory for raw docs, manifests, and evaluation files",
    )
    parser.add_argument("--concurrency", type=int, default=defaults_concurrency, help="Parallel generation workers")
    parser.add_argument("--dry-run", action="store_true", help="Plan documents without calling the OpenAI API")
    parser.add_argument("--resume", action="store_true", help="Skip document IDs already present under output/raw")
    parser.add_argument(
        "--provider",
        choices=("openai", "local", "auto"),
        default="auto",
        help="openai=Responses API, local=fact-grounded renderer, auto=openai if OPENAI_API_KEY else local",
    )
    parser.add_argument("--company-config", type=Path, default=None, help="Optional path to company.yaml")
    parser.add_argument("--generation-config", type=Path, default=None, help="Optional path to generation.yaml")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv(FACTORY_ROOT / ".env")
    generation_cfg = load_generation_config()
    parser = build_parser(
        generation_cfg.default_documents,
        generation_cfg.default_seed,
        generation_cfg.default_concurrency,
    )
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    if args.start_year < 2020 or args.end_year > 2026 or args.start_year > args.end_year:
        logging.error("Years must satisfy 2020 <= start <= end <= 2026")
        return 2
    if args.documents < 1:
        logging.error("--documents must be >= 1")
        return 2

    company = load_company_config(args.company_config)
    generation = load_generation_config(args.generation_config)
    output_dir = args.output if args.output.is_absolute() else (Path.cwd() / args.output)

    provider = args.provider
    if provider == "auto":
        provider = "openai" if os.getenv("OPENAI_API_KEY") else "local"
    logging.info("Using provider=%s", provider)

    factory = DocumentFactory(
        company=company,
        generation=generation,
        output_dir=output_dir.resolve(),
        llm_client=LLMClient(
            max_retries=generation.max_retries,
            base_delay_seconds=generation.retry_base_delay_seconds,
        ),
        concurrency=args.concurrency,
        provider=provider,
    )
    summary = factory.run(
        documents=args.documents,
        start_year=args.start_year,
        end_year=args.end_year,
        seed=args.seed,
        dry_run=args.dry_run,
        resume=args.resume,
    )
    logging.info(
        "Finished: generated=%s skipped=%s failed=%s dry_run=%s elapsed=%.2fs",
        summary.generated,
        summary.skipped,
        summary.failed,
        summary.dry_run,
        summary.elapsed_seconds,
    )
    return 0 if summary.failed == 0 or summary.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())
