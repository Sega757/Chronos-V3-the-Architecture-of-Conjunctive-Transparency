import json
import os
import hashlib
import numpy as np
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# Ensure import of chronos_logos does not create private_key.pem in root workspace
@pytest.fixture(scope="module", autouse=True)
def chronos_logos_module(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("key_dir")
    old_cwd = os.getcwd()
    os.chdir(tmp_dir)
    try:
        import chronos_logos
        yield chronos_logos
    finally:
        os.chdir(old_cwd)

from chronos_logos import (
    compute_huber_loss,
    als_irls_sterilize,
    generate_merkle_root,
    canonical_json,
    process_and_sign,
    load_or_generate_key,
)

class TestHuberLoss:
    @pytest.mark.parametrize(
        "residuals, delta, expected",
        [
            (0.0, 1.35, 0.0),
            (1.0, 1.35, 0.5),
            (-1.0, 1.35, 0.5),
            (1.35, 1.35, 0.5 * (1.35 ** 2)),
            (2.0, 1.35, 1.35 * (2.0 - 0.5 * 1.35)),
            (-3.0, 1.0, 1.0 * (3.0 - 0.5 * 1.0)),
        ],
    )
    def test_compute_huber_loss_scalars(self, residuals, delta, expected):
        res = compute_huber_loss(np.array([residuals]), delta)
        assert res[0] == pytest.approx(expected)

    def test_compute_huber_loss_vectorized(self):
        residuals = np.array([0.0, 0.5, 1.35, 2.0, -3.0])
        delta = 1.0
        expected = np.array([0.0, 0.125, 0.85, 1.5, 2.5])
        result = compute_huber_loss(residuals, delta)
        np.testing.assert_allclose(result, expected)

    def test_compute_huber_loss_threshold_boundary(self):
        delta = 1.35
        res_at_delta = np.array([delta, -delta])
        quadratic_loss = 0.5 * (delta ** 2)
        linear_loss = delta * (delta - 0.5 * delta)
        assert quadratic_loss == pytest.approx(linear_loss)

        loss = compute_huber_loss(res_at_delta, delta)
        np.testing.assert_allclose(loss, [quadratic_loss, quadratic_loss], rtol=1e-6)

class TestAlsIrlsSterilize:
    def test_clean_data(self):
        raw = [10.0, 10.2, 9.8, 10.1, 9.9]
        baseline, huber_loss = als_irls_sterilize(raw, delta=1.35)
        assert baseline == pytest.approx(10.0, abs=0.1)
        assert huber_loss < 0.1

    def test_outlier_downweighting(self):
        # Clean baseline around 10.0 with extreme outliers (hallucinations)
        raw = [10.0, 10.1, 9.9, 10.05, 9.95, 1000.0, -500.0]
        baseline, huber_loss = als_irls_sterilize(raw, delta=1.35)
        # Median baseline initially ~10.0, outliers should be severely downweighted
        assert baseline == pytest.approx(10.0, abs=0.2)
        assert huber_loss > 0.0

    def test_identical_values(self):
        raw = [5.0, 5.0, 5.0, 5.0]
        baseline, huber_loss = als_irls_sterilize(raw, delta=1.35)
        assert baseline == pytest.approx(5.0)
        assert huber_loss == pytest.approx(0.0)

class TestMerkleRoot:
    def test_empty_list(self):
        assert generate_merkle_root([]) == ""

    def test_single_element(self):
        val = ["leaf1"]
        expected = hashlib.sha256("leaf1".encode('utf-8')).hexdigest()
        assert generate_merkle_root(val) == expected

    def test_even_elements(self):
        leaves = ["a", "b"]
        h1 = hashlib.sha256(b"a").hexdigest()
        h2 = hashlib.sha256(b"b").hexdigest()
        expected = hashlib.sha256((h1 + h2).encode('utf-8')).hexdigest()
        assert generate_merkle_root(leaves) == expected

    def test_odd_elements(self):
        leaves = ["a", "b", "c"]
        h1 = hashlib.sha256(b"a").hexdigest()
        h2 = hashlib.sha256(b"b").hexdigest()
        h3 = hashlib.sha256(b"c").hexdigest()
        p1 = hashlib.sha256((h1 + h2).encode('utf-8')).hexdigest()
        p2 = hashlib.sha256((h3 + h3).encode('utf-8')).hexdigest()
        expected = hashlib.sha256((p1 + p2).encode('utf-8')).hexdigest()
        assert generate_merkle_root(leaves) == expected

    def test_generate_merkle_root_deterministic(self):
        leaves = [10.5, 20.2, 30.1]
        res1 = generate_merkle_root(leaves)
        res2 = generate_merkle_root(leaves)
        assert res1 == res2

class TestCanonicalJson:
    def test_canonical_json_formatting(self):
        obj = {"z": 1, "a": 2, "m": [3, 2, 1]}
        result = canonical_json(obj)
        assert result == '{"a":2,"m":[3,2,1],"z":1}'

class TestKeyManagement:
    def test_key_file_creation_and_loading(self, tmp_path, monkeypatch):
        key_path = tmp_path / "private_key.pem"
        monkeypatch.setattr("chronos_logos.KEY_FILE", str(key_path))

        assert not os.path.exists(key_path)
        key1 = load_or_generate_key()
        assert os.path.exists(key_path)

        key2 = load_or_generate_key()

        # Public keys should match
        pub1 = key1.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        pub2 = key2.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        assert pub1 == pub2

class TestProcessAndSign:
    def test_empty_raw_values_raises_value_error(self):
        with pytest.raises(ValueError, match="Cannot process empty telemetry."):
            process_and_sign("session-123", [], delta=1.35)

    def test_valid_processing_and_signature_verification(self, tmp_path, monkeypatch):
        key_path = tmp_path / "private_key.pem"
        monkeypatch.setattr("chronos_logos.KEY_FILE", str(key_path))

        priv_key = load_or_generate_key()
        monkeypatch.setattr("chronos_logos.private_key", priv_key)
        pub_key = priv_key.public_key()

        raw_values = [10.0, 10.5, 9.5]
        result = process_and_sign("session-1", raw_values, delta=1.35)

        assert "object_id" in result
        assert result["object_id"].startswith("KO_CHRONOS_VERIFIED_")
        assert result["signal_present"] is True
        assert isinstance(result["huber_residual"], float)
        assert isinstance(result["merkle_root"], str)

        parsed = json.loads(result["json"])
        assert parsed["object_id"] == result["object_id"]
        assert parsed["source"] == "chronos_logos.py"

        # Verify signature
        payload_hash = hashlib.sha256(result["json"].encode('utf-8')).digest()
        message = result["merkle_root"].encode('utf-8') + payload_hash

        pub_key.verify(result["signature"], message)

    def test_tampered_payload_signature_verification_fails(self, tmp_path, monkeypatch):
        key_path = tmp_path / "private_key.pem"
        monkeypatch.setattr("chronos_logos.KEY_FILE", str(key_path))
        priv_key = load_or_generate_key()
        monkeypatch.setattr("chronos_logos.private_key", priv_key)
        pub_key = priv_key.public_key()

        raw_values = [10.0, 10.5, 9.5]
        result = process_and_sign("session-1", raw_values, delta=1.35)

        tampered_json = result["json"].replace("10.0", "999.0")
        tampered_payload_hash = hashlib.sha256(tampered_json.encode('utf-8')).digest()
        tampered_message = result["merkle_root"].encode('utf-8') + tampered_payload_hash

        with pytest.raises(Exception):
            pub_key.verify(result["signature"], tampered_message)
