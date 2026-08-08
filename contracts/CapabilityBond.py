# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""CapabilityBond: consensus-backed behavioral proof for public A2A agents."""

from genlayer import *
import hashlib
import json
import re
from urllib.parse import urlsplit

POLICY_VERSION = "capabilitybond-a2a-research-v1"
MAX_ID = 80
MAX_URL = 500
MAX_TEXT = 3000
MAX_VECTORS = 64
MAX_CITATIONS = 4
ERR_EXPECTED = "[EXPECTED]"


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


def _clean(value, limit: int) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _identifier(value: str, label: str) -> str:
    value = _clean(value, MAX_ID).lower()
    if len(value) < 3 or re.fullmatch(r"[a-z0-9][a-z0-9._-]*", value) is None:
        raise gl.vm.UserError(f"{ERR_EXPECTED} invalid {label}")
    return value


def _public_https(url: str) -> bool:
    try:
        parsed = urlsplit(str(url))
        host = str(parsed.hostname or "").lower()
    except Exception:
        return False
    if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment:
        return False
    if host == "localhost" or host.endswith(".local") or host.endswith(".internal"):
        return False
    private = (r"127(?:\.[0-9]{1,3}){3}", r"10(?:\.[0-9]{1,3}){3}",
               r"192\.168(?:\.[0-9]{1,3}){2}", r"169\.254(?:\.[0-9]{1,3}){2}")
    if any(re.fullmatch(pattern, host) for pattern in private):
        return False
    match = re.fullmatch(r"172\.([0-9]{1,2})(?:\.[0-9]{1,3}){2}", host)
    return match is None or not (16 <= int(match.group(1)) <= 31)


def _canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _fingerprint(value) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _parse_profiles(vectors_json: str) -> list:
    try:
        vectors = json.loads(vectors_json)
    except Exception:
        raise gl.vm.UserError(f"{ERR_EXPECTED} invalid vectors JSON")
    if not isinstance(vectors, list) or len(vectors) < 2 or len(vectors) > MAX_VECTORS:
        raise gl.vm.UserError(f"{ERR_EXPECTED} profile requires 2-{MAX_VECTORS} vectors")
    normalized = []
    seen = {}
    for raw in vectors:
        if not isinstance(raw, dict):
            raise gl.vm.UserError(f"{ERR_EXPECTED} vector must be an object")
        vector_id = _identifier(raw.get("id", ""), "vector id")
        if vector_id in seen:
            raise gl.vm.UserError(f"{ERR_EXPECTED} duplicate vector id")
        prompt = _clean(raw.get("prompt", ""), MAX_TEXT)
        criteria = _clean(raw.get("criteria", ""), MAX_TEXT)
        minimum_citations = raw.get("minimum_citations", 0)
        if not prompt or not criteria or isinstance(minimum_citations, bool):
            raise gl.vm.UserError(f"{ERR_EXPECTED} incomplete vector")
        minimum_citations = int(minimum_citations)
        if minimum_citations < 0 or minimum_citations > MAX_CITATIONS:
            raise gl.vm.UserError(f"{ERR_EXPECTED} invalid minimum citations")
        seen[vector_id] = True
        normalized.append({"id": vector_id, "prompt": prompt, "criteria": criteria,
                           "minimum_citations": minimum_citations})
    normalized.sort(key=lambda item: item["id"])
    return normalized


def _select_vector(profile: dict, claim_id: str, revision: int, nonce: str) -> dict:
    nonce = _clean(nonce, 160)
    if len(nonce) < 8:
        raise gl.vm.UserError(f"{ERR_EXPECTED} challenge nonce is too short")
    seed = f"{profile['profile_id']}|{claim_id}|{revision}|{nonce}"
    index = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % len(profile["vectors"])
    return profile["vectors"][index]


