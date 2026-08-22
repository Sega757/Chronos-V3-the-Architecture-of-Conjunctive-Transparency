class PoSPArbiter:
    """
    Proof of Sampling (PoSP) Game-Theoretic Consensus Arbiter.
    Enforces Pure-Strategy Nash Equilibrium (E[U_cheat] < 0).
    """
    def __init__(self, cost_c=1.0, reward_r=10.0, stake_s=100.0, adversary_ratio_r=0.1):
        self.C = cost_c
        self.R = reward_r
        self.S = stake_s
        self.r = adversary_ratio_r

    def calculate_challenge_probability(self):
        """
        Calculates p > C(1-r) / (R + S)
        Uses the mathematically valid Alternative A.
        """
        numerator = self.C * (1.0 - self.r)
        denominator = self.R + self.S

        if denominator == 0:
            return 1.0

        p_min = numerator / denominator
        # Add a small buffer to ensure strict inequality
        p_enforced = min(1.0, p_min + 0.01)
        return p_enforced

    def trigger_challenge(self, p_threshold):
        import random
        # Cryptographically secure random would be used in production
        roll = random.random()
        return roll <= p_threshold

    def slash_stake(self, node_id):
        # In a real system, interacts with smart contract / Stake Vault
        print(f"SLASHING EXECUTED: Node {node_id} burned {self.S} stake.")
        return True
