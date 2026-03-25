#!/usr/bin/env python3
"""Main runtime loop for vinyl-spotify-player.

This is a hardware-safe starter implementation with placeholder hooks for
Spotify integration. It focuses on deterministic state transitions and logging.
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from enum import Enum

from motor import MotorController
from display import DisplayController


class State(str, Enum):
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"


class TonearmSensor:
    """Placeholder tonearm sensor.

    Replace `is_down` with real GPIO/Hall-effect implementation.
    """

    def is_down(self) -> bool:
        return False


class PlayerRuntime:
    def __init__(self) -> None:
        self.state = State.IDLE
        self.running = True
        self.sensor = TonearmSensor()
        self.motor = MotorController()
        self.display = DisplayController()

    def set_state(self, new_state: State) -> None:
        if new_state == self.state:
            return
        logging.info("state transition: %s -> %s", self.state.value, new_state.value)
        self.state = new_state

        if new_state == State.PLAYING:
            self.motor.start()
            self.display.show_status("Now Playing")
            # TODO: spotify.play()
        elif new_state in (State.PAUSED, State.IDLE):
            self.motor.stop()
            self.display.show_status("Paused")
            # TODO: spotify.pause()

    def tick(self) -> None:
        tonearm_down = self.sensor.is_down()

        if tonearm_down and self.state != State.PLAYING:
            self.set_state(State.PLAYING)
        elif not tonearm_down and self.state == State.PLAYING:
            self.set_state(State.PAUSED)

    def shutdown(self) -> None:
        logging.info("shutting down runtime")
        self.running = False
        self.motor.stop()
        self.display.show_status("Offline")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> int:
    setup_logging()
    runtime = PlayerRuntime()

    def _handle_signal(_sig, _frame):
        runtime.shutdown()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    runtime.display.show_status("Ready")
    logging.info("vinyl runtime started")

    while runtime.running:
        runtime.tick()
        time.sleep(0.1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
