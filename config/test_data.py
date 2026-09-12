"""File-relative inputs and stable per-case synthetic data."""

import hashlib
import json
from pathlib import Path
from faker import Faker

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "test_data.json"


def load_data(path: Path = DATA_PATH) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        user = data["auth"]["invalid_user"]
        if not all(isinstance(user[k], str) and user[k] for k in ("email", "password")):
            raise ValueError("invalid_user email/password must be nonempty strings")
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
