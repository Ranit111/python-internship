"""
Script to dump OpenAPI JSON specification for Task 05 deliverable.
"""

import json
from pathlib import Path
from app.main import app

def export_spec():
    spec = app.openapi()
    out_file = Path(__file__).parent.parent / "openapi_spec.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"Exported OpenAPI spec to {out_file}")

if __name__ == "__main__":
    export_spec()
