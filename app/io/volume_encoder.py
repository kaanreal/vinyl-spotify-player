"""Rotary encoder for volume control."""

import time
from abc import ABC, abstractmethod
from typing import Callable
from app.io.platform import Platform
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class VolumeEncoder(ABC):
    """Abstract base class for volume encoder."""
    
    @abstractmethod
    def start_monitoring(self, on_volume_change: Callable[[int], None]) -> None:
        """Start monitoring encoder rotation.
        
        Args:
            on_volume_change: Callback function(delta) called on rotation
                             delta is positive for clockwise, negative for counter-clockwise
        """
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop monitoring encoder."""
        pass


class RealVolumeEncoder(VolumeEncoder):
    """Real volume encoder using GPIO rotary encoder."""
    
    def __init__(self, clk_pin: int, dt_pin: int, volume_step: int = 5):
        """Initialize real volume encoder.
        
        Args:
            clk_pin: GPIO pin for CLK signal
            dt_pin: GPIO pin for DT signal
            volume_step: Volume change per click
        """
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
        except ImportError:
            raise RuntimeError("RPi.GPIO not available - use StubVolumeEncoder instead")
        
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.volume_step = volume_step
        self.monitoring = False
        
        # Set up GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.clk_pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        self.GPIO.setup(self.dt_pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        
        self._last_clk = self.GPIO.input(self.clk_pin)
        
        logger.info(f"Real volume encoder initialized on GPIO {clk_pin}/{dt_pin}")
    
    def start_monitoring(self, on_volume_change: Callable[[int], None]) -> None:
        """Start monitoring encoder rotation.
        
        Args:
            on_volume_change: Callback function(delta) called on rotation
        """
        import threading
        
        self.monitoring = True
        
        def monitor_loop():
            last_clk = self._last_clk
            
            while self.monitoring:
                clk = self.GPIO.input(self.clk_pin)
                dt = self.GPIO.input(self.dt_pin)
                
                if clk != last_clk:
                    if dt != clk:
                        # Clockwise
                        delta = self.volume_step
                        logger.debug(f"Encoder: +{delta}")
                    else:
                        # Counter-clockwise
                        delta = -self.volume_step
                        logger.debug(f"Encoder: {delta}")
                    
                    on_volume_change(delta)
                    last_clk = clk
                
                time.sleep(0.001)  # 1ms polling
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Volume encoder monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring encoder."""
        self.monitoring = False
        if hasattr(self, '_monitor_thread'):
            self._monitor_thread.join(timeout=1.0)
        logger.info("Volume encoder monitoring stopped")


class StubVolumeEncoder(VolumeEncoder):
    """Stub volume encoder for development/testing."""
    
    def __init__(self, volume_step: int = 5):
        """Initialize stub volume encoder.
        
        Args:
            volume_step: Volume change per simulated click
        """
        self.volume_step = volume_step
        self.monitoring = False
        self._on_volume_change = None
        logger.info("Stub volume encoder initialized (use up/down keys)")
    
    def simulate_rotation(self, direction: int) -> None:
        """Simulate encoder rotation.
        
        Args:
            direction: 1 for clockwise (volume up), -1 for counter-clockwise (volume down)
        """
        if self._on_volume_change:
            delta = self.volume_step * direction
            logger.info(f"[STUB] Volume encoder: {'+' if delta > 0 else ''}{delta}")
            self._on_volume_change(delta)
    
    def start_monitoring(self, on_volume_change: Callable[[int], None]) -> None:
        """Start monitoring encoder rotation.
        
        Args:
            on_volume_change: Callback function(delta) called on rotation
        """
        self.monitoring = True
        self._on_volume_change = on_volume_change
        logger.info("[STUB] Volume encoder monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring encoder."""
        self.monitoring = False
        self._on_volume_change = None
        logger.info("[STUB] Volume encoder monitoring stopped")


def create_volume_encoder(config: dict) -> VolumeEncoder:
    """Factory function to create appropriate volume encoder.
    
    Args:
        config: Application configuration
        
    Returns:
        VolumeEncoder: Real or stub encoder based on platform
    """
    encoder_config = config['encoder']
    volume_step = encoder_config.get('volume_step', 5)
    
    if Platform.is_raspberry_pi() and not Platform.is_dev_mode(config):
        clk_pin = encoder_config['clk_pin']
        dt_pin = encoder_config['dt_pin']
        return RealVolumeEncoder(clk_pin, dt_pin, volume_step)
    else:
        return StubVolumeEncoder(volume_step)
