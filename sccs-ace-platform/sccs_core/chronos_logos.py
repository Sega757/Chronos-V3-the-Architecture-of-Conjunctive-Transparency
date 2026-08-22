import numpy as np
import json
import time
import uuid
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# Generate a mock keypair for the service
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

def compute_huber_loss(residuals, delta=1.35):
    """
    Computes the Huber loss for a given set of residuals.
    """
    abs_res = np.abs(residuals)
    mask = abs_res <= delta
    # Quadratic for small errors, linear for large errors (outliers)
    return np.where(mask, 0.5 * (residuals ** 2), delta * (abs_res - 0.5 * delta))

def als_irls_sterilize(raw_values, delta=1.35):
    """
    Simulates Alternating Least Squares with Iteratively Reweighted Least Squares
    to find a robust baseline, minimizing the impact of outliers.
    """
    y = np.array(raw_values)
    # Simple estimation of baseline: start with median
    baseline = np.median(y)

    for _ in range(5): # IRLS iterations
        residuals = y - baseline
        abs_res = np.abs(residuals)

        # Calculate weights: w_i = delta / |a_i| for outliers
        weights = np.ones_like(y)
        outlier_mask = abs_res > delta

        # Prevent division by zero
        safe_res = np.where(abs_res == 0, 1e-8, abs_res)
        weights[outlier_mask] = delta / safe_res[outlier_mask]

        # Weighted least squares update
        baseline = np.sum(weights * y) / np.sum(weights)

    final_residuals = y - baseline
    huber_loss = np.mean(compute_huber_loss(final_residuals, delta))
    return baseline, huber_loss

def generate_merkle_root(values):
    """
    Generates a simple Merkle root hash from the raw values.
    """
    hashes = [hashlib.sha256(str(v).encode('utf-8')).hexdigest() for v in values]

    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1]) # Duplicate last if odd
        new_hashes = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i+1]
            new_hashes.append(hashlib.sha256(combined.encode('utf-8')).hexdigest())
        hashes = new_hashes

    return hashes[0] if hashes else ""

def canonical_json(obj):
    """
    Simulates RFC 8785 Canonical JSON serialization.
    """
    return json.dumps(obj, separators=(',', ':'), sort_keys=True)

def process_and_sign(session_id, raw_values, delta):
    """
    Executes the full sterilization and signing pipeline.
    """
    if not raw_values:
        raise ValueError("Cannot process empty telemetry.")

    # 1. Huber M-Estimation
    baseline, huber_loss = als_irls_sterilize(raw_values, delta)

    # 2. Merkle Root
    merkle_root = generate_merkle_root(raw_values)

    # 3. Payload Construction
    object_id = f"KO_CHRONOS_VERIFIED_{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "object_id": object_id,
        "baseline_value": float(baseline),
        "source": "chronos_logos.py"
    }

    canonical_str = canonical_json(payload)

    # 4. Cryptographic Signing (Ed25519)
    # Sign over H_Merkle || SHA256(Y_canonical)
    payload_hash = hashlib.sha256(canonical_str.encode('utf-8')).digest()
    message_to_sign = merkle_root.encode('utf-8') + payload_hash
    signature = private_key.sign(message_to_sign)

    return {
        "object_id": object_id,
        "timestamp": int(time.time() * 1000),
        "json": canonical_str,
        "huber_residual": float(huber_loss),
        "signal_present": True,
        "signature": signature,
        "merkle_root": merkle_root
    }
