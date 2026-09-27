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
        shirt = data["shop"]["shirt"]
        for variant in (shirt, shirt["alternate"]):
            for key in ("size", "color", "variant"):
                if not isinstance(variant[key], str):
                    raise ValueError("Variant fields must be strings")
        if shirt["alternate"]["variant"] == shirt["variant"]:
            raise ValueError("Alternate variant must differ from the default")
        pricing = shirt["pricing"]
        for tier in (pricing["discounted"], pricing["regular"]):
            if type(tier["price"]) is not int or tier["price"] <= 0:
                raise ValueError("Price must be positive integer minor units")
            if not (
                isinstance(tier["color"], str) and isinstance(tier["variant"], str)
            ):
                raise ValueError("Variant fields must be strings")
        discounted = pricing["discounted"]
        if type(discounted["compare_at"]) is not int or (
            discounted["compare_at"] <= discounted["price"]
        ):
            raise ValueError("Compare-at price must be an integer above price")
        if pricing["regular"]["compare_at"] is not None:
            raise ValueError("Regular price must not have a compare-at price")
        catalog = data["shop"]["catalog"]
        if type(catalog["page_size"]) is not int or catalog["page_size"] < 1:
            raise ValueError("Catalog page size must be a positive integer")
        if len(set(catalog["products"])) != len(catalog["products"]):
            raise ValueError("Catalog product names must be unique")
        for rows, keys in [
            (data["search_cases"], ("id", "term")),
            (data["filter_cases"], ("id", "name", "value")),
        ]:
            ids = set()
            for case in rows:
                if not all(isinstance(case[k], str) and case[k].strip() for k in keys):
                    raise ValueError("Case fields must be nonempty strings")
                expected = case["expected"]
                if not expected or not all(isinstance(n, str) for n in expected):
                    raise ValueError("Expected results must be product names")
                if case["id"] in ids:
                    raise ValueError("Case IDs must be unique")
                ids.add(case["id"])
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
