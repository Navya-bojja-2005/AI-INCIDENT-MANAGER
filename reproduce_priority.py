
import ai_engine
import importlib
importlib.reload(ai_engine)
from ai_engine import assign_priority_rule_based

test_cases = [
    "mouse is not working"
]

print("--- TESTING PRIORITY LOGIC (RELOADED) ---")
for text in test_cases:
    print(f"Testing input: {repr(text)}", flush=True)
    priority = assign_priority_rule_based(text)
    print(f"'{text}' -> {priority}", flush=True)
