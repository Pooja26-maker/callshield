import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_usage_lock = threading.Lock()


def log_usage(
    log_path: str,
    model: str,
    prompt_tokens: int | None,
    candidate_tokens: int | None,
    total_tokens: int | None,
    input_price_per_million: float | None = None,
    output_price_per_million: float | None = None,
) -> None:
    """Append one AI request's usage details to a JSONL file."""
    usage_available = any(
        value is not None
        for value in (prompt_tokens, candidate_tokens, total_tokens)
    )

    estimated_cost = None

    if (
        prompt_tokens is not None
        and candidate_tokens is not None
        and input_price_per_million is not None
        and output_price_per_million is not None
    ):
        estimated_cost = (
            prompt_tokens * input_price_per_million
            + candidate_tokens * output_price_per_million
        ) / 1_000_000

    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "candidate_tokens": candidate_tokens,
        "total_tokens": total_tokens,
        "usage_available": usage_available,
        "estimated_cost_usd": estimated_cost,
    }

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with _usage_lock:
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")


def get_usage_summary(log_path: str) -> dict[str, Any]:
    """Read the usage ledger and return aggregate statistics."""
    path = Path(log_path)

    records = []

    if path.exists():
        with _usage_lock:
            with path.open("r", encoding="utf-8") as file:
                for line in file:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

    prompt_total = sum(
        record.get("prompt_tokens") or 0 for record in records
    )
    candidate_total = sum(
        record.get("candidate_tokens") or 0 for record in records
    )
    total_tokens = sum(
        record.get("total_tokens") or 0 for record in records
    )

    priced_records = [
        record
        for record in records
        if record.get("estimated_cost_usd") is not None
    ]

    estimated_cost = (
        sum(record["estimated_cost_usd"] for record in priced_records)
        if priced_records
        else None
    )

    return {
        "request_count": len(records),
        "usage_available_request_count": sum(
            record.get("usage_available", False) for record in records
        ),
        "total_prompt_tokens": prompt_total,
        "total_candidate_tokens": candidate_total,
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost,
        "cost_available": len(priced_records) == len(records) and bool(records),
        "records": records,
    }