import os

# Tests never write usage stats to the real database (test_usage.py points
# usage.py at a temporary one when it needs to).
os.environ["MATHQUEST_USAGE_DB"] = "off"
