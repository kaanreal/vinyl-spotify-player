"""Display controller abstraction for circular UI."""

from __future__ import annotations

import logging


class DisplayController:
    def show_status(self, text: str) -> None:
        # TODO: render on actual display using pygame/Pillow/etc.
        logging.info("display: %s", text)
