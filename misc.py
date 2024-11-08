import random
import pyautogui
import pywinctl as pwc

from typing import Tuple, Any
from dataclasses import dataclass


@dataclass
class Utilities:

    @staticmethod
    def get_rect(window) -> Tuple[int, int, int, int]:
        x_jitter = random.randint(-5, 5)
        y_jitter = random.randint(-5, 5)
        return window.left + x_jitter, window.top + y_jitter, window.width, window.height


    @staticmethod
    def capture_screenshot(rect: Tuple[int, int, int, int]) -> Any:
        return pyautogui.screenshot(region=rect)

    @staticmethod
    def get_window() -> Any:
        windows = next(
            (
                pwc.getWindowsWithTitle(opt)
                for opt in ["TelegramDesktop", "64Gram", "Nekogram", "AyuGram"]
                if pwc.getWindowsWithTitle(opt)
            ),
            None,
        )

        if windows and not windows[0].isActive:
            windows[0].minimize()
            windows[0].restore()
            return windows[0]
        return None