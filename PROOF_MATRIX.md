# Proof matrix

| Claim | Evidence | Status |
|---|---|---|
| Contract is deployed on StudioNet | [Deployment transaction](https://explorer-studio.genlayer.com/tx/0x6a477f422c13457928bba953c27e6ee9a16d8daa0ff1e785d93175cc67221d22) | Finalized, majority agree |
| Explorer source matches this repository | `npm run verify:deployment`; SHA-256 `2516f94ac9e72d2bea14ecfb2e542e826fc99e89132995cf3ebbf2310b4345a2` | Verified |
| Reusable research profile can be stored | [Research profile transaction](https://explorer-studio.genlayer.com/tx/0x31129c069a6a71def9ba703ff374026cd95eb5a863b88b27432f03dc342d7260) | Finalized, majority agree, two successful executions |
| A distinct incident-analysis profile can be stored | [Incident profile transaction](https://explorer-studio.genlayer.com/tx/0x811f84181ad99fadc26bcde1dd38304fcc195b744cbd4ccbebc9b796fc273e93) | Finalized, majority agree; remaining validator canceled after quorum |
| Success, transient failure, strikes, forfeiture and recovery state rules work | `tests/direct/test_capabilitybond.py` | Covered by direct-mode tests |
| Challenge selection and normalized verdict invariants work | `tests/unit/test_normalization.py` | Covered by unit tests |
| Deployed schema exposes the documented API | `npm run verify:deployment` | 10 public methods verified |
| Validators independently execute the live A2A/evidence path | Contract source and direct mocked-web tests | Implemented and tested, but not yet demonstrated by a finalized live A2A challenge transaction |

## Evidence boundary

The deployment and profile transactions are genuine on-chain proofs. They do not by themselves demonstrate a live behavioral attestation. A portal submission should add a finalized `challenge_capability` transaction only after registering a bonded claim against a stable public A2A 0.3 endpoint. Error, timeout, or simulated transactions must not be represented as live challenge evidence.
