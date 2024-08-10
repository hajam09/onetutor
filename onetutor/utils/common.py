from collections.abc import Iterable
from enum import (
    Enum,
    auto
)


class Render(Enum):
    TEMPLATE = auto()
    FORM = auto()


class SettingTab:
    def __init__(self, code, name, render):
        self.code = code
        self.name = name
        self.render = render


tutorTabs = [
    SettingTab('password', 'Password Change', Render.FORM),
]

studentTabs = [
]

parentTabs = [

]


def getSettingByTabCode(tabs: Iterable, code: str) -> SettingTab | None:
    return next((tab for tab in tabs if tab.code == code), None)
