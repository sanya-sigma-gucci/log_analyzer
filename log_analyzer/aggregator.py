from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .parser import ParseError


@dataclass
class Summary:
    total_lines: int = 0
    valid_lines: int = 0
    invalid_lines: int = 0
    filtered_events: int = 0
    by_level: Dict[str, int] = field(default_factory=dict)
    by_source: Dict[str, int] = field(default_factory=dict)
    top_error_codes: Dict[str, int] = field(default_factory=dict)
    errors: List[ParseError] = field(default_factory=list)

    def finalize(self, top_n: int) -> None:
        """Sort output deterministically and apply top-N to error codes."""
        self.by_level = dict(sorted(self.by_level.items()))
        self.by_source = dict(sorted(self.by_source.items()))
        items = sorted(self.top_error_codes.items(), key=lambda kv: (-kv[1], kv[0]))
        if top_n > 0:
            items = items[:top_n]
        self.top_error_codes = dict(items)
        self.errors.sort(key=lambda e: e.line_number)