def _get_json(url: str):
    try:
        response = gl.nondet.web.get(url, headers={"Accept": "application/json", "User-Agent": "CapabilityBond/1"})
    except Exception:
        return None, "TRANSIENT_CARD_UNAVAILABLE"
    status = int(getattr(response, "status", 0) or 0)
    if status == 429 or status >= 500 or status == 0:
        return None, "TRANSIENT_CARD_UNAVAILABLE"
    if status < 200 or status >= 300:
        return None, "CARD_HTTP_ERROR"
    body = getattr(response, "body", b"")
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="ignore")
    try:
        return json.loads(str(body)), "NONE"
    except Exception:
        return None, "CARD_INVALID_JSON"


def _post_json(url: str, payload: dict):
    try:
        response = gl.nondet.web.post(
            url,
            body=_canonical_json(payload).encode("utf-8"),
            headers={"Accept": "application/json", "Content-Type": "application/json",
                     "User-Agent": "CapabilityBond/1", "A2A-Version": "0.3"},
        )
    except Exception:
        return None, "TRANSIENT_AGENT_UNAVAILABLE"
    status = int(getattr(response, "status", 0) or 0)
    if status == 429 or status >= 500 or status == 0:
        return None, "TRANSIENT_AGENT_UNAVAILABLE"
    if status < 200 or status >= 300:
        return None, "A2A_HTTP_ERROR"
    body = getattr(response, "body", b"")
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="ignore")
    try:
        return json.loads(str(body)), "NONE"
    except Exception:
        return None, "A2A_INVALID_JSON"


def _card_details(card: dict, claim: dict) -> dict:
    if not isinstance(card, dict):
        return {"agent_card_match": False, "skill_declared": False, "protocol_conformant": False,
                "endpoint": "", "card_fingerprint": ""}
    skills = card.get("skills", [])
    declared = any(isinstance(skill, dict) and str(skill.get("id", "")) == claim["skill_id"]
                   for skill in skills if isinstance(skills, list))
    endpoint = _clean(card.get("url", ""), MAX_URL)
    transport = str(card.get("preferredTransport", card.get("preferred_transport", "JSONRPC"))).upper()
    protocol = str(card.get("protocolVersion", card.get("protocol_version", "")))
    identity = _clean(card.get("name", ""), 160)
    return {
        "agent_card_match": identity == claim["agent_identity"],
        "skill_declared": declared,
        "protocol_conformant": bool(_public_https(endpoint) and transport == "JSONRPC" and protocol.startswith("0.3")),
        "endpoint": endpoint,
        "card_fingerprint": _fingerprint(card),
    }


def _extract_agent_output(response: dict):
    if not isinstance(response, dict) or str(response.get("jsonrpc", "")) != "2.0" or "error" in response:
        return None
    result = response.get("result")
    if not isinstance(result, dict):
        return None
    candidate_parts = []
    status = result.get("status", {})
    state = str(status.get("state", "")) if isinstance(status, dict) else ""
    artifacts = result.get("artifacts", [])
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if isinstance(artifact, dict) and isinstance(artifact.get("parts"), list):
                candidate_parts.extend(artifact["parts"])
    if isinstance(result.get("parts"), list):
        candidate_parts.extend(result["parts"])
    texts = []
    data_items = []
    for part in candidate_parts:
        if not isinstance(part, dict):
            continue
        if isinstance(part.get("text"), str):
            texts.append(part["text"])
        if isinstance(part.get("data"), dict):
            data_items.append(part["data"])
    text = "\n".join(texts)[:12000]
    structured = data_items[0] if data_items else None
    if structured is None and text:
        try:
            structured = json.loads(text)
        except Exception:
            structured = {"answer": text, "citations": []}
    completed = state.lower() in ("completed", "task_state_completed", "")
    return {"completed": completed, "structured": structured, "text": text}


def _citations_from_output(output: dict) -> list:
    structured = output.get("structured") if isinstance(output, dict) else None
    raw = structured.get("citations", []) if isinstance(structured, dict) else []
    result = []
    for item in raw if isinstance(raw, list) else []:
        url = _clean(item.get("url", "") if isinstance(item, dict) else item, MAX_URL)
        if url and _public_https(url) and url not in result:
            result.append(url)
        if len(result) == MAX_CITATIONS:
            break
    return result


