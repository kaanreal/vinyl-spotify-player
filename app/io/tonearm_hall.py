"""Tonearm hall effect sensor - play/pause control."""

import time
from abc import ABC, abstractmethod
from typing import Callable, Optional
from app.io.platform import Platform
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class TonearmSensor(ABC):
    """Abstract base class for tonearm sensor."""
    
    @abstractmethod
    def is_down(self) -> bool:
        """Check if tonearm is down (on record).
        
        Returns:
            bool: True if tonearm is down
        """
        pass
    
    @abstractmethod
    def start_monitoring(self, on_change: Callable[[bool], None]) -> None:
        """Start monitoring tonearm state changes.
        
        Args:
            on_change: Callback function(is_down) called on state change
        """
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop monitoring tonearm state."""
        pass


class RealTonearmSensor(TonearmSensor):
    """Real tonearm sensor using GPIO and hall effect sensor."""
    
    def __init__(self, hall_pin: int, poll_interval_ms: int = 50):
        """Initialize real tonearm sensor.
        
        Args:
            hall_pin: GPIO pin number for hall effect sensor
            poll_interval_ms: Polling interval in milliseconds
        """
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
        except ImportError:
            raise RuntimeError("RPi.GPIO not available - use StubTonearmSensor instead")
        
        self.hall_pin = hall_pin
        self.poll_interval = poll_interval_ms / 1000.0
        self.monitoring = False
        self._last_state = None
        
        # Set up GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.hall_pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        
        logger.info(f"Real tonearm sensor initialized on GPIO {hall_pin}")
    
    def is_down(self) -> bool:
        """Check if tonearm is down.
        
        Hall effect sensor returns LOW when magnet is near.
        
        Returns:
            bool: True if tonearm is down
        """
        return not self.GPIO.input(self.hall_pin)
    
    def start_monitoring(self, on_change: Callable[[bool], None]) -> None:
        """Start monitoring tonearm state changes.
        
        Args:
            on_change: Callback function(is_down) called on state change
        """
        import threading
        
        self.monitoring = True
        self._last_state = self.is_down()
        
        def monitor_loop():
            while self.monitoring:
                current_state = self.is_down()
                if current_state != self._last_state:
                    logger.info(f"Tonearm state changed: {'DOWN' if current_state else 'UP'}")
                    self._last_state = current_state
                    on_change(current_state)
                time.sleep(self.poll_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Tonearm monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring tonearm state."""
        self.monitoring = False
        if hasattr(self, '_monitor_thread'):
            self._monitor_thread.join(timeout=1.0)
        logger.info("Tonearm monitoring stopped")


class StubTonearmSensor(TonearmSensor):
    """Stub tonearm sensor for development/testing."""
    
    def __init__(self, poll_interval_ms: int = 50):
        """Initialize stub tonearm sensor.
        
        Args:
            poll_interval_ms: Polling interval in milliseconds
        """
        self.state_down = False
        self.poll_interval = poll_interval_ms / 1000.0
        self.monitoring = False
        logger.info("Stub tonearm sensor initialized (use keyboard to toggle)")
    
    def is_down(self) -> bool:
        """Check if tonearm is down.
        
        Returns:
            bool: True if tonearm is down
        """
        return self.state_down
    
    def toggle(self) -> None:
        """Toggle tonearm state (for keyboard simulation)."""
        self.state_down = not self.state_down
        logger.info(f"[STUB] Tonearm toggled: {'DOWN' if self.state_down else 'UP'}")
    
    def start_monitoring(self, on_change: Callable[[bool], None]) -> None:
        """Start monitoring tonearm state changes.
        
        Args:
            on_change: Callback function(is_down) called on state change
        """
        import threading
        
        self.monitoring = True
        self._last_state = self.state_down
        self._on_change = on_change
        
        def monitor_loop():
            while self.monitoring:
                if self.state_down != self._last_state:
                    self._last_state = self.state_down
                    on_change(self.state_down)
                time.sleep(self.poll_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("[STUB] Tonearm monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring tonearm state."""
        self.monitoring = False
        if hasattr(self, '_monitor_thread'):
            self._monitor_thread.join(timeout=1.0)
        logger.info("[STUB] Tonearm monitoring stopped")


def create_tonearm_sensor(config: dict) -> TonearmSensor:
    """Factory function to create appropriate tonearm sensor.
    
    Args:
        config: Application configuration
        
    Returns:
        TonearmSensor: Real or stub sensor based on platform
    """
    tonearm_config = config['tonearm']
    poll_interval = tonearm_config.get('poll_interval_ms', 50)
    
    if Platform.is_raspberry_pi() and not Platform.is_dev_mode(config):
        hall_pin = tonearm_config['hall_pin']
        return RealTonearmSensor(hall_pin, poll_interval)
    else:
        return StubTonearmSensor(poll_interval)
