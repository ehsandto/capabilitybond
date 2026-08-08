# Architecture and invariants

## Trust boundary

- Callers choose an immutable profile, claim and challenge nonce.
- External A2A agents and citation pages provide untrusted evidence.
- Validators independently reproduce the complete test.
- Contract state changes only from an exact normalized consensus record.

## Consensus invariant

A pass is valid only when identity, skill, protocol, task completion, required
outputs, evidence retrieval and evidence support are all true. `failure_class`,
`score_bucket` and `semantic_pass` are cross-checked before storage. Validators
compare the entire normalized record byte-for-byte; prose is excluded.

## Challenge selection

`sha256(profile_id | claim_id | next_revision | challenger_nonce) % N` selects
one immutable profile vector. The operator cannot know the nonce at claim
registration. Historical challenges store the selected vector and revision.

## Bond semantics

The bond is native GEN received by a payable registration call. Two consecutive
substantive failures permanently forfeit it. Transient infrastructure failures
never increment the strike count. Successful recovery reopens the current gate
but never erases `has_ever_failed`.
