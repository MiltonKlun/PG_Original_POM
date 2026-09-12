import pytest
from config.test_data import contact_data, load_data

pytestmark = pytest.mark.framework


def test_case_data_is_order_independent():
    original = contact_data("contact/accented", 42)
    contact_data("another-case", 42)
    assert contact_data("contact/accented", 42) == original
    assert original["email"].endswith("@example.com")
    assert contact_data("contact/accented", 43) != original


def test_data_path_is_independent_of_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert load_data()["auth"]["invalid_user"]["email"] == "invalid@example.com"


@pytest.mark.parametrize("content", ["broken JSON", "{}", '{"auth": null}'])
def test_malformed_data_has_context(tmp_path, content):
    path = tmp_path / "data.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid test data"):
        load_data(path)
