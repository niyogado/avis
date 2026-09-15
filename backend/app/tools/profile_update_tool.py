"""CLI utility to request an authorized profile update from the AVIS backend.

Usage examples:
  python -m app.tools.profile_update_tool --token "<JWT>" --full_name "Jane Doe" --headline "Data Scientist"

This tool only sends fields explicitly provided on the command line and will not invent
or overwrite fields that were not supplied. It talks to the `/api/profile` endpoint.
"""
from __future__ import annotations

import argparse
import sys
import json
from typing import Dict, Any
import requests


ALLOWED_FIELDS = {"full_name", "headline", "summary", "location"}


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for field in ALLOWED_FIELDS:
        value = getattr(args, field, None)
        if value is not None:
            payload[field] = value
    return payload


def request_profile_update(base_url: str, token: str, payload: Dict[str, Any]) -> requests.Response:
    url = base_url.rstrip("/") + "/api/profile/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return requests.put(url, headers=headers, json=payload, timeout=15)


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Request an authorized profile update against the AVIS backend")
    p.add_argument("--token", required=True, help="JWT access token with profile scope")
    p.add_argument("--base-url", default="http://localhost:8000", help="Base URL of the backend (default: http://localhost:8000)")
    p.add_argument("--full_name", help="Full name to set on the profile")
    p.add_argument("--headline", help="Headline to set on the profile")
    p.add_argument("--summary", help="Summary / about text to set on the profile")
    p.add_argument("--location", help="Location to set on the profile")
    p.add_argument("--print-json", action="store_true", help="Print the payload as JSON and exit (dry-run)")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    payload = build_payload(args)

    if not payload:
        print("No profile fields supplied. Nothing to update.")
        return 2

    if args.print_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    try:
        resp = request_profile_update(args.base_url, args.token, payload)
    except Exception as exc:  # Keep network errors visible to the caller
        print(f"Request failed: {exc}")
        return 3

    try:
        body = resp.json()
    except Exception:
        body = resp.text

    print(f"Status: {resp.status_code}")
    print(json.dumps(body, indent=2, ensure_ascii=False) if isinstance(body, (dict, list)) else body)
    return 0 if resp.ok else 4


if __name__ == "__main__":
    raise SystemExit(main())
