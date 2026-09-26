# memory-transfer-test

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

## Scope

The MVP compares normalized exports, not vendor APIs or vector-search quality. Probe retrieval uses a scope-aware exact-term search. Write export adapters for your two stores, then review the report before deleting the source.


MIT licensed. Store adapters are welcome.
