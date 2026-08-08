from pathlib import Path
from types import SimpleNamespace


SOURCE = (Path(__file__).parents[2] / "contracts" / "CapabilityBond.py").read_text(encoding="utf-8")
BEFORE_CONTRACT = SOURCE.split("class CapabilityBond", 1)[0]
HELPERS = BEFORE_CONTRACT.split("@gl.evm.contract_interface", 1)[0] + "def _clean" + BEFORE_CONTRACT.split("def _clean", 1)[1]
HELPERS = HELPERS.replace("from genlayer import *", "")
MODULE = type("Helpers", (), {})()
MODULE.gl = SimpleNamespace(vm=SimpleNamespace(UserError=ValueError))
exec(HELPERS, MODULE.__dict__)


def test_vector_selection_is_reproducible_and_nonce_bound():
    profile = {"profile_id": "p", "vectors": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}
    one = MODULE._select_vector(profile, "claim", 1, "nonce-value-one")
    two = MODULE._select_vector(profile, "claim", 1, "nonce-value-one")
    assert one == two


def test_valid_pass_record_requires_all_critical_gates():
    claim = {"claim_id": "claim"}
    vector = {"id": "vector"}
    record = {
        "claim_id": "claim", "challenge_id": "challenge", "vector_id": "vector",
        "score_bucket": "PASS", "failure_class": "NONE", "transient": False,
        "semantic_pass": True, "agent_card_match": True, "skill_declared": True,
        "protocol_conformant": True, "task_completed": True,
        "required_outputs_present": True, "evidence_retrievable": True,
        "evidence_supports_output": True,
    }
    assert MODULE._valid_public(record, claim, vector, "challenge") is True
    record["skill_declared"] = False
    assert MODULE._valid_public(record, claim, vector, "challenge") is False


def test_transient_record_must_use_transient_failure_class():
    claim = {"claim_id": "claim"}
    vector = {"id": "vector"}
    record = {"claim_id": "claim", "challenge_id": "challenge", "vector_id": "vector",
              "score_bucket": "TRANSIENT", "failure_class": "TRANSIENT_AGENT_UNAVAILABLE", "transient": True}
    assert MODULE._valid_public(record, claim, vector, "challenge") is True
    record["failure_class"] = "WRONG_ANSWER"
    assert MODULE._valid_public(record, claim, vector, "challenge") is False
