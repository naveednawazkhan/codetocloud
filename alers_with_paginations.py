#!/usr/bin/env python3
"""
Paginate through Prisma Cloud /v2/alert API and collect all alerts.

Usage:
    export PRISMA_AUTH_TOKEN="<x-redlock-auth JWT>"
    python3 prisma_alerts_paginate.py [--output alerts.json]

The script POSTs to https://api4.prismacloud.io/v2/alert with the same
filters as the captured curl (minus policy.id), then follows the
`nextPageToken` from each response until none is returned.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any

import requests

DEFAULT_URL = "https://api4.prismacloud.io/v2/alert"
DEFAULT_LIMIT = 1000


def build_headers(auth_token: str) -> dict[str, str]:
    return {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://app4.prismacloud.io",
        "referer": "https://app4.prismacloud.io/",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        ),
        "x-prisma-route": "/alerts/overview",
        "x-redlock-auth": auth_token,
    }


def build_payload(limit: int, page_token: str) -> dict[str, Any]:
    return {
        "detailed": False,
        "filters": [
            {"name": "timeRange.type", "operator": "=", "value": "ALERT_OPENED"},
            {"name": "alert.status", "operator": "=", "value": "open"},
            {"name": "policy.type", "operator": "=", "value": "config"},
        ],
        "timeRange": {"type": "to_now", "value": "epoch"},
        "limit": limit,
        "webClient": True,
        "pageToken": page_token,
    }


def paginate(
    url: str,
    auth_token: str,
    limit: int,
    timeout: int,
    max_retries: int,
    sleep_between: float,
) -> list[dict[str, Any]]:
    headers = build_headers(auth_token)
    session = requests.Session()
    all_alerts: list[dict[str, Any]] = []
    page_token = ""
    page_idx = 0

    while True:
        page_idx += 1
        payload = build_payload(limit, page_token)

        attempt = 0
        while True:
            attempt += 1
            try:
                resp = session.post(url, headers=headers, json=payload, timeout=timeout)
            except requests.RequestException as exc:
                if attempt > max_retries:
                    raise
                wait = 2 ** attempt
                print(
                    f"[page {page_idx}] request error: {exc} "
                    f"(retry {attempt}/{max_retries} in {wait}s)",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue

            if resp.status_code in (429, 502, 503, 504) and attempt <= max_retries:
                wait = 2 ** attempt
                print(
                    f"[page {page_idx}] HTTP {resp.status_code}, "
                    f"retry {attempt}/{max_retries} in {wait}s",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue

            if resp.status_code != 200:
                print(
                    f"[page {page_idx}] HTTP {resp.status_code}: {resp.text[:500]}",
                    file=sys.stderr,
                )
                resp.raise_for_status()
            break

        try:
            data = resp.json()
        except json.JSONDecodeError:
            print(f"[page {page_idx}] invalid JSON: {resp.text[:500]}", file=sys.stderr)
            raise

        items = data.get("items") or data.get("alerts") or []
        all_alerts.extend(items)
        next_token = data.get("nextPageToken") or ""

        print(
            f"[page {page_idx}] fetched {len(items)} alerts "
            f"(total={len(all_alerts)}) nextPageToken={'yes' if next_token else 'no'}",
            file=sys.stderr,
        )

        if not next_token:
            break
        page_token = next_token
        if sleep_between > 0:
            time.sleep(sleep_between)

    return all_alerts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Prisma Cloud /v2/alert endpoint")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="page size (default 100)")
    parser.add_argument("--output", "-o", default="alerts.json", help="output JSON file")
    parser.add_argument(
        "--auth-token",
        default=os.environ.get("PRISMA_AUTH_TOKEN", ""),
        help="x-redlock-auth JWT (or set PRISMA_AUTH_TOKEN env var)",
    )
    parser.add_argument("--timeout", type=int, default=60, help="per-request timeout seconds")
    parser.add_argument("--max-retries", type=int, default=5, help="retries on transient errors")
    parser.add_argument(
        "--sleep-between", type=float, default=0.0, help="seconds to sleep between pages"
    )
    args = parser.parse_args()

    if not args.auth_token:
        print(
            "ERROR: x-redlock-auth token missing. "
            "Pass --auth-token or set PRISMA_AUTH_TOKEN env var.",
            file=sys.stderr,
        )
        return 2

    alerts = paginate(
        url=args.url,
        auth_token=args.auth_token,
        limit=args.limit,
        timeout=args.timeout,
        max_retries=args.max_retries,
        sleep_between=args.sleep_between,
    )

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(alerts, fh, indent=2)

    print(f"TOTAL ALERTS: {len(alerts)}")
    print(f"Wrote {len(alerts)} alerts to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
