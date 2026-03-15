"""
environment.py — Simulated Environment
Generates dynamic tasks and responds to agent actions.
Scenarios: smart_city, healthcare, logistics, energy
"""

import random
from typing import Dict, Any, List

SCENARIO_TASKS: Dict[str, List[str]] = {
    "smart_city": ["traffic_jam",      "sensor_fault", "resource_shortage", "anomaly_detected"],
    "healthcare": ["patient_critical", "sensor_fault", "resource_shortage", "anomaly_detected"],
    "logistics":  ["supply_delay",     "sensor_fault", "resource_shortage", "anomaly_detected"],
    "energy":     ["power_surge",      "sensor_fault", "resource_shortage", "anomaly_detected"],
}


class Environment:
    def __init__(self, scenario: str = "smart_city"):
        self.scenario    = scenario
        self.task_pool   = SCENARIO_TASKS.get(scenario, SCENARIO_TASKS["smart_city"])
        self.tasks       = random.choices(self.task_pool, k=random.randint(3, 4))
        self._stress     = round(random.uniform(0.4, 0.7), 2)
        self._step_count = 0

    def observe(self) -> Dict[str, Any]:
        return {
            "scenario":      self.scenario,
            "pending_tasks": list(self.tasks),
            "stress_level":  round(self._stress, 2),
            "step":          self._step_count,
        }

    def apply_action(self, action: str, target: str) -> Dict[str, Any]:
        resolved = target in self.tasks
        if resolved:
            self.tasks   = [t for t in self.tasks if t != target]
            self._stress = max(0.0, self._stress - random.uniform(0.05, 0.12))
            eff = round(random.uniform(0.72, 0.96), 3)
        else:
            eff = round(random.uniform(0.50, 0.70), 3)

        return {"success": True, "resolved": resolved, "efficiency": eff}

    def step(self):
        self._step_count += 1
        self._stress = min(1.0, self._stress + random.uniform(0.02, 0.06))
        if random.random() < 0.6:
            new_task = random.choice(self.task_pool)
            if new_task not in self.tasks:
                self.tasks.append(new_task)
