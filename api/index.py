import sys
import os

# Add backend directory to sys.path so backend modules (main, db, agent, tools, schemas, seed) resolve cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(root_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app
