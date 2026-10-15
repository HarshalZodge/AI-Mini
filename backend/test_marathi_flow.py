"""
Test script to verify Marathi multi-turn inquiry and submission flow.
"""
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, SessionLocal
from agent import CivicAgent

def test_marathi_multi_turn():
    init_db()
    db = SessionLocal()
    agent = CivicAgent(db)

    print("--- TURN 1: Marathi initial grievance ---")
    t1 = "पाईपलाईन रोड, सावेडी येथे मोठा खड्डा पडला आहे आणि रस्ता खराब झाला आहे."
    history = []
    r1 = agent.run_agent_loop(t1, history)

    print("T1 Reply:\n", r1["reply"])
    assert r1["complaint_draft"] is None, "Turn 1 draft must be None!"
    assert "१. **नेमका रस्ता / लँडमार्क**" in r1["reply"] or "खड्डा" in r1["reply"]

    history.append({"role": "user", "content": t1})
    history.append({"role": "assistant", "content": r1["reply"]})

    print("\n--- TURN 2: Marathi clarification reply ---")
    t2 = "प्रेमदान चौकाजवळ, ३ दिवसांपासून हा खड्डा आहे आणि काल दुचाकी घसरून अपघात झाला."
    r2 = agent.run_agent_loop(t2, history)

    print("T2 Reply:\n", r2["reply"])
    print("T2 Draft Priority:", r2["complaint_draft"]["priority"] if r2["complaint_draft"] else None)
    assert r2["complaint_draft"] is not None, "Turn 2 draft must be generated!"
    assert r2["complaint_draft"]["priority"] >= 4, "Accident/slip must trigger high priority!"

    print("\n✅ MARATHI MULTI-TURN VERIFICATION PASSED!")

if __name__ == "__main__":
    test_marathi_multi_turn()
