# Wiring Draft

> This is a safe starter mapping. Validate pinout against your exact board/display revision before soldering.

## Power

- 12V PSU → motor driver + buck converter input
- Buck converter output (5V) → Raspberry Pi 5V/GND
- Common ground required across Pi, sensors, and motor driver

## Suggested GPIO Mapping (Pi Zero 2 W)

- Hall sensor data → `GPIO17` (input, pull-up)
- Encoder A → `GPIO22`
- Encoder B → `GPIO23`
- Encoder button (optional) → `GPIO27`
- Motor enable/PWM (via driver transistor/controller) → `GPIO18` (PWM)
- Motor direction (optional) → `GPIO24`

## Audio

- USB sound card connected to Pi USB
- Sound card output → PAM8403 input
- PAM8403 output → left/right speakers

## Safety Notes

- Do not power motor directly from Pi GPIO.
- Use flyback protection / proper motor driver module.
- Validate current draw and thermals during continuous spin.
- Add inline fuse on 12V rail where possible.
