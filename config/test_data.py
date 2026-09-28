"""Validated, typed test inputs and stable per-case synthetic data."""

import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

from faker import Faker

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "test_data.json"


@dataclass(frozen=True)
class Credentials:
    id: str
    email: str
    password: str


@dataclass(frozen=True)
class ContactInput:
    name: str
    email: str
    message: str


@dataclass(frozen=True)
class ContactCase(ContactInput):
    id: str


@dataclass(frozen=True)
class SearchCase:
    id: str
    term: str
    expected: tuple[str, ...]


@dataclass(frozen=True)
class FilterCase:
    id: str
    name: str
    value: str
    expected: tuple[str, ...]


@dataclass(frozen=True)
class Variant:
    """A selectable size and color, and the label the cart shows for it."""

    size: str
    color: str
    label: str


@dataclass(frozen=True)
class PriceTier:
    """Price of the variants in one color; compare-at only on promotions."""

    color: str
    label: str
    price: int
    compare_at: int | None


@dataclass(frozen=True)
class Product:
    name: str
    price: int


@dataclass(frozen=True)
class VariantProduct(Product):
    default: Variant
    alternate: Variant
    discounted: PriceTier
    regular: PriceTier


@dataclass(frozen=True)
class Catalog:
    page_size: int
    products: tuple[str, ...]


@dataclass(frozen=True)
class Shop:
    shirt: VariantProduct
    cap: Product
    unavailable: str
    catalog: Catalog


@dataclass(frozen=True)
class SuiteData:
    invalid_logins: tuple[Credentials, ...]
    shop: Shop
    contact_cases: tuple[ContactCase, ...]
    search_cases: tuple[SearchCase, ...]
    filter_cases: tuple[FilterCase, ...]


class _Case(Protocol):
    @property
    def id(self) -> str: ...


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def _amount(value: Any, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field} must be positive integer minor units")
    return value


def _names(values: Any, field: str) -> tuple[str, ...]:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{field} must be a nonempty list")
    return tuple(_text(value, field) for value in values)


def _rows(values: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{field} must be a nonempty list")
    return values


def _unique_ids[C: _Case](cases: list[C], field: str) -> tuple[C, ...]:
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{field} IDs must be unique")
    return tuple(cases)


def _variant(raw: dict[str, Any], field: str) -> Variant:
    return Variant(
        _text(raw["size"], f"{field}.size"),
        _text(raw["color"], f"{field}.color"),
        _text(raw["variant"], f"{field}.variant"),
    )


def _tier(raw: dict[str, Any], field: str) -> PriceTier:
    compare_at = raw["compare_at"]
    return PriceTier(
        _text(raw["color"], f"{field}.color"),
        _text(raw["variant"], f"{field}.variant"),
        _amount(raw["price"], f"{field}.price"),
        None if compare_at is None else _amount(compare_at, f"{field}.compare_at"),
    )


def _shop(raw: dict[str, Any]) -> Shop:
    shirt, pricing = raw["shirt"], raw["shirt"]["pricing"]
    product = VariantProduct(
        name=_text(shirt["name"], "shirt.name"),
        price=_amount(shirt["price"], "shirt.price"),
        default=_variant(shirt, "shirt"),
        alternate=_variant(shirt["alternate"], "shirt.alternate"),
        discounted=_tier(pricing["discounted"], "pricing.discounted"),
        regular=_tier(pricing["regular"], "pricing.regular"),
    )
    if product.alternate.label == product.default.label:
        raise ValueError("Alternate variant must differ from the default")
    discounted = product.discounted
    if discounted.compare_at is None or discounted.compare_at <= discounted.price:
        raise ValueError("Discounted compare-at price must be above its price")
    if product.regular.compare_at is not None:
        raise ValueError("Regular price must not have a compare-at price")
    catalog = Catalog(
        _amount(raw["catalog"]["page_size"], "catalog.page_size"),
        _names(raw["catalog"]["products"], "catalog.products"),
    )
    if len(set(catalog.products)) != len(catalog.products):
        raise ValueError("Catalog product names must be unique")
    return Shop(
        shirt=product,
        cap=Product(
            _text(raw["cap"]["name"], "cap.name"),
            _amount(raw["cap"]["price"], "cap.price"),
        ),
        unavailable=_text(raw["unavailable"]["name"], "unavailable.name"),
        catalog=catalog,
    )


def _parse(data: dict[str, Any]) -> SuiteData:
    logins = [
        Credentials(
            _text(row["id"], "login.id"),
            _text(row["email"], "login.email"),
            _text(row["password"], "login.password"),
        )
        for row in _rows(data["auth"]["invalid_users"], "auth.invalid_users")
    ]
    contacts = [
        ContactCase(
            name=_text(row["name"], "contact.name"),
            email=_text(row["email"], "contact.email"),
            message=_text(row["message"], "contact.message"),
            id=_text(row["id"], "contact.id"),
        )
        for row in _rows(data["contact_cases"], "contact_cases")
    ]
    searches = [
        SearchCase(
            _text(row["id"], "search.id"),
            _text(row["term"], "search.term"),
            _names(row["expected"], "search.expected"),
        )
        for row in _rows(data["search_cases"], "search_cases")
    ]
    filters = [
        FilterCase(
            _text(row["id"], "filter.id"),
            _text(row["name"], "filter.name"),
            _text(row["value"], "filter.value"),
            _names(row["expected"], "filter.expected"),
        )
        for row in _rows(data["filter_cases"], "filter_cases")
    ]
    return SuiteData(
        invalid_logins=_unique_ids(logins, "auth.invalid_users"),
        shop=_shop(data["shop"]),
        contact_cases=_unique_ids(contacts, "contact_cases"),
        search_cases=_unique_ids(searches, "search_cases"),
        filter_cases=_unique_ids(filters, "filter_cases"),
    )


@lru_cache
def load_data(path: Path = DATA_PATH) -> SuiteData:
    try:
        return _parse(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f"Invalid test data in {path}: {exc}") from exc


def contact_data(case_id: str, seed: int) -> ContactInput:
    digest = hashlib.sha256(f"{seed}:{case_id}".encode()).digest()
    fake = Faker("es_AR")
    fake.seed_instance(int.from_bytes(digest[:8], "big"))
    return ContactInput(
        name=fake.name(),
        email=f"qa-{digest.hex()[:12]}@example.com",
        message=fake.text(max_nb_chars=200),
    )
