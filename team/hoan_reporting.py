"""Reporting helpers assigned to Hoàn.

The GUI can use this module later to build dashboard summaries without
duplicating counting logic in widgets.
"""

from collections.abc import Iterable
from typing import Any


def summarize_submissions(submissions: Iterable[Any]) -> dict[str, int | float]:
    """Return stable batch totals for successful, warning, and failed papers."""
    items = list(submissions)
    successful = sum(getattr(item, "status", "") == "Thành công" for item in items)
    warnings = sum(getattr(item, "status", "") == "Cảnh báo" for item in items)
    errors = sum(getattr(item, "status", "") == "Lỗi" for item in items)
    scores = [float(getattr(item, "score", 0.0)) for item in items if getattr(item, "status", "") != "Lỗi"]
    return {
        "total": len(items),
        "successful": successful,
        "warnings": warnings,
        "errors": errors,
        "average_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
    }
