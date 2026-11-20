from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .parser import LogEntry


@dataclass(frozen=True)
class LogFilter:
    """Filters for log entries.

    from_ts is inclusive, to_ts is exclusive.
    Unset fields are ignored (match all values).
    """

    from_ts: Optional[datetime] = None
    to_ts: Optional[datetime] = None
    level: Optional[str] = None
    source: Optional[str] = None

    def matches(self, entry: LogEntry) -> bool:
        if self.from_ts is not None and entry.timestamp < self.from_ts:
            return False
        if self.to_ts is not None and entry.timestamp >= self.to_ts:
            return False
        if self.level is not None and entry.level != self.level:
            return False
        if self.source is not None and entry.source != self.source:
            return False
        return True