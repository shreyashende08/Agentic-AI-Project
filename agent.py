"""
agent.py — AgentCore
Handles Reason and Execute stages using a Knowledge Graph + Q-table (RL).
"""

import random
from typing import Dict, Any

KNOWLEDGE_GRAPH = {
    "traffic_jam":       {"cause": "high_vehicle_density", "action": "reroute_vehicles",   "domain": "smart_city"},
    "power_surge":       {"cause": "peak_demand",          "action": "load_balance",        "domain": "energy"},
    "patient_critical":  {"cause": "vitals_anomaly",       "action": "alert_medical_team",  "domain": "healthcare"},
    "supply_delay":      {"cause": "route_congestion",     "action": "find_alt_route",      "domain": "logistics"},
    "sensor_fault":      {"cause": "hardware_failure",     "action": "switch_to_backup",    "domain": "all"},
    "resource_shortage": {"cause": "demand_spike",         "action": "rebalance_resources", "domain": "all"},
    "anomaly_detected":  {"cause": "unknown_pattern",      "action": "escalate_analysis",   "domain": "all"},
}

Q_TABLE: Dict[str, float] = {
    "traffic_jam_high":        0.92,
    "power_surge_high":        0.88,
    "patient_critical_high":   0.97,
    "supply_delay_medium":     0.75,
    "sensor_fault_low":        0.60,
    "resource_shortage_high":  0.85,
    "anomaly_detected_medium": 0.70,
}

def _stress_bucket(stress: float) -> str:
    if stress >= 0.7:   return "high"
    elif stress >= 0.4: return "medium"
    return "low"


class AgentCore:
    def __init__(self, name: str, planner):
        self.name    = name
        self.planner = planner
        self.memory  = []
        self.q_table = Q_TABLE.copy()
        self._cycle  = 0

    def reason(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        pending = observation["pending_tasks"]
        stress  = observation["stress_level"]
        bucket  = _stress_bucket(stress)

        scored = []
        for task in pending:
            key   = f"{task}_{bucket}"
            score = self.q_table.get(key, 0.5 + random.uniform(-0.05, 0.1))
            kg    = KNOWLEDGE_GRAPH.get(task, {})
            scored.append({
                "task":   task,
                "score":  score,
                "action": kg.get("action", "generic_response"),
                "cause":  kg.get("cause",  "unknown"),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[0] if scored else {"task": "idle", "score": 0.5, "action": "monitor", "cause": "none"}

        self.memory.append({"cycle": self._cycle, "top_task": top["task"], "score": top["score"]})
        if len(self.memory) > 10:
            self.memory.pop(0)

        return {
            "top_task":   top["task"],
            "action":     top["action"],
            "cause":      top["cause"],
            "confidence": min(top["score"], 0.99),
            "all_scored": scored,
        }

    def execute(self, plan: Dict[str, Any], env) -> Dict[str, Any]:
        self._cycle += 1
        completed      = 0
        efficiency_sum = 0.0

        for step in plan["steps"]:
            outcome = env.apply_action(step["action"], step["target"])
            if outcome["success"]:
                completed      += 1
                efficiency_sum += outcome["efficiency"]

            # Q-table update: Q ← Q + α(reward − Q)
            alpha   = 0.1
            key     = f"{step['target']}_{_stress_bucket(env.observe()['stress_level'])}"
            old_q   = self.q_table.get(key, 0.5)
            self.q_table[key] = old_q + alpha * (outcome["efficiency"] - old_q)

        avg_eff = efficiency_sum / max(completed, 1)
        return {
            "actions_completed": completed,
            "efficiency":        avg_eff,
            "status":            "SUCCESS" if completed == len(plan["steps"]) else "PARTIAL",
        }
