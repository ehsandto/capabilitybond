# StudioNet deployment evidence

- Contract: `0xB6CBe79A392f8205F93a41b5c66771306fbb0BFB`
- Deployment transaction: `0x6a477f422c13457928bba953c27e6ee9a16d8daa0ff1e785d93175cc67221d22`
- Final status: `FINALIZED`
- Consensus result: `MAJORITY_AGREE`
- Deployed source SHA-256: `2516f94ac9e72d2bea14ecfb2e542e826fc99e89132995cf3ebbf2310b4345a2`

Explorer links:

- [CapabilityBond contract](https://explorer-studio.genlayer.com/address/0xB6CBe79A392f8205F93a41b5c66771306fbb0BFB)
- [Deployment transaction](https://explorer-studio.genlayer.com/tx/0x6a477f422c13457928bba953c27e6ee9a16d8daa0ff1e785d93175cc67221d22)

`npm run verify:deployment` fetched the deployed source and schema from StudioNet, normalized line endings, and verified exact equality with the repository contract. The schema exposes all 10 documented public methods.

One receipt entry is marked `ERROR` only because that validator was canceled after the network had already reached quorum. Its GenVM error code is `CONSENSUS_VALIDATOR_QUORUM_REACHED`; it is not a contract execution failure.

## Finalized state-transition proofs

These independent transactions exercised `register_profile` against the deployed contract and finalized with `MAJORITY_AGREE`. The stored profiles use different reusable capability policies and challenge-vector sets.

- Evidence-backed research profile: [transaction `0x31129c…7260`](https://explorer-studio.genlayer.com/tx/0x31129c069a6a71def9ba703ff374026cd95eb5a863b88b27432f03dc342d7260) — two validator executions succeeded.
- Incident-analysis profile: [transaction `0x811f84…3e93`](https://explorer-studio.genlayer.com/tx/0x811f84181ad99fadc26bcde1dd38304fcc195b744cbd4ccbebc9b796fc273e93) — one execution succeeded and the remaining validator was canceled after quorum (`CONSENSUS_VALIDATOR_QUORUM_REACHED`).

These prove deployment and deterministic state transitions. They are not presented as live A2A behavioral challenge attestations; that stronger evidence requires a public A2A 0.3 agent endpoint and a bonded claim.
