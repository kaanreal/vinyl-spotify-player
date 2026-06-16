from __future__ import annotations

import logging
import threading
import time
from enum import Enum


class TonearmState(Enum):
    UP = "up"
    DOWN = "down"


try:
    import RPi.GPIO as GPIO

    _HAS_GPIO = True
except ImportError:
    _HAS_GPIO = False
    logging.warning("RPi.GPIO not available — running in mock mode")


class GPIOHandler:
    def __init__(self, config: dict):
        self._cfg = config["gpio"]
        self._tonearm_state = TonearmState.UP
        self._listeners: list[callable] = []
        self._running = False
        self._thread: threading.Thread | None = None

        if _HAS_GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._cfg["hall_sensor_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self._cfg["motor_pwm_pin"], GPIO.OUT)
            self._pwm = GPIO.PWM(self._cfg["motor_pwm_pin"], 100)
            self._pwm.start(0)
            if self._cfg.get("motor_dir_pin"):
                GPIO.setup(self._cfg["motor_dir_pin"], GPIO.OUT)
                GPIO.output(self._cfg["motor_dir_pin"], 0)
        else:
            self._pwm = None

    def on_tonearm_change(self, callback: callable) -> None:
        self._listeners.append(callback)

    @property
    def tonearm_state(self) -> TonearmState:
        return self._tonearm_state

    def set_motor(self, speed: float = 1.0) -> None:
        if _HAS_GPIO and self._pwm:
            duty = max(0, min(100, speed * 100))
            self._pwm.ChangeDutyCycle(duty)
            logging.info("motor PWM set to %.0f%%", duty)

    def set_motor_direction(self, forward: bool = True) -> None:
        if _HAS_GPIO:
            pin = self._cfg.get("motor_dir_pin")
            if pin:
                GPIO.output(pin, 1 if forward else 0)

    def stop_motor(self) -> None:
        if _HAS_GPIO and self._pwm:
            self._pwm.ChangeDutyCycle(0)
            logging.info("motor stopped")

    def start_monitoring(self) -> None:
        if not _HAS_GPIO:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop_monitoring(self) -> None:
        self._running = False

    def _monitor_loop(self) -> None:
        stable_for = 0
        while self._running:
            if _HAS_GPIO:
                is_down = GPIO.input(self._cfg["hall_sensor_pin"]) == 0
            else:
                is_down = False

            expected = TonearmState.DOWN if is_down else TonearmState.UP
            if expected != self._tonearm_state:
                stable_for += 1
                if stable_for >= 3:
                    old = self._tonearm_state
                    self._tonearm_state = expected
                    logging.info("tonearm %s -> %s", old.value, expected.value)
                    for cb in self._listeners:
                        cb(expected)
                    stable_for = 0
            else:
                stable_for = 0
            time.sleep(0.05)

    def cleanup(self) -> None:
        self.stop_monitoring()
        self.stop_motor()
        if _HAS_GPIO:
            self._pwm.stop()
            GPIO.cleanup()
