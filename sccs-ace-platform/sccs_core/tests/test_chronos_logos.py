import os
import json
import hashlib
import pytest
import numpy as np

# Ensure import of chronos_logos does not create private_key.pem in root workspace
@pytest.fixture(scope="module")
def chronos_logos(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("key_dir")
    old_cwd = os.getcwd()
    os.chdir(tmp_dir)
    try:
        import sccs_core.chronos_logos as module
        yield module
    finally:
        os.chdir(old_cwd)

# --- Tests for compute_huber_loss ---

@pytest.mark.parametrize("residuals, delta, expected", [
    (0.0, 1.35, 0.0),
    (1.0, 1.35, 0.5), # 0.5 * 1.0^2 = 0.5
    (-1.0, 1.35, 0.5),
    (1.35, 1.35, 0.5 * (1.35**2)), # edge case |r| == delta
    (2.0, 1.35, 1.35 * (2.0 - 0.5 * 1.35)), # linear loss for |r| > delta
    (-3.0, 1.0, 1.0 * (3.0 - 0.5 * 1.0)),
])
def test_compute_huber_loss_scalar_and_array(chronos_logos, residuals, delta, expected):
    res = chronos_logos.compute_huber_loss(np.array([residuals]), delta)
    assert res[0] == pytest.approx(expected)

def test_compute_huber_loss_vectorized(chronos_logos):
    residuals = np.array([0.0, 0.5, 1.35, 2.0, -3.0])
    delta = 1.0
    # expected:
    # 0.0 -> 0
    # 0.5 -> 0.5 * 0.25 = 0.125
    # 1.35 -> 1.0 * (1.35 - 0.5) = 0.85
    # 2.0 -> 1.0 * (2.0 - 0.5) = 1.5
    # -3.0 -> 1.0 * (3.0 - 0.5) = 2.5
    expected = np.array([0.0, 0.125, 0.85, 1.5, 2.5])
    result = chronos_logos.compute_huber_loss(residuals, delta)
    np.testing.assert_allclose(result, expected)

# --- Tests for als_irls_sterilize ---

def test_als_irls_sterilize_clean_data(chronos_logos):
    data = [10.0, 10.1, 9.9, 10.05, 9.95]
    baseline, huber_loss = chronos_logos.als_irls_sterilize(data, delta=1.35)
    assert baseline == pytest.approx(10.0, abs=0.1)
    assert huber_loss == pytest.approx(0.0, abs=0.01)

def test_als_irls_sterilize_with_outliers(chronos_logos):
    # Mostly values around 5.0, with severe hallucinated outliers
    data = [5.0, 5.1, 4.9, 5.05, 4.95, 1000.0, -500.0]
    baseline, huber_loss = chronos_logos.als_irls_sterilize(data, delta=1.35)
    # Baseline should converge near 5.0 despite extreme outliers
    assert baseline == pytest.approx(5.0, abs=0.2)
    assert huber_loss > 0.0

def test_als_irls_sterilize_exact_zero_residuals(chronos_logos):
    # Data with identical values resulting in zero residual to test safe_res handling
    data = [7.0, 7.0, 7.0, 7.0]
    baseline, huber_loss = chronos_logos.als_irls_sterilize(data, delta=1.35)
    assert baseline == pytest.approx(7.0)
    assert huber_loss == pytest.approx(0.0)

# --- Tests for generate_merkle_root ---

def test_generate_merkle_root_empty(chronos_logos):
    assert chronos_logos.generate_merkle_root([]) == ""

def test_generate_merkle_root_single_leaf(chronos_logos):
    val = "leaf1"
    expected = hashlib.sha256(val.encode('utf-8')).hexdigest()
    assert chronos_logos.generate_merkle_root([val]) == expected

def test_generate_merkle_root_even_leaves(chronos_logos):
    leaves = ["a", "b"]
    h1 = hashlib.sha256(b"a").hexdigest()
    h2 = hashlib.sha256(b"b").hexdigest()
    expected = hashlib.sha256((h1 + h2).encode('utf-8')).hexdigest()
    assert chronos_logos.generate_merkle_root(leaves) == expected

def test_generate_merkle_root_odd_leaves(chronos_logos):
    leaves = ["a", "b", "c"]
    h1 = hashlib.sha256(b"a").hexdigest()
    h2 = hashlib.sha256(b"b").hexdigest()
    h3 = hashlib.sha256(b"c").hexdigest()
    # odd leaf 'c' duplicated -> h1+h2, h3+h3
    p1 = hashlib.sha256((h1 + h2).encode('utf-8')).hexdigest()
    p2 = hashlib.sha256((h3 + h3).encode('utf-8')).hexdigest()
    expected = hashlib.sha256((p1 + p2).encode('utf-8')).hexdigest()
    assert chronos_logos.generate_merkle_root(leaves) == expected

def test_generate_merkle_root_deterministic(chronos_logos):
    leaves = [10.5, 20.2, 30.1]
    res1 = chronos_logos.generate_merkle_root(leaves)
    res2 = chronos_logos.generate_merkle_root(leaves)
    assert res1 == res2

# --- Tests for canonical_json ---

def test_canonical_json_sorting_and_compactness(chronos_logos):
    data = {"z": 1, "a": 2, "m": [3, 2, 1]}
    result = chronos_logos.canonical_json(data)
    # Keys sorted alphabetically ('a', 'm', 'z') and no whitespace after separators
    assert result == '{"a":2,"m":[3,2,1],"z":1}'

# --- Tests for process_and_sign ---

def test_process_and_sign_empty_telemetry_raises(chronos_logos):
    with pytest.raises(ValueError, match="Cannot process empty telemetry"):
        chronos_logos.process_and_sign("session123", [], delta=1.35)

def test_process_and_sign_valid_telemetry(chronos_logos):
    raw_values = [1.0, 2.0, 3.0, 2.5]
    session_id = "session_abc"
    delta = 1.35

    res = chronos_logos.process_and_sign(session_id, raw_values, delta)

    assert "object_id" in res
    assert res["object_id"].startswith("KO_CHRONOS_VERIFIED_")
    assert "timestamp" in res
    assert isinstance(res["timestamp"], int)
    assert "json" in res
    assert "huber_residual" in res
    assert res["signal_present"] is True
    assert "signature" in res
    assert "merkle_root" in res

    # Verify JSON structure inside output
    parsed = json.loads(res["json"])
    assert parsed["object_id"] == res["object_id"]
    assert parsed["source"] == "chronos_logos.py"

    # Verify signature correctness using public key
    pub_key = chronos_logos.public_key
    payload_hash = hashlib.sha256(res["json"].encode('utf-8')).digest()
    message_to_verify = res["merkle_root"].encode('utf-8') + payload_hash

    # ed25519 verify raises InvalidSignature if invalid
    pub_key.verify(res["signature"], message_to_verify)

def test_process_and_sign_signature_rejects_tampered_message(chronos_logos):
    raw_values = [1.0, 2.0, 3.0]
    res = chronos_logos.process_and_sign("session_xyz", raw_values, delta=1.35)

    pub_key = chronos_logos.public_key
    tampered_merkle_root = "0" * 64
    payload_hash = hashlib.sha256(res["json"].encode('utf-8')).digest()
    tampered_message = tampered_merkle_root.encode('utf-8') + payload_hash

    from cryptography.exceptions import InvalidSignature
    with pytest.raises(InvalidSignature):
        pub_key.verify(res["signature"], tampered_message)
