"""GPIO tonearm controller for play/pause functionality."""

import time
from typing import Callable, Optional
import RPi.GPIO as GPIO


class TonearmController:
    """Controls playback based on GPIO tonearm switch state."""

    def __init__(self, gpio_pin: int, on_place: Callable[[], None], on_lift: Callable[[], None]):
        """Initialize the tonearm controller.
        
        Args:
            gpio_pin: GPIO pin number for the tonearm switch.
            on_place: Callback function when tonearm is placed.
            on_lift: Callback function when tonearm is lifted.
        """
        self.gpio_pin = gpio_pin
        self.on_place = on_place
        self.on_lift = on_lift
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Debouncing
        self.last_state: Optional[bool] = None
        self.last_change_time: float = 0
        self.debounce_delay: float = 0.1  # 100ms debounce
        
        # Get initial state
        self._update_state()
    
    def _get_current_state(self) -> bool:
        """Get the current state of the tonearm switch.
        
        Returns:
            True if tonearm is placed (switch closed), False if lifted (switch open).
        """
        # GPIO.LOW means switch is closed (tonearm placed)
        # GPIO.HIGH means switch is open (tonearm lifted)
        return GPIO.input(self.gpio_pin) == GPIO.LOW
    
    def _update_state(self) -> None:
        """Update the state without triggering callbacks."""
        self.last_state = self._get_current_state()
        self.last_change_time = time.time()
    
    def check(self) -> None:
        """Check for state changes and trigger callbacks if needed."""
        current_state = self._get_current_state()
        current_time = time.time()
        
        # Check if state has changed
        if current_state != self.last_state:
            # Check debounce delay
            if current_time - self.last_change_time >= self.debounce_delay:
                # State change confirmed
                if current_state:
                    # Tonearm placed
                    print("Tonearm placed - starting playback")
                    self.on_place()
                else:
                    # Tonearm lifted
                    print("Tonearm lifted - pausing playback")
                    self.on_lift()
                
                self.last_state = current_state
                self.last_change_time = current_time
    
    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        GPIO.cleanup(self.gpio_pin)
