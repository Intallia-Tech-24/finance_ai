import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_server import utils

def test_utils():
    print("=== Test: File Exists ===")
    print(utils.file_exists("HDFC", "income"))  # Should be True if file exists
    print(utils.file_exists("XYZ", "income"))   # Should be False

    print("\n=== Test: Load Financial CSV ===")
    df = utils.load_financial_csv("HDFC", "income")
    print(df.head(2))

    print("\n=== Test: Get Row by Label ===")
    row = utils.get_row_by_label(df, "Net Income")
    print(row)

if __name__ == "__main__":
    test_utils()
