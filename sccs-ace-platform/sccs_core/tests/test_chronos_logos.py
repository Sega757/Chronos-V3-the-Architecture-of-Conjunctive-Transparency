import os
import json
import numpy as np
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from sccs_core import chronos_logos


class TestLoadOrGenerateKey:
    def test_generate_new_key(self, tmp_path, monkeypatch):
        key_path = str(tmp_path / "private_key.pem")
        monkeypatch.setattr(chronos_logos, "KEY_FILE", key_path)

        assert not os.path.exists(key_path)
        key = chronos_logos.load_or_generate_key()
        assert isinstance(key, ed25519.Ed25519PrivateKey)
        assert os.path.exists(key_path)

    def test_load_existing_key(self, tmp_path, monkeypatch):
        key_path = str(tmp_path / "private_key.pem")
        monkeypatch.setattr(chronos_logos, "KEY_FILE", key_path)

        original_key = ed25519.Ed25519PrivateKey.generate()
        pem = original_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(key_path, "wb") as f:
            f.write(pem)

        loaded_key = chronos_logos.load_or_generate_key()
        assert isinstance(loaded_key, ed25519.Ed25519PrivateKey)

        # Test that loaded key matches original key public bytes
        orig_pub = original_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        loaded_pub = loaded_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        assert orig_pub == loaded_pub


class TestComputeHuberLoss:
    def test_quadratic_region(self):
        delta = 1.35
        residuals = np.array([0.0, 0.5, -0.5, 1.0, -1.35])
        loss = chronos_logos.compute_huber_loss(residuals, delta=delta)
        expected = 0.5 * (residuals ** 2)
        np.testing.assert_allclose(loss, expected)

    def test_linear_region(self):
        delta = 1.35
        residuals = np.array([2.0, -3.0, 5.0])
        loss = chronos_logos.compute_huber_loss(residuals, delta=delta)
        abs_res = np.abs(residuals)
        expected = delta * (abs_res - 0.5 * delta)
        np.testing.assert_allclose(loss, expected)

    def test_zero_residual(self):
        loss = chronos_logos.compute_huber_loss(0.0, delta=1.35)
        assert loss == 0.0


class TestAlsIrlsSterilize:
    def test_clean_data(self):
        raw_values = [10.0, 10.2, 9.8, 10.1, 9.9]
        baseline, huber_loss = chronos_logos.als_irls_sterilize(raw_values, delta=1.35)
        assert abs(baseline - 10.0) < 0.2
        assert huber_loss >= 0

    def test_outlier_downweighting(self):
        # Clean baseline centered around 100 with extreme outlier hallucination 10000
        raw_values = [100.0, 101.0, 99.0, 100.5, 99.5, 10000.0]
        baseline, huber_loss = chronos_logos.als_irls_sterilize(raw_values, delta=1.35)
        # ALS-IRLS should attenuate the outlier and keep baseline near 100
        assert abs(baseline - 100.0) < 5.0

    def test_zero_residual_handling(self):
        # Same values ensure zero residuals
        raw_values = [5.0, 5.0, 5.0]
        baseline, huber_loss = chronos_logos.als_irls_sterilize(raw_values, delta=1.35)
        assert baseline == 5.0
        assert huber_loss == 0.0


class TestGenerateMerkleRoot:
    def test_empty_input(self):
        assert chronos_logos.generate_merkle_root([]) == ""

    def test_single_element(self):
        root = chronos_logos.generate_merkle_root([42])
        import hashlib
        expected = hashlib.sha256("42".encode('utf-8')).hexdigest()
        assert root == expected

    def test_even_number_of_elements(self):
        root = chronos_logos.generate_merkle_root([1, 2, 3, 4])
        assert isinstance(root, str)
        assert len(root) == 64

    def test_odd_number_of_elements(self):
        root_odd = chronos_logos.generate_merkle_root([1, 2, 3])
        assert isinstance(root_odd, str)
        assert len(root_odd) == 64

    def test_determinism(self):
        values = [10, 20, 30, 40, 50]
        r1 = chronos_logos.generate_merkle_root(values)
        r2 = chronos_logos.generate_merkle_root(values)
        assert r1 == r2


class TestCanonicalJson:
    def test_key_sorting_and_compact_formatting(self):
        data = {"z": 1, "a": 2, "m": {"b": 3, "a": 4}}
        result = chronos_logos.canonical_json(data)
        expected = '{"a":2,"m":{"a":4,"b":3},"z":1}'
        assert result == expected

    def test_insertion_order_independence(self):
        dict1 = {"b": 2, "a": 1}
        dict2 = {"a": 1, "b": 2}
        assert chronos_logos.canonical_json(dict1) == chronos_logos.canonical_json(dict2)


class TestProcessAndSign:
    def test_empty_raw_values_raises_value_error(self):
        with pytest.raises(ValueError, match="Cannot process empty telemetry."):
            chronos_logos.process_and_sign("session_123", [], delta=1.35)

    def test_process_and_sign_signature_roundtrip(self, tmp_path, monkeypatch):
        # Redirect private_key in module to use a fresh key
        test_key = ed25519.Ed25519PrivateKey.generate()
        monkeypatch.setattr(chronos_logos, "private_key", test_key)
        monkeypatch.setattr(chronos_logos, "public_key", test_key.public_key())

        raw_values = [10.0, 11.0, 12.0, 10.5]
        res = chronos_logos.process_and_sign("session_001", raw_values, delta=1.35)

        assert "object_id" in res
        assert res["object_id"].startswith("KO_CHRONOS_VERIFIED_")
        assert "timestamp" in res
        assert "json" in res
        assert "huber_residual" in res
        assert res["signal_present"] is True
        assert "signature" in res
        assert "merkle_root" in res

        # Verify signature
        import hashlib
        canonical_str = res["json"]
        payload_hash = hashlib.sha256(canonical_str.encode('utf-8')).digest()
        message_to_verify = res["merkle_root"].encode('utf-8') + payload_hash

        # Should verify without raising InvalidSignature exception
        test_key.public_key().verify(res["signature"], message_to_verify)

    def test_signature_verification_fails_on_tampered_payload(self, tmp_path, monkeypatch):
        test_key = ed25519.Ed25519PrivateKey.generate()
        monkeypatch.setattr(chronos_logos, "private_key", test_key)
        monkeypatch.setattr(chronos_logos, "public_key", test_key.public_key())

        raw_values = [10.0, 11.0, 12.0]
        res = chronos_logos.process_and_sign("session_002", raw_values, delta=1.35)

        import hashlib
        from cryptography.exceptions import InvalidSignature

        # Tampered message
        tampered_canonical_str = res["json"].replace("KO_CHRONOS_VERIFIED_", "KO_TAMPERED_")
        tampered_hash = hashlib.sha256(tampered_canonical_str.encode('utf-8')).digest()
        tampered_message = res["merkle_root"].encode('utf-8') + tampered_hash

        with pytest.raises(InvalidSignature):
            test_key.public_key().verify(res["signature"], tampered_message)