def _fetch_evidence(urls: list):
    evidence = []
    for url in urls:
        try:
            response = gl.nondet.web.get(url, headers={"User-Agent": "CapabilityBond/1"})
            status = int(getattr(response, "status", 0) or 0)
            body = getattr(response, "body", b"")
            if isinstance(body, bytes):
                body = body.decode("utf-8", errors="ignore")
            evidence.append({"url": url, "status": status, "content": _clean(body, 5000)})
        except Exception:
            evidence.append({"url": url, "status": 0, "content": ""})
    return evidence


def _semantic_verdict(claim: dict, profile: dict, vector: dict, output: dict, evidence: list) -> dict:
    prompt = f"""You are validating an autonomous agent capability test.
Registered promise: {claim['promise']}
Profile rubric: {profile['rubric']}
Challenge: {vector['prompt']}
Success criteria: {vector['criteria']}
Minimum citations: {vector['minimum_citations']}
Agent output: {_canonical_json(output.get('structured'))[:10000]}
Retrieved evidence: {_canonical_json(evidence)[:16000]}
Return JSON only with exactly these fields:
{{"required_outputs_present":true|false,"evidence_supports_output":true|false,"semantic_pass":true|false,"score_bucket":"PASS"|"FAIL","failure_class":"NONE"|"MISSING_OUTPUT"|"INSUFFICIENT_EVIDENCE"|"UNSUPPORTED_CLAIM"|"WRONG_ANSWER"}}
PASS only when every success criterion is satisfied and retrieved evidence supports the answer."""
    try:
        result = gl.nondet.exec_prompt(prompt, response_format="json")
    except Exception:
        return {"transient": True, "failure_class": "TRANSIENT_EVALUATOR"}
    allowed_failures = ("NONE", "MISSING_OUTPUT", "INSUFFICIENT_EVIDENCE", "UNSUPPORTED_CLAIM", "WRONG_ANSWER")
    failure = str(result.get("failure_class", "WRONG_ANSWER"))
    if failure not in allowed_failures:
        failure = "WRONG_ANSWER"
    semantic_pass = bool(result.get("semantic_pass") is True and failure == "NONE")
    return {
        "transient": False,
        "required_outputs_present": result.get("required_outputs_present") is True,
        "evidence_supports_output": result.get("evidence_supports_output") is True,
        "semantic_pass": semantic_pass,
        "score_bucket": "PASS" if semantic_pass else "FAIL",
        "failure_class": "NONE" if semantic_pass else failure,
    }


def _run_challenge(claim: dict, profile: dict, vector: dict, challenge_id: str) -> dict:
    card, error = _get_json(claim["agent_card_url"])
    if error != "NONE":
        return _transient_or_failure(claim, vector, challenge_id, error)
    details = _card_details(card, claim)
    if not details["agent_card_match"] or not details["skill_declared"] or not details["protocol_conformant"]:
        failure = "CARD_MISMATCH" if not details["agent_card_match"] else (
            "SKILL_NOT_DECLARED" if not details["skill_declared"] else "PROTOCOL_NONCONFORMANT")
        return _base_record(claim, vector, challenge_id, details, failure, False)
    request = {
        "jsonrpc": "2.0", "id": challenge_id, "method": "message/send",
        "params": {"message": {"role": "user", "messageId": challenge_id,
                                "parts": [{"kind": "text", "text": vector["prompt"]}]},
                   "metadata": {"capabilityBondClaim": claim["claim_id"], "skillId": claim["skill_id"]}},
    }
    response, error = _post_json(details["endpoint"], request)
    if error != "NONE":
        return _transient_or_failure(claim, vector, challenge_id, error, details)
    output = _extract_agent_output(response)
    if output is None or not output["completed"]:
        return _base_record(claim, vector, challenge_id, details, "TASK_NOT_COMPLETED", False)
    citations = _citations_from_output(output)
    evidence = _fetch_evidence(citations)
    retrievable = sum(1 for item in evidence if 200 <= item["status"] < 300 and item["content"])
    if retrievable < int(vector["minimum_citations"]):
        record = _base_record(claim, vector, challenge_id, details, "INSUFFICIENT_EVIDENCE", False)
        record["task_completed"] = True
        record["citation_count"] = len(citations)
        record["retrievable_citation_count"] = retrievable
        return record
    verdict = _semantic_verdict(claim, profile, vector, output, evidence)
    if verdict.get("transient") is True:
        return _transient_or_failure(claim, vector, challenge_id, verdict["failure_class"], details)
    record = _base_record(claim, vector, challenge_id, details, verdict["failure_class"], verdict["semantic_pass"])
    record.update({
        "task_completed": True,
        "citation_count": len(citations),
        "retrievable_citation_count": retrievable,
        "required_outputs_present": verdict["required_outputs_present"],
        "evidence_retrievable": retrievable >= int(vector["minimum_citations"]),
        "evidence_supports_output": verdict["evidence_supports_output"],
        "semantic_pass": verdict["semantic_pass"],
        "score_bucket": verdict["score_bucket"],
    })
    return record


