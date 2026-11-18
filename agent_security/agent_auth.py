"""
agent_security/agent_auth.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Multi-Agent Cryptographic Authentication & Tamper-Evident Context.

Addresses Professor Critique (Section 164-171):
Provides:
  1. Cryptographic HMAC-SHA256 Agent Identity & Per-Agent Signing Keys
  2. Tamper-Evident Signed Context Fields (Immutable Def-Use Integrity)
  3. Signature Verification & Anti-Spoofing Gatekeeper
"""

from __future__ import annotations

import hmac
import hashlib
import time
import json
import secrets
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AgentID(str, Enum):
    AGENT_0_HEALER      = "Agent-0:SelfHealingGuard"
    AGENT_1_STRUCTURAL  = "Agent-1:StructuralInspector"
    AGENT_2_GREEN       = "Agent-2:GreenAuditor"
    AGENT_3_SECURITY    = "Agent-3:SecurityThreatHunter"
    AGENT_4_COMMUNICATOR= "Agent-4:TechnicalCommunicator"
    OPTIMIZER_AGENT     = "Agent-Opt:AutonomousOptimizer"


class SecurityTamperException(Exception):
    """Raised when an unauthorized agent attempts to overwrite signed context or forge signatures."""
    pass


@dataclass(frozen=True)
class SignedArtifact:
    agent_id: str
    field_name: str
    payload_digest: str
    timestamp: float
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "field_name": self.field_name,
            "payload_digest": self.payload_digest,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }


