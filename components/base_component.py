from dataclasses import dataclass
from playwright.sync_api import Locator, expect


class BaseComponent:
    """A UI region located by its root; child locators are scoped to it."""

    def __init__(self, root: Locator) -> None:
        self.root = root
        self.page = root.page


@dataclass(frozen=True)
class Disclosure:
    """A header control that opens a panel (search, menu or cart drawer)."""

    trigger: Locator
    panel: Locator
    close_control: Locator

    def open_with_keyboard(self) -> None:
        self.trigger.focus()
        self.trigger.press("Enter")
        expect(self.panel).to_be_visible()

    def close_with_escape(self) -> None:
        self.panel.page.keyboard.press("Escape")

    @property
    def focus_inside(self) -> Locator:
        """The focused element, if it is the panel itself or inside it."""
        focused = self.panel.page.locator(":focus")
        return self.panel.locator(":focus").or_(self.panel.and_(focused))
