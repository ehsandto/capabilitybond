# Corrected Intelligent Contract submission

## Title

CapabilityBond — Bonded Behavioral Proofs for A2A Agents

## Description

CapabilityBond is a reusable GenLayer proof-of-capability primitive for public A2A agents. Operators lock GEN behind a skill claim linked to an immutable Agent Card URL and challenge profile. Permissionless challengers reveal a nonce, selecting a profile vector. Validators independently fetch and fingerprint the Agent Card, verify the advertised skill and JSON-RPC endpoint, send the same live A2A task, retrieve cited evidence and evaluate the registered promise, rubric and criteria. Consensus requires exact equality of normalized identity, protocol, task, evidence, verdict and failure fields; prose never controls state. Transient outages do not slash. One substantive failure marks SUSPECT; two mark FAILED and forfeit the bond, while recovery preserves failure history. The frozen-review source-executing unit helper was removed, its coverage migrated to standard direct tests, and a discovery guard verifies CapabilityBond.py is the sole deployable source. The corrected Explorer source exactly matches the repository.

## Evidence

- Repository: https://github.com/ehsandto/capabilitybond
- Corrected contract: https://explorer-studio.genlayer.com/address/0x892DB175b67ab8497E6969596ed3bfb4DEA708AB
- Deployment: https://explorer-studio.genlayer.com/tx/0x90df15d468d865f8bb1ff141c64403f282b0eda82bd9542d8929156cd487c0d4
- Research profile: https://explorer-studio.genlayer.com/tx/0x8af7bd6088a27f82cbb27d524d7ea9d3542118f3d1477beab43e1f6a90d89926
- Incident profile: https://explorer-studio.genlayer.com/tx/0xf122c59411fd4feb8a34b20dd8617892c7f1fd520e0dd4262c7f58bdac41a7d8
