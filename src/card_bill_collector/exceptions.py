from typing import Dict


class NoVisibleWindowError(Exception):
    def __init__(self, screen_info: Dict):
        super().__init__(f"Could find any visible window on current screen: {screen_info}")