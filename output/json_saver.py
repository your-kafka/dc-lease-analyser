import json
from datetime import datetime

def save_json(extracted: dict, file_path: str, file_type: str, method: str, output_path: str):
    payload = {
        "metadata": {
            "source_file": file_path,
            "file_type": file_type,
            "extraction_method": method,
            "extracted_at": datetime.now().isoformat(),
        },
        "extracted": extracted,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)