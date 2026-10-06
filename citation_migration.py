#!/usr/bin/env python3
"""Check that page citations were remapped when memory IDs changed."""

import argparse
import json
import sys
from pathlib import Path

TEXT = {
    "en": ("Citation migration", "orphan citation", "expected remapped ID", "healthy"),
    "fr": ("Migration des citations", "citation orpheline", "ID remappé attendu", "sain"),
    "es": ("Migración de citas", "cita huérfana", "ID reasignado esperado", "correcto"),
}


def audit(source, destination, remap):
    source_ids = {row["id"] for row in source["records"]}
    destination_ids = {row["id"] for row in destination["records"]}
    destination_pages = {row["id"]: row for row in destination["pages"]}
    if len(destination_pages) != len(destination["pages"]):
        raise ValueError("duplicate destination page ID")
    findings = []
    for page in source["pages"]:
        target = destination_pages.get(page["id"])
        if target is None:
            findings.append({"page": page["id"], "kind": "missing_page"})
            continue
        actual = set(target["based_on"])
        for old_id in page["based_on"]:
            if old_id not in source_ids:
                findings.append({"page": page["id"], "kind": "invalid_source", "id": old_id})
                continue
            expected = remap.get(old_id)
            if expected is None:
                findings.append({"page": page["id"], "kind": "missing_mapping", "id": old_id})
            elif expected not in destination_ids:
                findings.append({"page": page["id"], "kind": "missing_target", "id": expected})
            elif expected not in actual:
                findings.append({"page": page["id"], "kind": "wrong_citation", "id": old_id,
                                 "expected": expected})
        for cited_id in sorted(actual - destination_ids):
            findings.append({"page": page["id"], "kind": "orphan", "id": cited_id})
    return {"ok": not findings, "pages": len(source["pages"]), "findings": findings}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("demo", "check"))
    ap.add_argument("source", type=Path, nargs="?")
    ap.add_argument("destination", type=Path, nargs="?")
    ap.add_argument("remap", type=Path, nargs="?")
    ap.add_argument("--lang", choices=TEXT, default="en")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.command == "demo":
            source = {"records": [{"id": "old-1"}],
                      "pages": [{"id": "guide", "based_on": ["old-1"]}]}
            destination = {"records": [{"id": "new-1"}],
                           "pages": [{"id": "guide", "based_on": ["old-1"]}]}
            remap = {"old-1": "new-1"}
        else:
            if not all((args.source, args.destination, args.remap)):
                ap.error("check requires SOURCE.json DESTINATION.json REMAP.json")
            source = json.loads(args.source.read_text())
            destination = json.loads(args.destination.read_text())
            remap = json.loads(args.remap.read_text())
        result = audit(source, destination, remap)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        title, orphan, expected, healthy = TEXT[args.lang]
        print(title)
        if result["ok"]:
            print(healthy)
        for row in result["findings"]:
            detail = f"; {expected}: {row['expected']}" if "expected" in row else ""
            print(f"{row['page']}: {orphan} ({row['kind']}: {row.get('id', '?')}){detail}")
    return 0 if (not result["ok"] if args.command == "demo" else result["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
