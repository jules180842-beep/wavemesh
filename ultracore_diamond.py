"""
ultracore_diamond.py - Integrated Core
Ties PI sequences -> Diamond/Ceramic validation -> WaveMesh.io telemetry -> Ultra Staking

This is the drop-in updated version you asked for.
Works as backend for wavemesh.app / wavemesh.io iPhone client.
"""

import math
import time
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# === Core Material Constants from research ===
BASELINE_CERAMIC_GPA = 16.9
DIAMOND_BUMP_GPA = 2.0
TARGET_GPA = BASELINE_CERAMIC_GPA + DIAMOND_BUMP_GPA  # 18.9 GPa
COHERENCE_TARGET_US = 4.67
COHERENCE_MIN_HEALTHY_US = 3.5

# === PI Sequence Engine ===
class PiSequenceEngine:
    """
    Generates PI-derived sequences for ultra_diamond.pi logic.
    Used for node IDs, staking entropy, and coherence modulation.
    """
    def __init__(self):
        self.pi = math.pi

    def golden_pi_ratio(self, n: int) -> float:
        """phi * pi / n style sequence for diamond lattice spacing"""
        phi = (1 + math.sqrt(5)) / 2
        return (phi * self.pi) / max(1, n)

    def pi_pulse_sequence(self, length: int = 16) -> List[float]:
        """Creates deterministic but non-repeating pulse timing from pi decimals"""
        seq = []
        for i in range(1, length + 1):
            # fractional part of pi * i * e
            val = (self.pi * i * math.e) % 1.0
            seq.append(round(val, 6))
        return seq

    def pi_hash_entropy(self, seed: str) -> str:
        """For ultra staking randomness, tied to pi"""
        raw = f"{seed}:{self.pi}:{time.time_ns() // 1_000_000}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

# === Diamond Node Model ===
@dataclass
class DiamondNodeState:
    node_id: str
    gpa_measured: float
    coherence_us: float
    temp_k: float
    pi_phase: float
    timestamp: float

    @property
    def health_score(self) -> float:
        gpa_score = min(1.0, self.gpa_measured / TARGET_GPA)
        coh_score = min(1.0, self.coherence_us / COHERENCE_TARGET_US)
        return round((gpa_score * 0.6 + coh_score * 0.4), 4)

    @property
    def is_ultra(self) -> bool:
        return self.gpa_measured >= TARGET_GPA and self.coherence_us >= COHERENCE_MIN_HEALTHY_US

# === Ultra Diamond Core ===
class UltraCoreDiamond:
    def __init__(self, node_id: str = "ultra_diamond_001"):
        self.node_id = node_id
        self.pi_engine = PiSequenceEngine()
        self.history: List[DiamondNodeState] = []

    def validate_sample(self, gpa: float, coherence_us: float, temp_k: float = 295.0) -> DiamondNodeState:
        phase = self.pi_engine.golden_pi_ratio(len(self.history) + 1)
        state = DiamondNodeState(
            node_id=self.node_id,
            gpa_measured=gpa,
            coherence_us=coherence_us,
            temp_k=temp_k,
            pi_phase=phase,
            timestamp=time.time()
        )
        self.history.append(state)
        return state

    def get_telemetry_payload(self) -> Dict:
        if not self.history:
            return {"node_id": self.node_id, "status": "idle"}
        last = self.history[-1]
        return {
            "node_id": last.node_id,
            "gpa": last.gpa_measured,
            "target_gpa": TARGET_GPA,
            "coherence_us": last.coherence_us,
            "coherence_target": COHERENCE_TARGET_US,
            "health": last.health_score,
            "is_ultra": last.is_ultra,
            "pi_phase": last.pi_phase,
            "pi_pulse": self.pi_engine.pi_pulse_sequence(8),
            "timestamp": last.timestamp
        }

# === WaveMesh.io Integration ===
class WaveMeshClient:
    """
    Bridge for wavemesh.app iPhone client.
    iPhone cannot do ESP-NOW mesh directly, so it talks wss://wavemesh.io
    This payload is what your iOS app / Web App will poll.
    """
    def __init__(self, core: UltraCoreDiamond):
        self.core = core
        self.endpoint = "wss://wavemesh.io/api/v1/stream"

    def build_ws_message(self) -> str:
        payload = self.core.get_telemetry_payload()
        payload["proto"] = "ultracore_diamond_v2"
        payload["pi_integrated"] = True
        return json.dumps(payload)

# === Ultra Staking Logic ===
class UltraStaking:
    def __init__(self, pi_engine: PiSequenceEngine):
        self.pi_engine = pi_engine
        self.stake_ledger: Dict[str, float] = {}

    def calculate_reward_multiplier(self, state: DiamondNodeState) -> float:
        """
        Reward scales with health and pi_phase alignment.
        Ultra nodes get diamond bump.
        """
        base = 1.0 + state.health_score
        if state.is_ultra:
            base += 0.5  # diamond bonus
        # pi resonance bonus: when pi_phase close to 0.5
        resonance = 1.0 - abs(0.5 - (state.pi_phase % 1.0))
        return round(base * (1 + resonance * 0.25), 4)

    def stake(self, wallet: str, amount: float, state: DiamondNodeState) -> Dict:
        mult = self.calculate_reward_multiplier(state)
        reward = amount * mult
        entropy = self.pi_engine.pi_hash_entropy(wallet)
        self.stake_ledger[wallet] = self.stake_ledger.get(wallet, 0) + reward
        return {
            "wallet": wallet,
            "staked": amount,
            "multiplier": mult,
            "reward_est": reward,
            "entropy": entropy,
            "is_ultra_qualified": state.is_ultra,
            "tx_pi_proof": f"pi:{state.pi_phase:.6f}:{entropy}"
        }

# === Example Runner (for testing + iOS API) ===
if __name__ == "__main__":
    core = UltraCoreDiamond(node_id="ultra_diamond_pi_01")
    mesh = WaveMeshClient(core)
    staking = UltraStaking(core.pi_engine)

    # Simulate a measurement that hits your new ceramic + diamond target
    test_state = core.validate_sample(gpa=18.95, coherence_us=4.67, temp_k=298.0)

    print("STATE:", asdict(test_state))
    print("HEALTH:", test_state.health_score, "ULTRA:", test_state.is_ultra)
    print("MESH PAYLOAD:", mesh.build_ws_message())
    print("STAKING:", staking.stake("pi_wallet_abc123", 1000, test_state))

    # For FastAPI integration on wavemesh.io:
    # from fastapi import FastAPI
    # app = FastAPI()
    # @app.get("/ultra/status")
    # def status():
    #     return core.get_telemetry_payload()
