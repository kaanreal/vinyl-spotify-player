"""Platform detection for hardware abstraction."""

import platform
import os


class Platform:
    """Platform detection and capabilities."""
    
    _is_pi = None
    _is_dev_mode = None
    
    @classmethod
    def is_raspberry_pi(cls) -> bool:
        """Detect if running on a Raspberry Pi.
        
        Returns:
            bool: True if running on Raspberry Pi
        """
        if cls._is_pi is not None:
            return cls._is_pi
        
        # Check for Raspberry Pi specific files
        if os.path.exists('/proc/device-tree/model'):
            try:
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().lower()
                    cls._is_pi = 'raspberry pi' in model
                    return cls._is_pi
            except:
                pass
        
        # Fallback: check platform
        machine = platform.machine().lower()
        cls._is_pi = machine in ['armv7l', 'aarch64', 'armv6l'] and platform.system() == 'Linux'
        return cls._is_pi
    
    @classmethod
    def is_dev_mode(cls, config: dict = None) -> bool:
        """Check if development mode is enabled.
        
        In dev mode, hardware is simulated with keyboard/mouse.
        
        Args:
            config: Optional configuration dictionary
            
        Returns:
            bool: True if in development mode
        """
        if cls._is_dev_mode is not None:
            return cls._is_dev_mode
        
        # If explicitly set in config, use that
        if config and 'dev_mode' in config:
            cls._is_dev_mode = config['dev_mode'].get('enabled', False)
            return cls._is_dev_mode
        
        # Otherwise, dev mode = not on Pi
        cls._is_dev_mode = not cls.is_raspberry_pi()
        return cls._is_dev_mode
    
    @classmethod
    def get_platform_name(cls) -> str:
        """Get a human-readable platform name.
        
        Returns:
            str: Platform name
        """
        if cls.is_raspberry_pi():
            return "Raspberry Pi"
        return f"{platform.system()} ({platform.machine()})"
