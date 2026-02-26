
from ai_engine import assign_priority_rule_based

test_cases = [
    "The server is down and production is halted",   # Expected: High
    "I cannot login to the application",             # Expected: Medium
    "My mouse is not working",                       # Expected: Low
    "There is a typo on the dashboard",              # Expected: Low
    "The application is throwing an unknown error",  # Expected: Medium
    "Firewall breach detected",                      # Expected: High
    "Printer is jammed",                             # Expected: Low
    "System latency is high",                        # Expected: Medium (latency)
    "Please reset my password",                      # Expected: Low (reset password in Low list)
]

print("--- TESTING PRIORITY LOGIC ---")
for text in test_cases:
    priority = assign_priority_rule_based(text)
    print(f"Input: '{text}'\n  -> Priority: {priority}")
