"""Tests for chronos_common.signing module."""

import hashlib
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from chronos_common.canonical_json import canonicalize
from chronos_common.signing import Ed25519Signer, KeyPair, SignedPayload, verify_signature


class TestKeyPair:
    """Test suite for KeyPair dataclass and key generation."""

    def test_generate(self):
        node_id = "node-alpha"
        keypair = KeyPair.generate(node_id)
        assert keypair.node_id == node_id
        assert isinstance(keypair.private_key, Ed25519PrivateKey)
        assert isinstance(keypair.public_key_bytes, bytes)
        assert len(keypair.public_key_bytes) == 32

    def test_public_key_bytes_property(self):
        keypair = KeyPair.generate("node-beta")
        pub_bytes_1 = keypair.public_key_bytes
        pub_bytes_2 = keypair.public_key_bytes
        assert pub_bytes_1 == pub_bytes_2
        assert len(pub_bytes_1) == 32


class TestEd25519Signer:
    """Test suite for Ed25519Signer."""

    def test_sign_returns_signed_payload(self):
        keypair = KeyPair.generate("node-1")
        signer = Ed25519Signer(keypair)
        payload = {"action": "transfer", "amount": 100}

        signed = signer.sign(payload)

        assert isinstance(signed, SignedPayload)
        assert signed.signer_id == "node-1"
        assert signed.public_key == keypair.public_key_bytes
        assert len(signed.signature) == 64
        expected_digest = hashlib.sha256(canonicalize(payload)).digest()
        assert signed.payload_hash == expected_digest


class TestVerifySignature:
    """Test suite for verify_signature function and edge cases."""

    @pytest.mark.parametrize(
        "payload",
        [
            {"key": "value", "count": 42},
            ["element1", "element2", 123],
            "simple string payload",
            100500,
            {"nested": {"structure": [True, False, None]}},
        ],
    )
    def test_verify_signature_happy_path(self, payload):
        keypair = KeyPair.generate("signer-node")
        signer = Ed25519Signer(keypair)
        signed = signer.sign(payload)

        is_valid = verify_signature(
            payload=payload,
            public_key=signed.public_key,
            signature=signed.signature,
        )
        assert is_valid is True

    def test_key_order_invariance(self):
        keypair = KeyPair.generate("signer-node")
        signer = Ed25519Signer(keypair)

        payload_1 = {"z": 26, "a": 1, "m": 13}
        payload_2 = {"a": 1, "m": 13, "z": 26}

        signed_1 = signer.sign(payload_1)

        # Signature of payload_1 must verify for payload_2 due to canonical JSON ordering
        assert verify_signature(payload_2, signed_1.public_key, signed_1.signature) is True

    @pytest.mark.parametrize(
        "tampered_payload",
        [
            {"action": "transfer", "amount": 101},  # modified value
            {"action": "transfer", "amount": 100, "extra": True},  # extra key
            {"action": "transfer"},  # missing key
            "tampered string",  # completely different payload
        ],
    )
    def test_tampered_payload(self, tampered_payload):
        keypair = KeyPair.generate("signer-node")
        signer = Ed25519Signer(keypair)
        original_payload = {"action": "transfer", "amount": 100}
        signed = signer.sign(original_payload)

        assert (
            verify_signature(
                payload=tampered_payload,
                public_key=signed.public_key,
                signature=signed.signature,
            )
            is False
        )

    def test_incorrect_public_key(self):
        keypair_1 = KeyPair.generate("node-1")
        keypair_2 = KeyPair.generate("node-2")
        signer_1 = Ed25519Signer(keypair_1)

        payload = {"data": "confidential"}
        signed = signer_1.sign(payload)

        # Verification with keypair_2's public key should fail
        assert (
            verify_signature(
                payload=payload,
                public_key=keypair_2.public_key_bytes,
                signature=signed.signature,
            )
            is False
        )

    @pytest.mark.parametrize(
        "corrupted_sig_func",
        [
            lambda sig: bytes([sig[0] ^ 0xFF]) + sig[1:],  # bit flipped
            lambda sig: sig[:-1],  # truncated (63 bytes)
            lambda sig: sig + b"\x00",  # extra byte (65 bytes)
            lambda sig: b"\x00" * 64,  # zero signature
        ],
    )
    def test_corrupted_signature(self, corrupted_sig_func):
        keypair = KeyPair.generate("node-1")
        signer = Ed25519Signer(keypair)
        payload = {"msg": "hello"}
        signed = signer.sign(payload)

        corrupted_signature = corrupted_sig_func(signed.signature)
        assert (
            verify_signature(
                payload=payload,
                public_key=signed.public_key,
                signature=corrupted_signature,
            )
            is False
        )

    @pytest.mark.parametrize(
        "malformed_pubkey",
        [
            b"",  # empty
            b"\x00" * 16,  # too short (16 bytes)
            b"\x00" * 31,  # 31 bytes
            b"\x00" * 33,  # too long (33 bytes)
            b"\x00" * 64,  # 64 bytes
        ],
    )
    def test_malformed_public_key(self, malformed_pubkey):
        keypair = KeyPair.generate("node-1")
        signer = Ed25519Signer(keypair)
        payload = {"msg": "hello"}
        signed = signer.sign(payload)

        # verify_signature should return False and never raise exceptions for malformed public keys
        assert (
            verify_signature(
                payload=payload,
                public_key=malformed_pubkey,
                signature=signed.signature,
            )
            is False
        )
