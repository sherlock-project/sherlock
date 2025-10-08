import json
from pathlib import Path

REQUIRED_FIELDS = {"urlMain", "url", "errorType"}

def load_data():
    data_path = Path(__file__).parent.parent / "sherlock_project" / "resources" / "data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_sites_present_with_required_fields():
    data = load_data()
    for site in ["Ko-fi", "StackBlitz", "Modrinth"]:
        assert site in data, f"{site} entry missing in data.json"
        fields = set(data[site].keys())
        missing = REQUIRED_FIELDS - fields
        assert not missing, f"{site} missing fields: {missing}"

print("All tests passed.")