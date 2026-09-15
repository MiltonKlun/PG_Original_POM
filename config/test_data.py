"""File-relative inputs and stable per-case synthetic data."""

import hashlib
import json
from pathlib import Path
from faker import Faker

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "test_data.json"


def load_data(path: Path = DATA_PATH) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for rows, keys in [
            (data["auth"]["invalid_users"], ("id", "email", "password")),
            (data["contact_cases"], ("id", "name", "email", "message")),
        ]:
            if not isinstance(rows, list) or not rows:
                raise ValueError("Named test cases must be a nonempty list")
            ids = set()
            for row in rows:
                if not all(isinstance(row[k], str) and row[k] for k in keys):
                    raise ValueError("Case fields must be nonempty strings")
                if row["id"] in ids:
                    raise ValueError("Case IDs must be unique")
                ids.add(row["id"])
        for key in ("shirt", "cap", "unavailable"):
            if not isinstance(data["shop"][key]["name"], str):
                raise ValueError("Product name must be a string")
        for key in ("shirt", "cap"):
            price = data["shop"][key]["price"]
            if type(price) is not int or price <= 0:
                raise ValueError("Price must be positive integer minor units")
        for key in ("size", "color", "variant"):
            if not isinstance(data["shop"]["shirt"][key], str):
                raise ValueError("Variant fields must be strings")
        return data
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f"Invalid test data in {path}: {exc}") from exc


def contact_data(case_id: str, seed: int) -> dict[str, str]:
    digest = hashlib.sha256(f"{seed}:{case_id}".encode()).digest()
    fake = Faker("es_AR")
    fake.seed_instance(int.from_bytes(digest[:8], "big"))
    return {
        "name": fake.name(),
        "email": f"qa-{digest.hex()[:12]}@example.com",
        "message": fake.text(max_nb_chars=200),
    }
