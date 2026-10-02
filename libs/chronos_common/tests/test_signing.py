"""Tests for chronos_common.signing module."""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from chronos_common.signing import Ed25519Signer, KeyPair, SignedPayload, verify_signature


class TestKeyPair:
    """Test suite for KeyPair dataclass and generation."""

    def test_keypair_generate(self):
        node_id = "node-alpha-1"
        keypair = KeyPair.generate(node_id)

        assert keypair.node_id == node_id
        assert isinstance(keypair.private_key, Ed25519PrivateKey)
        assert isinstance(keypair.public_key_bytes, bytes)
        assert len(keypair.public_key_bytes) == 32


class TestEd25519SignerAndVerify:
    """Test suite for Ed25519Signer and verify_signature."""

    @pytest.fixture
    def keypair(self) -> KeyPair:
        return KeyPair.generate("test-node")

    @pytest.fixture
    def signer(self, keypair: KeyPair) -> Ed25519Signer:
        return Ed25519Signer(keypair)

    def test_sign_returns_valid_signed_payload(self, keypair: KeyPair, signer: Ed25519Signer):
        payload = {"action": "TRANSFER", "amount": 100, "user": "alice"}
        signed_payload = signer.sign(payload)

        assert isinstance(signed_payload, SignedPayload)
        assert signed_payload.signer_id == keypair.node_id
        assert signed_payload.public_key == keypair.public_key_bytes
        assert isinstance(signed_payload.signature, bytes)
        assert len(signed_payload.signature) == 64
        assert isinstance(signed_payload.payload_hash, bytes)
        assert len(signed_payload.payload_hash) == 32

    def test_verify_signature_happy_path(self, keypair: KeyPair, signer: Ed25519Signer):
        payload = {"data": "valid_payload", "status": "active"}
        signed_payload = signer.sign(payload)

        valid = verify_signature(
            payload=payload,
            public_key=signed_payload.public_key,
            signature=signed_payload.signature,
        )
        assert valid is True

    def test_verify_signature_tampered_payload(self, signer: Ed25519Signer):
        original_payload = {"key": "value", "count": 5}
        signed_payload = signer.sign(original_payload)

        # Modified value
        assert verify_signature({"key": "value", "count": 6}, signed_payload.public_key, signed_payload.signature) is False

        # Added key
        assert verify_signature({"key": "value", "count": 5, "extra": True}, signed_payload.public_key, signed_payload.signature) is False

        # Removed key
        assert verify_signature({"key": "value"}, signed_payload.public_key, signed_payload.signature) is False

    def test_verify_signature_corrupted_signature(self, signer: Ed25519Signer):
        payload = {"message": "hello"}
        signed_payload = signer.sign(payload)

        # Bit flip in signature
        corrupted_sig = bytearray(signed_payload.signature)
        corrupted_sig[0] ^= 0xFF
        assert verify_signature(payload, signed_payload.public_key, bytes(corrupted_sig)) is False

        # Truncated signature
        truncated_sig = signed_payload.signature[:32]
        assert verify_signature(payload, signed_payload.public_key, truncated_sig) is False

        # Garbage signature
        garbage_sig = b"invalid_signature_bytes_that_are_not_ed25519"
        assert verify_signature(payload, signed_payload.public_key, garbage_sig) is False

    def test_verify_signature_wrong_public_key(self, signer: Ed25519Signer):
        payload = {"data": "secure"}
        signed_payload = signer.sign(payload)

        other_keypair = KeyPair.generate("other-node")
        assert verify_signature(payload, other_keypair.public_key_bytes, signed_payload.signature) is False

    def test_canonical_json_key_ordering(self, signer: Ed25519Signer):
        payload_1 = {"b": 2, "a": 1, "c": {"z": 10, "y": 9}}
        payload_2 = {"a": 1, "c": {"y": 9, "z": 10}, "b": 2}

        signed_1 = signer.sign(payload_1)
        signed_2 = signer.sign(payload_2)

        assert signed_1.payload_hash == signed_2.payload_hash
        assert verify_signature(payload_2, signed_1.public_key, signed_1.signature) is True

    @pytest.mark.parametrize(
        "special_payload",
        [
            {"greeting": "Hello, 世界 🌍!"},
            {"special_chars": "\n\t\r\"'\\"},
            {"emoji_array": ["🚀", "🛡️", "⚡"]},
        ],
    )
    def test_unicode_and_special_characters(self, signer: Ed25519Signer, special_payload):
        signed = signer.sign(special_payload)
        assert verify_signature(special_payload, signed.public_key, signed.signature) is True

    @pytest.mark.parametrize(
        "boundary_payload",
        [
            {},
            "",
            0,
            False,
            [],
            None,
        ],
    )
    def test_boundary_payloads(self, signer: Ed25519Signer, boundary_payload):
        signed = signer.sign(boundary_payload)
        assert verify_signature(boundary_payload, signed.public_key, signed.signature) is True

    def test_non_serializable_payload_raises_error(self, signer: Ed25519Signer):
        non_serializable = {"invalid_set": {1, 2, 3}}

        with pytest.raises(Exception):
            signer.sign(non_serializable)

        with pytest.raises(Exception):
            verify_signature(non_serializable, signer._keypair.public_key_bytes, b"dummy")
