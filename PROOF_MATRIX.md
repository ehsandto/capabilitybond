# Corrected proof matrix

| Claim | Evidence | Status |
|---|---|---|
| Corrected contract deployed | [Deployment](https://explorer-studio.genlayer.com/tx/0x90df15d468d865f8bb1ff141c64403f282b0eda82bd9542d8929156cd487c0d4) | Finalized, majority agree |
| Explorer source matches repository | `npm run verify:deployment`; SHA-256 `2516f94ac9e72d2bea14ecfb2e542e826fc99e89132995cf3ebbf2310b4345a2` | Exact match |
| Only deployable contract is discovered | `npm run check:discovery` | `contracts/CapabilityBond.py` only |
| Research profile stored on corrected contract | [Transaction](https://explorer-studio.genlayer.com/tx/0x8af7bd6088a27f82cbb27d524d7ea9d3542118f3d1477beab43e1f6a90d89926) | Finalized, 3–0, success |
| Incident profile stored on corrected contract | [Transaction](https://explorer-studio.genlayer.com/tx/0xf122c59411fd4feb8a34b20dd8617892c7f1fd520e0dd4262c7f58bdac41a7d8) | Finalized, 3–0, success |
| Success, transient, strikes and forfeiture work | `tests/direct/test_capabilitybond.py` | Direct tests pass |
| Nonce selection is reproducible | `tests/direct/test_capabilitybond.py` | Snapshot/replay test passes |
| Validator rejects conflicting normalized record | `tests/direct/test_capabilitybond.py` | Explicit validator-disagreement test passes |

## Evidence boundary

The profile transactions are genuine on-chain state proofs, not live A2A
behavioral challenges. A behavioral-attestation link should be claimed only after
a stable public A2A 0.3 agent is challenged successfully.
