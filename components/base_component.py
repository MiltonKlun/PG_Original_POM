from playwright.sync_api import Locator


class BaseComponent:
    """A UI region located by its root; child locators are scoped to it."""

    def __init__(self, root: Locator) -> None:
        self.root = root
        self.page = root.page