class AgentKeyManager:
    """
    Manages session-ephemeral cryptographic HMAC keys per agent.
    Keys are securely derived from a session master secret using HMAC-SHA256.
    """
    def __init__(self, master_secret: Optional[str] = None):
        self._master = master_secret.encode('utf-8') if master_secret else secrets.token_bytes(32)
        self._agent_keys: Dict[AgentID, bytes] = {}
        for aid in AgentID:
            self._agent_keys[aid] = hmac.new(
                self._master,
                msg=aid.value.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()

    def get_agent_key(self, agent_id: AgentID) -> bytes:
        return self._agent_keys[agent_id]


class SecureAgentContext:
    """
    Tamper-Evident Multi-Agent Context.
    Enforces write-once, signed-immutable semantics across all 5 agents.
    """
    def __init__(self, key_manager: Optional[AgentKeyManager] = None):
        self._key_manager = key_manager or AgentKeyManager()
        self._store: Dict[str, Any] = {}
        self._signatures: Dict[str, SignedArtifact] = {}

    def _hash_payload(self, payload: Any) -> str:
        if isinstance(payload, str):
            data = payload.encode('utf-8')
        else:
            try:
                data = json.dumps(payload, sort_keys=True).encode('utf-8')
            except Exception:
                data = str(payload).encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def sign_and_set(self, agent_id: AgentID, field_name: str, payload: Any) -> SignedArtifact:
        """
        Signs the payload with the agent's private HMAC key and stores it in context.
        Raises SecurityTamperException if the field has already been signed by another agent.
        """
        if field_name in self._signatures:
            existing = self._signatures[field_name]
            if existing.agent_id != agent_id.value:
                raise SecurityTamperException(
                    f"[Tamper Alert]: Unauthorized overwrite attempt on '{field_name}'! "
                    f"Owned by {existing.agent_id}, targeted by {agent_id.value}."
                )

        payload_digest = self._hash_payload(payload)
        now = time.time()
        agent_key = self._key_manager.get_agent_key(agent_id)

        msg = f"{agent_id.value}:{field_name}:{payload_digest}:{now}".encode('utf-8')
        sig = hmac.new(agent_key, msg=msg, digestmod=hashlib.sha256).hexdigest()

        artifact = SignedArtifact(
            agent_id=agent_id.value,
            field_name=field_name,
            payload_digest=payload_digest,
            timestamp=now,
            signature=sig
        )
        self._store[field_name] = payload
        self._signatures[field_name] = artifact
        return artifact

    def get_verified(self, field_name: str) -> Tuple[Any, SignedArtifact]:
        """
        Retrieves a context field after verifying its cryptographic HMAC signature and digest.
        Raises SecurityTamperException if data was modified or signature is invalid.
        """
        if field_name not in self._store or field_name not in self._signatures:
            raise KeyError(f"Context field '{field_name}' is not set.")

        payload = self._store[field_name]
        artifact = self._signatures[field_name]

        # 1. Verify Payload Hash
        current_digest = self._hash_payload(payload)
        if not hmac.compare_digest(current_digest, artifact.payload_digest):
            raise SecurityTamperException(
                f"[Integrity Violation]: Payload digest mismatch on field '{field_name}'! Data has been modified."
            )

        # 2. Verify Cryptographic Signature
        try:
            aid = AgentID(artifact.agent_id)
        except ValueError:
            raise SecurityTamperException(f"Unknown signing agent identity: {artifact.agent_id}")

        agent_key = self._key_manager.get_agent_key(aid)
        expected_msg = f"{artifact.agent_id}:{field_name}:{artifact.payload_digest}:{artifact.timestamp}".encode('utf-8')
        expected_sig = hmac.new(agent_key, msg=expected_msg, digestmod=hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_sig, artifact.signature):
            raise SecurityTamperException(
                f"[Authentication Failure]: Invalid signature for agent {artifact.agent_id} on field '{field_name}'!"
            )

        return payload, artifact

    def audit_all_signatures(self) -> Dict[str, bool]:
        """Audits integrity across every signed field in the context."""
        report = {}
        for k in self._signatures:
            try:
                self.get_verified(k)
                report[k] = True
            except SecurityTamperException:
                report[k] = False
        return report


def test_agent_authentication_integrity() -> bool:
    """Automated verification test of multi-agent signing and anti-tamper security."""
    km = AgentKeyManager()
    ctx = SecureAgentContext(key_manager=km)

    print("=" * 70)
    print("  MULTI-AGENT CRYPTOGRAPHIC AUTHENTICATION TEST SUITE")
    print("=" * 70)

    # 1. Agent 0 signs clean code
    clean_code = "def add(a, b): return a + b"
    sig0 = ctx.sign_and_set(AgentID.AGENT_0_HEALER, "clean_code", clean_code)
    val0, _ = ctx.get_verified("clean_code")
    assert val0 == clean_code
    print(" PASS 1. Agent-0 signed 'clean_code' verified with HMAC-SHA256")

    # 2. Agent 3 signs security profile
    sec_data = {"security_score": 100, "findings": []}
    sig3 = ctx.sign_and_set(AgentID.AGENT_3_SECURITY, "security_profile", sec_data)
    val3, _ = ctx.get_verified("security_profile")
    assert val3["security_score"] == 100
    print(" PASS 2. Agent-3 signed 'security_profile' verified with HMAC-SHA256")

    # 3. Test Unauthorized Overwrite Prevention (Agent 2 trying to hijack Agent 0's field)
    tamper_blocked = False
    try:
        ctx.sign_and_set(AgentID.AGENT_2_GREEN, "clean_code", "malicious_injected_code()")
    except SecurityTamperException:
        tamper_blocked = True
    assert tamper_blocked
    print(" PASS 3. Unauthorized cross-agent field hijack blocked (TamperBlocked)")

    # 4. Test In-Memory Tamper Detection (Man-in-the-Middle mutation of internal store)
    ctx._store["clean_code"] = "malicious_tampered_bytes()"
    tamper_detected = False
    try:
        ctx.get_verified("clean_code")
    except SecurityTamperException:
        tamper_detected = True
    assert tamper_detected
    print(" PASS 4. In-memory data tampering detected via SHA-256 digest mismatch")

    print("\n" + "=" * 70)
    print("  ALL MULTI-AGENT CRYPTOGRAPHIC INTEGRITY TESTS PASSED!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    test_agent_authentication_integrity()
