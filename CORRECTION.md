# Frozen-review correction

The rejected revision contained `tests/unit/test_normalization.py`. That test
read `contracts/CapabilityBond.py`, sliced its source text, and executed the
helpers with Python `exec()`. The frozen reviewer consequently detected the
test as a contract-source candidate, but it had no `gl.Contract` class.

The correction:

1. deletes the source-executing unit helper;
2. migrates reproducibility and normalized validator-disagreement coverage into
   `tests/direct/test_capabilitybond.py` using the standard GenLayer direct VM;
3. adds `npm run check:discovery`, which requires exactly one Python file under
   `contracts/` and rejects direct tests that execute contract source;
4. passes GenVM lint/schema validation, six direct tests and TypeScript checks;
5. redeploys the exact repository contract and verifies its on-chain SHA-256.

Corrected contract: https://explorer-studio.genlayer.com/address/0x892DB175b67ab8497E6969596ed3bfb4DEA708AB

Corrected deployment: https://explorer-studio.genlayer.com/tx/0x90df15d468d865f8bb1ff141c64403f282b0eda82bd9542d8929156cd487c0d4

Source SHA-256: `2516f94ac9e72d2bea14ecfb2e542e826fc99e89132995cf3ebbf2310b4345a2`
