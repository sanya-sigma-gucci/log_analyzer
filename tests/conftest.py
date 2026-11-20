from __future__ import annotations

import pytest


@pytest.fixture
def sample_log_lines():
    return [
        "2026-09-01T00:08:59Z | WARN | auth-api | AUTH_LOGIN_OK | User session created\n",
        "2026-09-01T00:20:18Z | ERROR | payment-worker | PAYMENT_TIMEOUT | Payment provider timed out\n",
        "2026-09-01T00:47:04Z | INFO | auth-api | AUTH_TOKEN_EXPIRED | Access token expired\n",
        "2026-09-01T01:04:21Z | ERROR | orders-api | ORDER_REJECTED | Order validation failed\n",
        "2026-09-01T02:34:23Z | WARN | auth-api | AUTH_TOKEN_EXPIRED | Access token expired\n",
    ]


@pytest.fixture
def sample_log_file(tmp_path, sample_log_lines):
    p = tmp_path / "sample.log"
    p.write_text("".join(sample_log_lines), encoding="utf-8")
    return p