def _base_record(claim: dict, vector: dict, challenge_id: str, details: dict, failure: str, passed: bool) -> dict:
    return {
        "claim_id": claim["claim_id"], "challenge_id": challenge_id, "vector_id": vector["id"],
        "card_fingerprint": details.get("card_fingerprint", ""),
        "agent_card_match": details.get("agent_card_match", False),
        "skill_declared": details.get("skill_declared", False),
        "protocol_conformant": details.get("protocol_conformant", False),
        "task_completed": False, "required_outputs_present": False,
        "citation_count": 0, "retrievable_citation_count": 0,
        "evidence_retrievable": False, "evidence_supports_output": False,
        "semantic_pass": passed, "score_bucket": "PASS" if passed else "FAIL",
        "failure_class": failure, "transient": False,
    }


def _transient_or_failure(claim: dict, vector: dict, challenge_id: str, error: str, details=None) -> dict:
    transient = error.startswith("TRANSIENT_")
    record = _base_record(claim, vector, challenge_id, details or {}, error, False)
    record["transient"] = transient
    record["score_bucket"] = "TRANSIENT" if transient else "FAIL"
    return record


def _valid_public(record: dict, claim: dict, vector: dict, challenge_id: str) -> bool:
    if not isinstance(record, dict):
        return False
    if record.get("claim_id") != claim["claim_id"] or record.get("challenge_id") != challenge_id:
        return False
    if record.get("vector_id") != vector["id"]:
        return False
    if record.get("score_bucket") not in ("PASS", "FAIL", "TRANSIENT"):
        return False
    if record.get("transient") is True:
        return str(record.get("failure_class", "")).startswith("TRANSIENT_") and record.get("score_bucket") == "TRANSIENT"
    if record.get("semantic_pass") is True:
        return bool(record.get("score_bucket") == "PASS" and record.get("failure_class") == "NONE"
                    and record.get("agent_card_match") is True and record.get("skill_declared") is True
                    and record.get("protocol_conformant") is True and record.get("task_completed") is True
                    and record.get("required_outputs_present") is True and record.get("evidence_retrievable") is True
                    and record.get("evidence_supports_output") is True)
    return record.get("score_bucket") == "FAIL" and record.get("failure_class") != "NONE"


