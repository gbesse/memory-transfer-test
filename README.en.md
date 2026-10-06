# memory-transfer-test

## New check: citations after migration

`python3 citation_migration.py demo --lang en` shows a page still citing `old-1` after transfer to `new-1` in ten seconds (successful demo exits 0). For normalized exports: `python3 citation_migration.py check source.json destination.json remap.json --lang en`. Both exports contain `records: [{id}]` and `pages: [{id, based_on: [id]}]`; `remap.json` maps old to new IDs. It detects missing targets, stale citations and orphans. It does not contact a store and relies on your mapping.

**Related project:** [Hindsight #5298](https://github.com/vectorize-io/hindsight/issues/5298) describes `based_on` citations retaining source IDs after merge import. This CLI checks that symptom in exports; there is no direct Hindsight adapter.

[Français](README.md) · [English](README.en.md) · [Español](README.es.md)

## Related projects and target gap

- [MemMachine](https://github.com/MemMachine/MemMachine) provides persistent memory for agents. Moving to or from such a store should preserve corrections, deletion, scope, and provenance.
- [Agent Memory Benchmark](https://github.com/AlekseiMarchenko/agent-memory-benchmark) already tests recall, conflicts, and selective forgetting across providers. Those behaviors **overlap** with ours. Our MVP targets the different **source → destination migration** case by comparing two exports of the same state.
- **Our angle:** check transfer invariants before cutover. No MemMachine or provider adapter is included yet.

Check that an agent-memory migration preserves active facts, scopes, and provenance without resurrecting corrected or deleted memories. Compare two normalized JSON exports and run scope and term retrieval probes.

## Quick start

Python 3.11+, no external dependencies.

```bash
python3 memory_transfer.py examples/source.json examples/destination-ok.json examples/probes.json
python3 memory_transfer.py examples/source.json examples/destination-bug.json examples/probes.json
python3 -m unittest discover -s tests -v
```

The first command passes. The second exits `2`: it catches a corrected fact returning, a deleted fact returning, and a changed scope. `--output report.json` saves the report. Each record has `id`, `text`, `scope`, `provenance`, with optional `status` and `supersedes`. A probe has `scope` and `term`.

## Example: scope boundary

`python3 -m examples.scope_boundary` compares a correct migration with a copy where the same memory changes scope. The latter also fails team-scoped retrieval probes. Exports are synthetic; no live store is queried.

## Scope

The MVP compares normalized exports, not vendor APIs or vector-search quality. Probe retrieval uses a scope-aware exact-term search. Write export adapters for your two stores, then review the report before deleting the source.


MIT licensed. Store adapters are welcome.
