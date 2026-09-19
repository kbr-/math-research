# Duplicate, rediscovery and topic-view acceptance review

The default `claim_views.py duplicates` threshold (summary-token Jaccard 0.5)
returned **22 pairs**. All 22 were reviewed against exact recorded scopes,
assessments/corrections and targeted source evidence. None warrants merging IDs:
most share a method but differ in source grammar, ranks, field/accuracy, finite
bounds, or proof status. Several are qualified extensions or applications; the
wide-round result explicitly supersedes the earlier wide-move interface.

`candidate-decisions.json` records every pair, reason and source fingerprint.
`candidates.json` preserves the complete original discovery output. `packets.json`
preserves bounded retrieval evidence; this was a metadata scope comparison, not
independent verification of all underlying proofs. Lexical retrieval is incomplete
for paraphrases and never establishes mathematical equivalence.

A separate census found **44 assessments** explicitly using rediscovery/refinement
language. All have dispositions in `explicit-decisions.json`, backed by
`explicit-refinement-inventory.json`. This includes the distribution-identity
rediscovery, rank-two conservativity rediscovery and the separately attributed
pointwise collision-search mechanism. Two keyword matches describe a partition or
proof operation rather than a relationship between mathematical claims. Existing
incoming refinements and already proposed worker edges are distinguished from new
proposals; method/representation improvements are not declared duplicate results.

`relationship-proposals.json` supplies 37 scoped relation proposals. The coordinator
must deduplicate against concurrent worker proposals and refresh affected endpoint
reviews, including the historical status review required by the supersedes edge.
No canonical registry, notebook, original claim text, ID or Git state was changed.

`topics.json` is the complete derived topic map, with all 866 claims assigned.
`resolution-parities.md` is a representative generated topic view containing the
publication theorem. Both were generated through the requested existing tool;
no graph UI or separate metadata source was introduced. `validation.json` records
focused acceptance checks and in-memory schema validation of the edge union.

Reproduction commands and complete output are archived under timing session
`parallel_index_duplicate_review`. Source and report drafting occurred within the
marked reading/coding windows; worker time overlaps other agents and is not a
separate additive wall-clock total for the coordinator's cycle.