class CapabilityBond(gl.Contract):
    profile_json: TreeMap[str, str]
    claim_json: TreeMap[str, str]
    challenge_json: TreeMap[str, str]
    profile_ids: DynArray[str]
    claim_ids: DynArray[str]
    challenge_ids: DynArray[str]
    claim_owner: TreeMap[str, Address]
    revision_by_claim: TreeMap[str, u256]
    profile_count: u256
    claim_count: u256
    challenge_count: u256

    def __init__(self) -> None:
        self.profile_count = u256(0)
        self.claim_count = u256(0)
        self.challenge_count = u256(0)

    @gl.public.write
    def register_profile(self, profile_id: str, name: str, rubric: str, vectors_json: str) -> dict:
        profile_id = _identifier(profile_id, "profile id")
        if self.profile_json.get(profile_id, ""):
            raise gl.vm.UserError(f"{ERR_EXPECTED} profile already exists")
        profile = {"profile_id": profile_id, "name": _clean(name, 120), "rubric": _clean(rubric, MAX_TEXT),
                   "vectors": _parse_profiles(vectors_json), "policy_version": POLICY_VERSION,
                   "creator": str(gl.message.sender_address)}
        if not profile["name"] or not profile["rubric"]:
            raise gl.vm.UserError(f"{ERR_EXPECTED} name and rubric are required")
        self.profile_json[profile_id] = _canonical_json(profile)
        self.profile_ids.append(profile_id)
        self.profile_count = u256(int(self.profile_count) + 1)
        return profile

    @gl.public.write.payable
    def register_claim(self, claim_id: str, agent_card_url: str, agent_identity: str,
                       skill_id: str, promise: str, profile_id: str) -> dict:
        claim_id = _identifier(claim_id, "claim id")
        profile_id = _identifier(profile_id, "profile id")
        if self.claim_json.get(claim_id, ""):
            raise gl.vm.UserError(f"{ERR_EXPECTED} claim already exists")
        if not self.profile_json.get(profile_id, ""):
            raise gl.vm.UserError(f"{ERR_EXPECTED} profile not found")
        if not _public_https(agent_card_url):
            raise gl.vm.UserError(f"{ERR_EXPECTED} agent card URL must be public HTTPS")
        if gl.message.value == u256(0):
            raise gl.vm.UserError(f"{ERR_EXPECTED} a non-zero GEN bond is required")
        claim = {"claim_id": claim_id, "agent_card_url": _clean(agent_card_url, MAX_URL),
                 "agent_identity": _clean(agent_identity, 160), "skill_id": _identifier(skill_id, "skill id"),
                 "promise": _clean(promise, MAX_TEXT), "profile_id": profile_id,
                 "owner": str(gl.message.sender_address), "bond": int(gl.message.value),
                 "status": "UNVERIFIED", "consecutive_failures": 0, "has_ever_failed": False,
                 "active": True, "bond_forfeited": False, "policy_version": POLICY_VERSION}
        if not claim["agent_identity"] or not claim["promise"]:
            raise gl.vm.UserError(f"{ERR_EXPECTED} identity and promise are required")
        self.claim_json[claim_id] = _canonical_json(claim)
        self.claim_owner[claim_id] = gl.message.sender_address
        self.revision_by_claim[claim_id] = u256(0)
        self.claim_ids.append(claim_id)
        self.claim_count = u256(int(self.claim_count) + 1)
        return claim

    def _consensus_challenge(self, claim: dict, profile: dict, vector: dict, challenge_id: str) -> dict:
        def leader_fn():
            return {"public": _run_challenge(claim, profile, vector, challenge_id)}

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return) or not isinstance(leader_result.calldata, dict):
                return False
            leader_public = leader_result.calldata.get("public")
            if not _valid_public(leader_public, claim, vector, challenge_id):
                return False
            validator_public = _run_challenge(claim, profile, vector, challenge_id)
            return _canonical_json(leader_public) == _canonical_json(validator_public)

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        public = result.get("public") if isinstance(result, dict) else None
        if not _valid_public(public, claim, vector, challenge_id):
            raise gl.vm.UserError(f"{ERR_EXPECTED} invalid consensus challenge record")
        return public

    @gl.public.write
    def challenge_capability(self, claim_id: str, challenge_id: str, challenger_nonce: str) -> dict:
        claim_id = _identifier(claim_id, "claim id")
        challenge_id = _identifier(challenge_id, "challenge id")
        if self.challenge_json.get(challenge_id, ""):
            raise gl.vm.UserError(f"{ERR_EXPECTED} challenge already exists")
        encoded_claim = self.claim_json.get(claim_id, "")
        if not encoded_claim:
            raise gl.vm.UserError(f"{ERR_EXPECTED} claim not found")
        claim = json.loads(encoded_claim)
        if not claim["active"]:
            raise gl.vm.UserError(f"{ERR_EXPECTED} claim is inactive")
        profile = json.loads(self.profile_json[claim["profile_id"]])
        revision = int(self.revision_by_claim[claim_id]) + 1
        vector = _select_vector(profile, claim_id, revision, challenger_nonce)
        public = self._consensus_challenge(claim, profile, vector, challenge_id)
        prior_status = claim["status"]
        if public["transient"] is not True:
            if public["semantic_pass"] is True:
                claim["status"] = "VERIFIED"
                claim["consecutive_failures"] = 0
            else:
                claim["consecutive_failures"] = int(claim["consecutive_failures"]) + 1
                if claim["consecutive_failures"] >= 2:
                    claim["status"] = "FAILED"
                    claim["has_ever_failed"] = True
                    claim["bond_forfeited"] = True
                else:
                    claim["status"] = "SUSPECT"
        record = {**public, "revision": revision, "prior_status": prior_status,
                  "resulting_status": claim["status"], "challenger": str(gl.message.sender_address),
                  "policy_version": POLICY_VERSION}
        self.challenge_json[challenge_id] = _canonical_json(record)
        self.claim_json[claim_id] = _canonical_json(claim)
        self.revision_by_claim[claim_id] = u256(revision)
        self.challenge_ids.append(challenge_id)
        self.challenge_count = u256(int(self.challenge_count) + 1)
        return record

    @gl.public.write
    def deactivate_and_withdraw(self, claim_id: str) -> None:
        claim_id = _identifier(claim_id, "claim id")
        encoded = self.claim_json.get(claim_id, "")
        if not encoded:
            raise gl.vm.UserError(f"{ERR_EXPECTED} claim not found")
        if gl.message.sender_address != self.claim_owner[claim_id]:
            raise gl.vm.UserError(f"{ERR_EXPECTED} only claim owner can deactivate")
        claim = json.loads(encoded)
        if not claim["active"]:
            raise gl.vm.UserError(f"{ERR_EXPECTED} claim already inactive")
        claim["active"] = False
        claim["status"] = "INACTIVE"
        self.claim_json[claim_id] = _canonical_json(claim)
        if not claim["bond_forfeited"] and int(claim["bond"]) > 0:
            amount = u256(int(claim["bond"]))
            claim["bond"] = 0
            self.claim_json[claim_id] = _canonical_json(claim)
            _Recipient(self.claim_owner[claim_id]).emit_transfer(value=amount)

    @gl.public.view
    def get_profile(self, profile_id: str) -> dict:
        encoded = self.profile_json.get(_identifier(profile_id, "profile id"), "")
        if not encoded:
            raise gl.vm.UserError(f"{ERR_EXPECTED} profile not found")
        return json.loads(encoded)

    @gl.public.view
    def get_claim(self, claim_id: str) -> dict:
        encoded = self.claim_json.get(_identifier(claim_id, "claim id"), "")
        if not encoded:
            raise gl.vm.UserError(f"{ERR_EXPECTED} claim not found")
        return json.loads(encoded)

    @gl.public.view
    def get_challenge(self, challenge_id: str) -> dict:
        encoded = self.challenge_json.get(_identifier(challenge_id, "challenge id"), "")
        if not encoded:
            raise gl.vm.UserError(f"{ERR_EXPECTED} challenge not found")
        return json.loads(encoded)

    @gl.public.view
    def is_currently_verified(self, claim_id: str) -> bool:
        claim = self.get_claim(claim_id)
        return bool(claim["active"] and claim["status"] == "VERIFIED")

    @gl.public.view
    def has_ever_failed(self, claim_id: str) -> bool:
        return bool(self.get_claim(claim_id)["has_ever_failed"])

    @gl.public.view
    def get_model_card(self) -> dict:
        return {"name": "CapabilityBond", "policy_version": POLICY_VERSION,
                "purpose": "Bonded, permissionless behavioral validation for public A2A agent skills.",
                "consensus": "Validators independently fetch the Agent Card, execute the selected A2A challenge, retrieve evidence, evaluate the explicit promise and require exact normalized verdict equality.",
                "failure_model": "Transient failures do not change status; two consecutive substantive failures forfeit the bond and close the verified gate.",
                "consumer_gates": ["is_currently_verified", "has_ever_failed"]}
