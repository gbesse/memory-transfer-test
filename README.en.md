# memory-transfer-test

## New: Hindsight export receipt

**“Recallable observations disappeared from my memory export.”** [Hindsight #5419](https://github.com/vectorize-io/hindsight/issues/5419) describes observations with deleted sources that are omitted from `export-bank`. `export_receipt.py` compares IDs in a source snapshot with the `source_id` fields in a Hindsight bank archive’s `observations.json`. It also flags observations whose `source_memory_ids` are missing. It does not change a bank.

```sh
python3 export_receipt.py demo --lang en
psql -v ON_ERROR_STOP=1 -v bank_id=my-bank -Atf examples/export-receipt/source-snapshot.sql > source.json
hindsight-admin export-bank --bank my-bank --output bank.zip
python3 export_receipt.py check --source source.json --archive bank.zip --lang en
```

The synthetic demo shows two source observations, one exported and one missing with an orphaned source. The real check reads a **whole-bank** archive and a JSON snapshot from the same bank; export immediately after the snapshot, preferably without concurrent writes. The read-only SQL assumes `memory_units` is reachable through your `search_path`. Keep the snapshot and archive local because they contain bank data. Exit 0: match; 2: missing observation or orphaned source; 3: comparison impossible without IDs; 1: invalid input. This receipt does not establish the cause of an omission or the quality of a later import.

**Related projects:** [Hindsight #5419](https://github.com/vectorize-io/hindsight/issues/5419) motivates the comparison; [Hindsight](https://github.com/vectorize-io/hindsight) defines the archive format. This independent tool reads `export-bank` ZIP files, with no affiliation or live-instance integration.

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
