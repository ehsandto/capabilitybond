import json


VECTORS = json.dumps([
    {"id": "origin-a", "prompt": "Research product A origin", "criteria": "Return manufacturer and country with support", "minimum_citations": 1},
    {"id": "origin-b", "prompt": "Research product B origin", "criteria": "Return manufacturer and country with support", "minimum_citations": 1},
])


def _deploy_claim(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/CapabilityBond.py")
    direct_vm.sender = direct_alice
    contract.register_profile("research-v1", "Research profile", "Evidence-backed product origin", VECTORS)
    direct_vm.value = 100
    contract.register_claim(
        "agent-origin", "https://agent.example.com/.well-known/agent-card.json",
        "Origin Research Agent", "verify_product_origin",
        "Return manufacturer, country of origin and supporting citations", "research-v1",
    )
    direct_vm.value = 0
    return contract


def _mock_success(direct_vm):
    card = {
        "protocolVersion": "0.3.0", "name": "Origin Research Agent",
        "url": "https://agent.example.com/a2a", "preferredTransport": "JSONRPC",
        "skills": [{"id": "verify_product_origin", "name": "Origin", "description": "Research origin", "tags": ["research"]}],
    }
    response = {
        "jsonrpc": "2.0", "id": "ignored",
        "result": {"status": {"state": "completed"}, "artifacts": [{"parts": [{"data": {
            "manufacturer": "Acme", "country": "US",
            "citations": [{"url": "https://evidence.example.com/product-a"}],
        }}]}]},
    }
    direct_vm.mock_web(r".*well-known/agent-card\.json.*", {"status": 200, "body": json.dumps(card)})
    direct_vm.mock_web(r".*agent\.example\.com/a2a.*", {
        "response": {"status": 200, "headers": {"Content-Type": "application/json"},
                     "body": json.dumps(response).encode()},
        "method": "POST",
    })
    direct_vm.mock_web(r".*evidence\.example\.com/product-a.*", {"status": 200, "body": "Acme manufactures product A in the United States."})
    direct_vm.mock_llm(r".*validating an autonomous agent capability test.*", json.dumps({
        "required_outputs_present": True, "evidence_supports_output": True,
        "semantic_pass": True, "score_bucket": "PASS", "failure_class": "NONE",
    }))


def test_profile_and_bonded_claim_state(direct_vm, direct_deploy, direct_alice):
    contract = _deploy_claim(direct_vm, direct_deploy, direct_alice)
    claim = contract.get_claim("agent-origin")
    assert claim["bond"] == 100
    assert claim["status"] == "UNVERIFIED"
    assert claim["has_ever_failed"] is False


def test_successful_live_challenge_opens_verified_gate(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy_claim(direct_vm, direct_deploy, direct_alice)
    _mock_success(direct_vm)
    direct_vm.sender = direct_bob
    record = contract.challenge_capability("agent-origin", "challenge-one", "unpredictable-nonce-1")
    assert record["failure_class"] == "NONE"
    assert record["score_bucket"] == "PASS"
    assert record["resulting_status"] == "VERIFIED"
    assert contract.is_currently_verified("agent-origin") is True
    assert contract.has_ever_failed("agent-origin") is False


def test_transient_failure_does_not_change_claim_state(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy_claim(direct_vm, direct_deploy, direct_alice)
    direct_vm.mock_web(r".*well-known/agent-card\.json.*", {"status": 503, "body": ""})
    direct_vm.sender = direct_bob
    record = contract.challenge_capability("agent-origin", "challenge-transient", "unpredictable-nonce-2")
    assert record["score_bucket"] == "TRANSIENT"
    assert record["resulting_status"] == "UNVERIFIED"
    assert contract.get_claim("agent-origin")["consecutive_failures"] == 0


def test_two_substantive_failures_forfeit_bond_and_preserve_history(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy_claim(direct_vm, direct_deploy, direct_alice)
    card = {
        "protocolVersion": "0.3.0", "name": "Origin Research Agent",
        "url": "https://agent.example.com/a2a", "preferredTransport": "JSONRPC", "skills": [],
    }
    direct_vm.mock_web(r".*well-known/agent-card\.json.*", {"status": 200, "body": json.dumps(card)})
    direct_vm.sender = direct_bob
    first = contract.challenge_capability("agent-origin", "challenge-fail-one", "unpredictable-nonce-3")
    second = contract.challenge_capability("agent-origin", "challenge-fail-two", "unpredictable-nonce-4")
    assert first["resulting_status"] == "SUSPECT"
    assert second["resulting_status"] == "FAILED"
    claim = contract.get_claim("agent-origin")
    assert claim["bond_forfeited"] is True
    assert contract.has_ever_failed("agent-origin") is True
    assert contract.is_currently_verified("agent-origin") is False


def test_nonce_bound_vector_selection_is_reproducible(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy_claim(direct_vm, direct_deploy, direct_alice)
    _mock_success(direct_vm)
    direct_vm.sender = direct_bob
    snapshot = direct_vm.snapshot()
    first = contract.challenge_capability("agent-origin", "challenge-repeat", "fixed-public-nonce")
    direct_vm.revert(snapshot)
    second = contract.challenge_capability("agent-origin", "challenge-repeat", "fixed-public-nonce")
    assert first["vector_id"] == second["vector_id"]
    assert first["score_bucket"] == second["score_bucket"]


def test_validator_rejects_substantively_different_normalized_record(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy_claim(direct_vm, direct_deploy, direct_alice)
    _mock_success(direct_vm)
    direct_vm.sender = direct_bob
    contract.challenge_capability("agent-origin", "challenge-validator", "validator-nonce")

    direct_vm.clear_mocks()
    card = {
        "protocolVersion": "0.3.0", "name": "Origin Research Agent",
        "url": "https://agent.example.com/a2a", "preferredTransport": "JSONRPC", "skills": [],
    }
    direct_vm.mock_web(r".*well-known/agent-card\.json.*", {"status": 200, "body": json.dumps(card)})
    assert direct_vm.run_validator() is False
