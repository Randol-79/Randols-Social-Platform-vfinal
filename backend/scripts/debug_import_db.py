import traceback
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import database
    import database.models as m

    print("Imported database.models successfully")
except Exception:
    traceback.print_exc()
    raise
