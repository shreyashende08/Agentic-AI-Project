"""
Agentic AI System — Main Entry Point
Author: Shreya Shailendra Shende
Theme: Decision-Making AI / Autonomous Systems

Run:
    python main.py
    python main.py --scenario healthcare
    python main.py --scenario logistics
    python main.py --scenario energy
"""

import argparse
import time
from agent import AgentCore
from planner import TaskPlanner
from environment import Environment
from logger import SimulationLogger

def run_simulation(scenario: str = "smart_city"):
    print("\n" + "=" * 60)
    print("   AGENTIC AI — Autonomous Decision-Making System")
    print("=" * 60)
    print(f"   Scenario : {scenario.upper().replace('_', ' ')}")
    print(f"   Mode     : Autonomous (no human intervention)")
    print("=" * 60 + "\n")

    logger = SimulationLogger(scenario)

    env = Environment(scenario)
    print(f"[ENV]  Environment loaded → {len(env.tasks)} tasks detected\n")

    planner = TaskPlanner(strategy="priority_rl")
    agent   = AgentCore(name="Agentic-Core-v1", planner=planner)

    print("[AGENT] Starting perception → reasoning → planning → execution loop\n")
    state = env.observe()

    for cycle in range(1, 6):
        print(f"── Cycle {cycle} {'─' * 40}")

        observation = env.observe()
        print(f"  [PERCEIVE]  Observed {len(observation['pending_tasks'])} pending tasks | "
              f"env_stress={observation['stress_level']:.2f}")

        reasoning = agent.reason(observation)
        print(f"  [REASON]    Priority task → '{reasoning['top_task']}' | "
              f"confidence={reasoning['confidence']:.0%}")

        plan = planner.generate_plan(reasoning)
        print(f"  [PLAN]      {len(plan['steps'])} steps planned | "
              f"estimated_gain={plan['efficiency_gain']:.0%}")

        result = agent.execute(plan, env)
        print(f"  [EXECUTE]   {result['actions_completed']} actions done | "
              f"efficiency={result['efficiency']:.0%} | "
              f"status={result['status']}\n")

        logger.log_cycle(cycle, observation, reasoning, plan, result)
        env.step()
        time.sleep(0.3)

    report = logger.summary()
    print("=" * 60)
    print("   SIMULATION COMPLETE — Summary Report")
    print("=" * 60)
    print(f"  Total cycles        : {report['cycles']}")
    print(f"  Avg efficiency gain : {report['avg_efficiency']:.1%}")
    print(f"  Tasks resolved      : {report['tasks_resolved']}")
    print(f"  Human interventions : {report['human_interventions']}  ✓ (fully autonomous)")
    print(f"  Decision latency    : {report['avg_latency_ms']} ms avg")
    print("=" * 60 + "\n")

    logger.save_results()
    print("[DONE]  Results saved to results/\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic AI Simulation")
    parser.add_argument(
        "--scenario",
        choices=["smart_city", "healthcare", "logistics", "energy"],
        default="smart_city",
        help="Choose simulation scenario (default: smart_city)"
    )
    args = parser.parse_args()
    run_simulation(args.scenario)
