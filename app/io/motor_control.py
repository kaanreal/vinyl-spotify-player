"""Motor control for turntable spinning."""

import time
from abc import ABC, abstractmethod
from typing import Optional
from app.io.platform import Platform
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class MotorController(ABC):
    """Abstract base class for motor controller."""
    
    @abstractmethod
    def start(self) -> None:
        """Start the motor spinning."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the motor."""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if motor is running.
        
        Returns:
            bool: True if motor is running
        """
        pass
    
    @abstractmethod
    def get_rpm(self) -> float:
        """Get current motor RPM.
        
        Returns:
            float: Current RPM
        """
        pass


class RealMotorController(MotorController):
    """Real motor controller using PWM and motor driver."""
    
    def __init__(self, pwm_pin: int, dir_pin: int, enable_pin: int, target_rpm: float = 33.3):
        """Initialize real motor controller.
        
        Args:
            pwm_pin: GPIO pin for PWM speed control
            dir_pin: GPIO pin for direction control
            enable_pin: GPIO pin for motor enable
            target_rpm: Target RPM for the motor
        """
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
        except ImportError:
            raise RuntimeError("RPi.GPIO not available - use StubMotorController instead")
        
        self.pwm_pin = pwm_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.target_rpm = target_rpm
        self.running = False
        
        # Set up GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.pwm_pin, self.GPIO.OUT)
        self.GPIO.setup(self.dir_pin, self.GPIO.OUT)
        self.GPIO.setup(self.enable_pin, self.GPIO.OUT)
        
        # Set direction (clockwise)
        self.GPIO.output(self.dir_pin, self.GPIO.HIGH)
        
        # Set up PWM (1kHz frequency)
        self.pwm = self.GPIO.PWM(self.pwm_pin, 1000)
        self.duty_cycle = 50  # Start at 50% duty cycle
        
        logger.info(f"Real motor controller initialized (target: {target_rpm} RPM)")
    
    def start(self) -> None:
        """Start the motor spinning."""
        if not self.running:
            self.GPIO.output(self.enable_pin, self.GPIO.HIGH)
            self.pwm.start(self.duty_cycle)
            self.running = True
            logger.info(f"Motor started (target: {self.target_rpm} RPM)")
    
    def stop(self) -> None:
        """Stop the motor."""
        if self.running:
            self.pwm.stop()
            self.GPIO.output(self.enable_pin, self.GPIO.LOW)
            self.running = False
            logger.info("Motor stopped")
    
    def is_running(self) -> bool:
        """Check if motor is running.
        
        Returns:
            bool: True if motor is running
        """
        return self.running
    
    def get_rpm(self) -> float:
        """Get current motor RPM.
        
        For a real implementation, this would read from an encoder.
        For now, we assume it matches target when running.
        
        Returns:
            float: Current RPM
        """
        return self.target_rpm if self.running else 0.0
    
    def set_duty_cycle(self, duty: float) -> None:
        """Set PWM duty cycle.
        
        Args:
            duty: Duty cycle (0-100)
        """
        duty = max(0, min(100, duty))
        self.duty_cycle = duty
        if self.running:
            self.pwm.ChangeDutyCycle(duty)


class StubMotorController(MotorController):
    """Stub motor controller for development/testing."""
    
    def __init__(self, target_rpm: float = 33.3):
        """Initialize stub motor controller.
        
        Args:
            target_rpm: Target RPM for simulation
        """
        self.target_rpm = target_rpm
        self.running = False
        self.current_rpm = 0.0
        self._start_time = None
        logger.info(f"Stub motor controller initialized (target: {target_rpm} RPM)")
    
    def start(self) -> None:
        """Start the motor spinning."""
        if not self.running:
            self.running = True
            self._start_time = time.time()
            self.current_rpm = self.target_rpm
            logger.info(f"[STUB] Motor started (simulated {self.target_rpm} RPM)")
    
    def stop(self) -> None:
        """Stop the motor."""
        if self.running:
            self.running = False
            self.current_rpm = 0.0
            self._start_time = None
            logger.info("[STUB] Motor stopped")
    
    def is_running(self) -> bool:
        """Check if motor is running.
        
        Returns:
            bool: True if motor is running
        """
        return self.running
    
    def get_rpm(self) -> float:
        """Get current motor RPM.
        
        Returns:
            float: Current RPM (simulated)
        """
        return self.current_rpm
    
    def get_rotation_angle(self) -> float:
        """Get current rotation angle for animation.
        
        Returns:
            float: Rotation angle in degrees
        """
        if not self.running or self._start_time is None:
            return 0.0
        
        elapsed = time.time() - self._start_time
        # RPM to degrees per second: RPM * 360 / 60
        degrees_per_second = self.target_rpm * 6.0
        angle = (elapsed * degrees_per_second) % 360
        return angle


def create_motor_controller(config: dict) -> MotorController:
    """Factory function to create appropriate motor controller.
    
    Args:
        config: Application configuration
        
    Returns:
        MotorController: Real or stub motor controller based on platform
    """
    motor_config = config['motor']
    target_rpm = motor_config.get('target_rpm', 33.3)
    
    if Platform.is_raspberry_pi() and not Platform.is_dev_mode(config):
        pwm_pin = motor_config['pwm_pin']
        dir_pin = motor_config['dir_pin']
        enable_pin = motor_config['enable_pin']
        return RealMotorController(pwm_pin, dir_pin, enable_pin, target_rpm)
    else:
        return StubMotorController(target_rpm)
