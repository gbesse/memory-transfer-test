"""Check semantic invariants after migrating agent memory records."""
import argparse
import json
import re
from pathlib import Path
import sys


TEXT = {
    'en': {'invalid': 'Invalid migration input; inspect validation_errors in the JSON report.', 'read_error': 'Could not read normalized migration inputs.'},
    'fr': {'invalid': 'Entrée de migration invalide ; consultez validation_errors dans le rapport JSON.', 'read_error': 'Impossible de lire les entrées normalisées de migration.'},
    'es': {'invalid': 'Entrada de migración no válida; consulte validation_errors en el informe JSON.', 'read_error': 'No se pudieron leer las entradas normalizadas de migración.'},
}


def validate_records(records):
    """Validate identity and correction lineage without retaining text in findings.

    A missing superseded target is allowed for compacted exports. Present targets
    must share the correcting record's scope. Deleted corrections still suppress
    old facts: deletion must not resurrect a previously corrected fact.
    """
    if not isinstance(records, list):
        return [{'code': 'records_array_required'}]
    errors, by_id = [], {}
    for index, item in enumerate(records):
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip()
                                            for k in ('id', 'text', 'scope', 'provenance')):
            errors.append({'code': 'record_shape', 'index': index})
            continue
        identifier = item['id']
        if identifier in by_id:
            errors.append({'code': 'duplicate_id', 'id': identifier})
        by_id[identifier] = item
        if item.get('status', 'active') not in ('active', 'deleted'):
            errors.append({'code': 'invalid_status', 'id': identifier})
        if 'supersedes' in item and (not isinstance(item['supersedes'], str) or not item['supersedes'].strip()):
            errors.append({'code': 'invalid_supersedes', 'id': identifier})
    edges = {}
    for identifier, item in by_id.items():
        target = item.get('supersedes')
        if not isinstance(target, str) or target not in by_id:
            continue
        edges[identifier] = target
        if by_id[target]['scope'] != item['scope']:
            errors.append({'code': 'cross_scope_correction', 'id': identifier, 'target': target})
    # Iterative linear-time traversal also handles very long correction histories.
    visited = set()
    for start in sorted(edges):
        path, current = set(), start
        while current in edges and current not in visited:
            if current in path:
                errors.append({'code': 'correction_cycle', 'id': current})
                break
            path.add(current)
            current = edges[current]
        visited.update(path)
    return errors


def active(records):
    errors = validate_records(records)
    if errors:
        raise ValueError('invalid_records')
    by_id = {item['id']: item for item in records}
    superseded = {item['supersedes'] for item in records if item.get('supersedes')}
    return {identifier: item for identifier, item in by_id.items()
            if item.get('status', 'active') == 'active' and identifier not in superseded}


def retrieve(records, scope, term):
    return sorted(identifier for identifier, item in active(records).items()
                  if item['scope'] == scope and term.lower() in re.findall(r'\w+', item['text'].lower()))


def check(source, destination, probes):
    errors = []
    for label, records in (('source', source), ('destination', destination)):
        errors.extend(dict(error, export=label) for error in validate_records(records))
    if not isinstance(probes, list) or any(not isinstance(probe, dict) or
        any(not isinstance(probe.get(k), str) or not probe[k].strip() for k in ('scope', 'term')) for probe in probes):
        errors.append({'code': 'invalid_probes', 'export': 'probes'})
    if errors:
        return {'pass': False, 'input_valid': False, 'validation_errors': errors,
                'missing_ids': [], 'unexpected_ids': [], 'changed_ids': [], 'probes': []}
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
    return {'input_valid': True, 'validation_errors': [], 'pass': not (missing or unexpected or changed) and all(p['pass'] for p in probe_results),
            'missing_ids': missing, 'unexpected_ids': unexpected, 'changed_ids': changed,
            'probes': probe_results}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('probes', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--lang', choices=TEXT, default='en')
    args = parser.parse_args(argv)
    try:
        source = json.loads(args.source.read_text())['records']
        destination = json.loads(args.destination.read_text())['records']
        probes = json.loads(args.probes.read_text())['probes']
    except (OSError, ValueError, KeyError, TypeError):
        print(TEXT[args.lang]['read_error'], file=sys.stderr)
        return 1
    report = check(source, destination, probes)
    if not report['input_valid']:
        print(TEXT[args.lang]['invalid'], file=sys.stderr)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + '\n')
    print(encoded)
    return 0 if report['pass'] else 2


if __name__ == '__main__':
    sys.exit(main())
