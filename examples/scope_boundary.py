"""Show how a scope change invalidates a memory transfer."""
import json

from memory_transfer import check

source = [{"id": "m1", "text": "Billing refund approved", "scope": "team-a", "provenance": "case-1"}]
correct = [dict(source[0])]
leaked = [{**source[0], "scope": "team-b"}]
probes = [{"scope": "team-a", "term": "refund"}, {"scope": "team-b", "term": "refund"}]
accepted = check(source, correct, probes)
rejected = check(source, leaked, probes)
assert accepted["pass"] and not rejected["pass"] and rejected["changed_ids"] == ["m1"]
print(json.dumps({"source": "synthetic exports; no memory provider", "same_scope_passes": accepted["pass"], "changed_scope_rejected": not rejected["pass"], "failed_probes": [item["scope"] for item in rejected["probes"] if not item["pass"]]}, sort_keys=True))
