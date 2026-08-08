# Security model

- Only public HTTPS Agent Cards, endpoints and citations are fetched; common
  loopback/private IPv4 ranges and credential-bearing URLs are rejected.
- Agent Card identity, skill and JSON-RPC endpoint are independently rechecked.
- Challenge profiles and claims are immutable; only derived status evolves.
- One transient failure cannot slash a bond.
- Exact verdict equality favors safety: unstable agents fail to reach a state
  transition instead of accepting a leader-only opinion.
- Challenger nonces provide post-registration selection, not cryptographic
  randomness. Challengers can choose a vector by grinding; this helps testing
  coverage but must not be represented as unbiased randomness.
- v1 does not support authenticated agents or private citations.
