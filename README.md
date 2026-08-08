# CapabilityBond

CapabilityBond is a reusable GenLayer proof-of-capability primitive for public
A2A agents. An operator locks GEN behind an explicit skill claim. Permissionless
challengers select an immutable challenge vector after registration and every
validator independently discovers the agent, executes the A2A task, retrieves
cited evidence and evaluates the registered promise.

The contract stores only a normalized consensus record. Free-form reasoning and
raw model prose never control state.

## Why it needs GenLayer

Agent Cards are self-descriptions. CapabilityBond tests observed behavior:

1. Fetch and fingerprint the public Agent Card.
2. Verify identity, advertised skill, public endpoint and A2A JSON-RPC 0.3.
3. Select the challenge from an immutable profile using claim, revision and a
   challenger nonce committed only when the challenge is submitted.
4. Send `message/send` to the card-declared endpoint.
5. Extract the completed task artifact and its citations.
6. Fetch the cited public evidence.
7. Evaluate the immutable promise, profile rubric and vector criteria.
8. Require exact equality of the normalized validator record.

## Failure and recovery model

- `TRANSIENT_*`: stored for audit but does not alter claim status.
- First substantive failure: `SUSPECT`.
- Second consecutive substantive failure: `FAILED`; the bond is forfeited.
- A later pass restores `VERIFIED`, while `has_ever_failed` remains true.
- An active, non-forfeited claim may deactivate and withdraw its bond.

Consumers can compose `is_currently_verified(claim_id)` and
`has_ever_failed(claim_id)` according to their risk tolerance.

## Deliberate v1 scope

The first version supports public, unauthenticated A2A JSON-RPC 0.3 agents that
return a synchronous completed task/message with text or structured data and up
to four public HTTPS citations. Streaming, authentication, private evidence and
arbitrary A2A protocol versions are out of scope rather than weakly simulated.

## Validate

```powershell
genvm-lint check contracts\CapabilityBond.py --json
python -m pytest tests\unit tests\direct -q
```

## Standards context

- A2A specification: https://a2a-protocol.org/v0.3.0/specification/
- ERC-8004: https://eips.ethereum.org/EIPS/eip-8004
- GenLayer equivalence principle: https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle

## License

MIT
