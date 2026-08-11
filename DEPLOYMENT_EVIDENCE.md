# Corrected StudioNet deployment evidence

- Contract: `0x892DB175b67ab8497E6969596ed3bfb4DEA708AB`
- Deployment transaction: `0x90df15d468d865f8bb1ff141c64403f282b0eda82bd9542d8929156cd487c0d4`
- Final status: `FINALIZED`
- Consensus: `MAJORITY_AGREE`
- Deployed source SHA-256: `2516f94ac9e72d2bea14ecfb2e542e826fc99e89132995cf3ebbf2310b4345a2`
- Public methods verified: 10

Explorer:

- [Corrected CapabilityBond contract](https://explorer-studio.genlayer.com/address/0x892DB175b67ab8497E6969596ed3bfb4DEA708AB)
- [Corrected deployment transaction](https://explorer-studio.genlayer.com/tx/0x90df15d468d865f8bb1ff141c64403f282b0eda82bd9542d8929156cd487c0d4)

`npm run verify:deployment` fetched the deployed source and schema, normalized
line endings, and verified exact equality with `contracts/CapabilityBond.py`.
`npm run check:discovery` confirms that this is the sole deployable Python
contract source and that tests do not read or execute contract source.

One deployment receipt can show `CONSENSUS_VALIDATOR_QUORUM_REACHED`; that is a
validator canceled after quorum, not a contract execution failure.

## Corrected-deployment state proofs

- [Evidence-backed research profile](https://explorer-studio.genlayer.com/tx/0x8af7bd6088a27f82cbb27d524d7ea9d3542118f3d1477beab43e1f6a90d89926) — finalized, 3 agree / 0 disagree, successful execution.
- [Incident-analysis profile](https://explorer-studio.genlayer.com/tx/0xf122c59411fd4feb8a34b20dd8617892c7f1fd520e0dd4262c7f58bdac41a7d8) — finalized, 3 agree / 0 disagree, successful execution.

These prove deployment and deterministic profile state transitions. They are
not presented as live A2A behavioral challenge attestations.
