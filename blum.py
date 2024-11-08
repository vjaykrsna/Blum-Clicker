import asyncio
import random
from itertools import product
import mouse
import keyboard

from misc import Utilities
from logger import logger
from localization import get_language
from config import get_config_value
from typing import Tuple, Any


class BlumClicker:
    def __init__(self):
        self.utils = Utilities()
        self.paused: bool = True
        self.window_options: str | None = None
        self.replays: int = 0

    async def handle_input(self) -> bool:
        if keyboard.is_pressed(get_config_value("START_HOTKEY")) and self.paused:
            self.paused = False
            logger.info(get_language("PRESS_P_TO_PAUSE"))
            await asyncio.sleep(0.2)
        elif keyboard.is_pressed(get_config_value("TOGGLE_HOTKEY")):
            self.paused = not self.paused
            logger.info(
                get_language("PROGRAM_PAUSED")
                if self.paused
                else get_language("PROGRAM_RESUMED")
            )
            await asyncio.sleep(0.2)
        return self.paused

    @staticmethod
    async def collect_green(screen: Any, rect: Tuple[int, int, int, int], side: str) -> bool:
        width, height = screen.size
        x_start = 0 if side == "left" else width // 2
        x_end = width // 2 if side == "left" else width
        y_range = range(int(height * 0.25), height, 20)
        
        if random.random() < 0.02:
            y_range = range(0, int(height * 0.25), 20)

        bomb_positions = []

        for x, y in product(range(x_start, x_end, 20), y_range):
            r, g, b = screen.getpixel((x, y))
            greenish_range = (100 <= r <= 180) and (210 <= g <= 255) and (b < 100)
            bomb_range = (100 <= r <= 150) and (100 <= g <= 150) and (100 <= b <= 150)

            if bomb_range:
                bomb_positions.append((x, y))
                continue
            
            if greenish_range and not BlumClicker.is_near_bomb(x, y, bomb_positions, 30):
                screen_x = rect[0] + x
                screen_y = rect[1] + y
                mouse.move(screen_x, screen_y, absolute=True)
                mouse.click(button=mouse.LEFT)
                await asyncio.sleep(random.uniform(0.05, 0.2))
                return True
        return False

    @staticmethod
    def is_near_bomb(x: int, y: int, bomb_positions: list, radius: int) -> bool:
        """Check if (x, y) is within `radius` pixels of any bomb position."""
        return any((bx - x) ** 2 + (by - y) ** 2 < radius ** 2 for bx, by in bomb_positions)

    async def run(self) -> None:
        try:
            window = self.utils.get_window()
            if not window:
                return logger.error(get_language("WINDOW_NOT_FOUND"))
            logger.info(get_language("CLICKER_INITIALIZED"))
            logger.info(get_language("FOUND_WINDOW").format(window=window.title))
            logger.info(get_language("PRESS_S_TO_START"))

            while True:
                if await self.handle_input():
                    continue
                rect = self.utils.get_rect(window)
                screenshot = self.utils.capture_screenshot(rect)
                await asyncio.gather(
                    self.collect_green(screenshot, rect, "left"),
                    self.collect_green(screenshot, rect, "right")
                )
        except (Exception, ExceptionGroup) as error:
            logger.error(get_language("WINDOW_CLOSED").format(error=error))
