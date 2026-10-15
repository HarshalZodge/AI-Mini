"""
Test script to verify multi-turn agent inquiry and submission flow.
"""
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, SessionLocal
from agent import CivicAgent

def test_multi_turn_flow():
    init_db()
    db = SessionLocal()
    agent = CivicAgent(db)

    print("--- TURN 1: Citizen reports problem with missing details ---")
    t1_input = "There is a pothole on Pipeline Road, Savedi."
    history = []
    r1 = agent.run_agent_loop(t1_input, history)

    print("T1 Reply:\n", r1["reply"])
    print("T1 Steps:", [s["tool_name"] for s in r1["agent_steps"]])
    print("T1 Draft is None:", r1["complaint_draft"] is None)
    assert r1["complaint_draft"] is None, "Turn 1 draft must be None!"
    assert any(s["tool_name"] == "evaluate_completeness" for s in r1["agent_steps"]), "Turn 1 must log evaluate_completeness!"

    history.append({"role": "user", "content": t1_input})
    history.append({"role": "assistant", "content": r1["reply"]})

    print("\n--- TURN 2: Citizen provides landmark and hazard duration ---")
    t2_input = "It is near Premdan Chowk signal, for 3 days now. Two bikes slipped yesterday."
    r2 = agent.run_agent_loop(t2_input, history)

    print("T2 Reply:\n", r2["reply"])
    print("T2 Steps:", [s["tool_name"] for s in r2["agent_steps"]])
    print("T2 Draft Category:", r2["complaint_draft"]["category"] if r2["complaint_draft"] else None)
    print("T2 Draft Priority:", r2["complaint_draft"]["priority"] if r2["complaint_draft"] else None)
    print("T2 Draft Location:", r2["complaint_draft"]["location"] if r2["complaint_draft"] else None)
    assert r2["complaint_draft"] is not None, "Turn 2 draft must be generated!"
    assert r2["complaint_draft"]["category"] == "Roads & Potholes", "Category must be preserved across turns!"
    assert r2["complaint_draft"]["priority"] >= 4, "Priority should be elevated due to slip/hazard!"

    history.append({"role": "user", "content": t2_input})
    history.append({"role": "assistant", "content": r2["reply"]})

    print("\n--- TURN 3: Citizen confirms submission ---")
    t3_input = "Yes, please submit"
    r3 = agent.run_agent_loop(t3_input, history)

    print("T3 Reply:\n", r3["reply"])
    print("T3 Submitted Complaint:", r3["submitted_complaint"])
    assert r3["submitted_complaint"] is not None, "Turn 3 must record complaint!"
    assert "CR-2026-" in r3["submitted_complaint"]["tracking_id"], "Tracking ID must be valid!"

    print("\n✅ ALL 3 TURNS PASSED MULTI-TURN VERIFICATION!")

if __name__ == "__main__":
    test_multi_turn_flow()
