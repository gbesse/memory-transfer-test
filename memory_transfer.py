"""Check semantic invariants after migrating agent memory records."""
import argparse
import json
import re
from pathlib import Path
import sys


def active(records):
    by_id = {item['id']: item for item in records}
    superseded = {item['supersedes'] for item in records if item.get('supersedes')}
    return {identifier: item for identifier, item in by_id.items()
            if item.get('status', 'active') == 'active' and identifier not in superseded}


def retrieve(records, scope, term):
    return sorted(identifier for identifier, item in active(records).items()
                  if item['scope'] == scope and term.lower() in re.findall(r'\w+', item['text'].lower()))


def check(source, destination, probes):
    expected = active(source)
    actual = active(destination)
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    changed = sorted(identifier for identifier in set(expected) & set(actual)
                     if any(expected[identifier].get(key) != actual[identifier].get(key)
                            for key in ('text', 'scope', 'provenance')))
    probe_results = []
    for probe in probes:
        baseline = retrieve(source, probe['scope'], probe['term'])
        migrated = retrieve(destination, probe['scope'], probe['term'])
        probe_results.append({'scope': probe['scope'], 'term': probe['term'],
                              'expected_ids': baseline, 'actual_ids': migrated,
                              'pass': baseline == migrated})
    return {'pass': not (missing or unexpected or changed) and all(p['pass'] for p in probe_results),
            'missing_ids': missing, 'unexpected_ids': unexpected, 'changed_ids': changed,
            'probes': probe_results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('probes', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = json.loads(args.source.read_text())['records']
    destination = json.loads(args.destination.read_text())['records']
    probes = json.loads(args.probes.read_text())['probes']
    report = check(source, destination, probes)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + '\n')
    print(encoded)
    return 0 if report['pass'] else 2


if __name__ == '__main__':
    sys.exit(main())
