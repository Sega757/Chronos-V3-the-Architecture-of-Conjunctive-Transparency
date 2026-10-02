"""Tests for chronos_common.signing module."""

from dataclasses import FrozenInstanceError
import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from chronos_common.signing import (
    Ed25519Signer,
    KeyPair,
    SignedPayload,
    verify_signature,
)


class TestKeyPair:
    """Test suite for KeyPair dataclass and key generation."""

    def test_generate_keypair(self):
        node_id = "node-alpha"
        kp = KeyPair.generate(node_id)
        assert kp.node_id == node_id
        assert isinstance(kp.private_key, Ed25519PrivateKey)
        assert isinstance(kp.public_key_bytes, bytes)
        assert len(kp.public_key_bytes) == 32

    def test_keypair_immutability(self):
        kp = KeyPair.generate("node-1")
        with pytest.raises(FrozenInstanceError):
            kp.node_id = "node-2"

    def test_public_key_bytes_consistency(self):
        kp = KeyPair.generate("node-1")
        assert kp.public_key_bytes == kp.public_key_bytes


class TestEd25519Signer:
    """Test suite for Ed25519Signer and SignedPayload generation."""

    def test_sign_payload_attributes(self):
        kp = KeyPair.generate("node-signer")
        signer = Ed25519Signer(kp)
        payload = {"action": "transfer", "amount": 100}

        signed = signer.sign(payload)

        assert isinstance(signed, SignedPayload)
        assert signed.signer_id == "node-signer"
        assert signed.public_key == kp.public_key_bytes
        assert isinstance(signed.signature, bytes)
        assert len(signed.signature) == 64
        assert isinstance(signed.payload_hash, bytes)
        assert len(signed.payload_hash) == 32

    @pytest.mark.parametrize(
        "payload",
        [
            {"a": 1, "b": [2, 3]},
            ["item1", "item2"],
            "simple string payload",
            12345,
            98.6,
            True,
            None,
        ],
    )
    def test_sign_different_payload_types(self, payload):
        kp = KeyPair.generate("node-types")
        signer = Ed25519Signer(kp)
        signed = signer.sign(payload)
        assert verify_signature(payload, signed.public_key, signed.signature)

    @pytest.mark.parametrize("payload", [{}, "", []])
    def test_sign_empty_and_boundary_payloads(self, payload):
        kp = KeyPair.generate("node-empty")
        signer = Ed25519Signer(kp)
        signed = signer.sign(payload)
        assert verify_signature(payload, signed.public_key, signed.signature)

    def test_sign_unicode_and_special_chars(self):
        kp = KeyPair.generate("node-unicode")
        signer = Ed25519Signer(kp)
        payload = {"message": "Hello 🌍! Special chars: \n \t \u2603"}
        signed = signer.sign(payload)
        assert verify_signature(payload, signed.public_key, signed.signature)

    def test_sign_non_serializable_payload_raises(self):
        kp = KeyPair.generate("node-invalid")
        signer = Ed25519Signer(kp)

        class CustomClass:
            pass

        with pytest.raises((TypeError, ValueError)):
            signer.sign({"custom": CustomClass()})

        with pytest.raises((TypeError, ValueError)):
            signer.sign({1, 2, 3})


class TestVerifySignature:
    """Test suite for verify_signature function."""

    def test_verify_signature_happy_path(self):
        kp = KeyPair.generate("node-verify")
        signer = Ed25519Signer(kp)
        payload = {"status": "ok", "code": 200}
        signed = signer.sign(payload)

        is_valid = verify_signature(payload, signed.public_key, signed.signature)
        assert is_valid is True

    def test_key_order_invariance(self):
        kp = KeyPair.generate("node-order")
        signer = Ed25519Signer(kp)
        payload1 = {"b": 2, "a": 1}
        payload2 = {"a": 1, "b": 2}

        signed1 = signer.sign(payload1)
        # Signature generated for payload1 should verify for payload2 with identical content but different key order
        assert verify_signature(payload2, signed1.public_key, signed1.signature) is True

    @pytest.mark.parametrize(
        "tampered_payload",
        [
            {"status": "ok", "code": 201},  # Modified value
            {"status": "ok", "code": 200, "extra": True},  # Added key
            {"status": "ok"},  # Deleted key
            "completely different payload",  # Type change
        ],
    )
    def test_verify_tampered_payload_returns_false(self, tampered_payload):
        kp = KeyPair.generate("node-tamper")
        signer = Ed25519Signer(kp)
        original_payload = {"status": "ok", "code": 200}
        signed = signer.sign(original_payload)

        is_valid = verify_signature(tampered_payload, signed.public_key, signed.signature)
        assert is_valid is False

    def test_verify_mismatched_key_returns_false(self):
        kp1 = KeyPair.generate("node-1")
        kp2 = KeyPair.generate("node-2")
        signer = Ed25519Signer(kp1)
        payload = {"data": "confidential"}
        signed = signer.sign(payload)

        is_valid = verify_signature(payload, kp2.public_key_bytes, signed.signature)
        assert is_valid is False

    @pytest.mark.parametrize(
        "bad_signature",
        [
            b"a" * 64,  # Random bytes of valid length
            b"short_sig",  # Truncated signature
            b"",  # Empty signature
        ],
    )
    def test_verify_corrupted_signature_returns_false(self, bad_signature):
        kp = KeyPair.generate("node-corrupted-sig")
        payload = {"key": "value"}

        is_valid = verify_signature(payload, kp.public_key_bytes, bad_signature)
        assert is_valid is False

    def test_verify_signature_bit_flip_returns_false(self):
        kp = KeyPair.generate("node-bitflip")
        signer = Ed25519Signer(kp)
        payload = {"key": "value"}
        signed = signer.sign(payload)

        # Flip a bit in the signature
        corrupted_sig = bytearray(signed.signature)
        corrupted_sig[0] ^= 0xFF
        is_valid = verify_signature(payload, signed.public_key, bytes(corrupted_sig))
        assert is_valid is False

    def test_verify_invalid_public_key_bytes_returns_false(self):
        kp = KeyPair.generate("node-invalid-pk")
        signer = Ed25519Signer(kp)
        payload = {"key": "value"}
        signed = signer.sign(payload)

        # 32 bytes but invalid curve point bytes
        invalid_32_bytes = b"x" * 32
        is_valid = verify_signature(payload, invalid_32_bytes, signed.signature)
        assert is_valid is False

    @pytest.mark.parametrize(
        "malformed_public_key",
        [
            b"short_key",  # Incorrect length
            b"",  # Empty key
        ],
    )
    def test_verify_malformed_public_key_raises_value_error(self, malformed_public_key):
        kp = KeyPair.generate("node-malformed-pk")
        signer = Ed25519Signer(kp)
        payload = {"key": "value"}
        signed = signer.sign(payload)

        with pytest.raises(ValueError, match="An Ed25519 public key is 32 bytes long"):
            verify_signature(payload, malformed_public_key, signed.signature)
