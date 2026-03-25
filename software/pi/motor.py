"""Motor controller abstraction.

Replace print/log placeholders with real GPIO/PWM implementation.
"""

from __future__ import annotations

import logging


class MotorController:
    def __init__(self) -> None:
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        logging.info("motor start")
        # TODO: set PWM duty cycle / driver enable

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        logging.info("motor stop")
        # TODO: disable PWM / driver

    @property
    def running(self) -> bool:
        return self._running
