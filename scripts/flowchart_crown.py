#!/usr/bin/env python3
"""Execute or verify the bounded mmdio flowchart semantic crown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from mmdio.flowchart_crown import crown, receipt_json, verify_receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--rendered", type=Path)
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verify:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        verify_receipt(receipt)
        print(json.dumps({"standing": "ALIVE", "replay": "REPLAY_MATCH"}, sort_keys=True))
        return 0

    if args.input is None:
        raise SystemExit("input is required unless --verify is used")

    receipt = crown(args.input.read_text(encoding="utf-8"))
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(receipt_json(receipt), encoding="utf-8")
    if args.rendered is not None:
        args.rendered.parent.mkdir(parents=True, exist_ok=True)
        args.rendered.write_text(receipt["rendered"], encoding="utf-8")
    print(
        json.dumps(
            {
                "standing": receipt["standing"],
                "canonical_sha256": receipt["subject"]["canonical_sha256"],
                "receipt_sha256": receipt["receipt_sha256"],
                "replay": receipt["execution"]["replay"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
