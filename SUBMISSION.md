# Intelligent Contract submission

**Title:** CapabilityBond - Behavioral Proof for A2A Agents

**Description:**

CapabilityBond is a reusable GenLayer proof-of-capability primitive for public A2A agents. Operators lock GEN behind an explicit skill claim linked to an immutable Agent Card URL and challenge profile. Permissionless challengers reveal a nonce after registration, selecting one profile vector. Every validator independently fetches and fingerprints the Agent Card, verifies the advertised skill and JSON-RPC endpoint, sends the same live A2A task, retrieves cited evidence, and evaluates the registered promise, rubric and vector criteria. Consensus requires exact equality of the normalized identity, protocol, task, evidence, verdict and failure fields; free-form reasoning never controls state. Transient outages do not slash. One substantive failure marks SUSPECT, two mark FAILED and forfeit the bond, while later recovery preserves permanent failure history. Two composable gates support normal and high-risk consumers.
