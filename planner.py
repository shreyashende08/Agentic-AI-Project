"""
planner.py — TaskPlanner
Converts agent reasoning into an ordered, executable action plan.
"""

import random
from typing import Dict, Any, List

ACTION_TEMPLATES: Dict[str, List[str]] = {
    "reroute_vehicles":    ["scan_traffic_grid",    "compute_alt_paths",       "dispatch_reroute_signal"],
    "load_balance":        ["monitor_grid_load",    "identify_overload_nodes", "redistribute_power"],
    "alert_medical_team":  ["verify_vitals_feed",   "classify_severity",       "notify_on_call_doctor"],
    "find_alt_route":      ["query_route_db",       "check_availability",      "update_dispatch_order"],
    "switch_to_backup":    ["ping_backup_sensor",   "validate_data_stream",    "reroute_data_pipeline"],
    "rebalance_resources": ["audit_resource_pool",  "rank_deficits",           "reallocate_units"],
    "escalate_analysis":   ["capture_anomaly_log",  "run_pattern_match",       "flag_for_review"],
    "monitor":             ["idle_scan"],
    "generic_response":    ["log_event",            "notify_operator"],
}


class TaskPlanner:
    def __init__(self, strategy: str = "priority_rl"):
        self.strategy    = strategy
        self._plan_count = 0

    def generate_plan(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        self._plan_count += 1
        action = reasoning["action"]
        task   = reasoning["top_task"]
        conf   = reasoning["confidence"]

        sub_steps = ACTION_TEMPLATES.get(action, ACTION_TEMPLATES["generic_response"])

        steps = []
        for i, sub in enumerate(sub_steps):
            steps.append({
                "step_id":  i + 1,
                "action":   sub,
                "target":   task,
                "priority": round(conf - i * 0.05, 3),
            })

        # Secondary tasks (multi-agent style)
        for sec in reasoning.get("all_scored", [])[1:3]:
            sec_steps = ACTION_TEMPLATES.get(sec["action"], ["log_event"])
            steps.append({
                "step_id":  len(steps) + 1,
                "action":   sec_steps[0],
                "target":   sec["task"],
                "priority": round(sec["score"] * 0.6, 3),
            })

        steps.sort(key=lambda x: x["priority"], reverse=True)

        efficiency = min(conf * 0.45 + 0.05 * len(steps) + random.uniform(0, 0.05), 0.98)

        return {
            "plan_id":         self._plan_count,
            "primary_action":  action,
            "steps":           steps,
            "efficiency_gain": efficiency,
            "strategy_used":   self.strategy,
        }
