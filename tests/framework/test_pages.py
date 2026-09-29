from unittest.mock import MagicMock

import pytest

from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.shop_page import ShopPage

pytestmark = pytest.mark.framework


def test_paths_come_from_each_page_template():
    page = MagicMock()
    assert HomePage(page).url_for() == "/"
    assert ContactPage(page).url_for() == "/contacto/"
    assert ProductPage(page).url_for(slug="qa-remera") == "/productos/qa-remera/"


@pytest.mark.parametrize(
    "page_class,params",
    [(ProductPage, {}), (HomePage, {"slug": "extra"}), (ProductPage, {"id": "x"})],
    ids=["missing", "unexpected", "wrong-name"],
)
def test_open_rejects_mismatched_parameters(page_class, params):
    page = MagicMock()
    with pytest.raises(TypeError):
        page_class(page).open(**params)
    page.goto.assert_not_called()


@pytest.mark.parametrize("slug", ["../admin", "QA-Remera", "a/b", "", "x?q=1"])
def test_open_rejects_unsafe_path_segments(slug):
    page = MagicMock()
    with pytest.raises(ValueError):
        ProductPage(page).open(slug=slug)
    page.goto.assert_not_called()


def test_components_are_built_on_first_use():
    page = MagicMock()
    home = HomePage(page)
    assert "cart" not in vars(home)
    assert home.cart is home.cart
    assert home.cart.trigger is home.navbar.cart_link


@pytest.mark.parametrize(
    "page_class,path,shown",
    [
        (ProductPage, "/productos/qa-remera/", True),
        (ProductPage, "/productos/qa-remera", True),
        (ProductPage, "/productos/", False),
        (ProductPage, "/productos/a/b/", False),
        (ShopPage, "/productos/", True),
        (ShopPage, "/productos/qa-remera/", False),
        (HomePage, "/", True),
        (HomePage, "/contacto/", False),
    ],
)
def test_each_page_recognizes_its_own_path(page_class, path, shown):
    # Content waits rely on this to tell the new page from the previous one.
    assert page_class(MagicMock()).shows_path(path) is shown
