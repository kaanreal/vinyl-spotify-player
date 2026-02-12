# Hardware Wiring Guide

This guide shows how to connect all hardware components to the Raspberry Pi Zero 2 W.

## GPIO Pin Reference

| Component                | Connection         | GPIO Pin        | Physical Pin |
| ------------------------ | ------------------ | --------------- | ------------ |
| **Hall Effect Sensor**   | Signal             | GPIO 17         | Pin 11       |
|                          | VCC                | 3.3V            | Pin 1        |
|                          | GND                | Ground          | Pin 6        |
| **Rotary Encoder**       | CLK                | GPIO 5          | Pin 29       |
|                          | DT                 | GPIO 6          | Pin 31       |
|                          | VCC                | 3.3V            | Pin 17       |
|                          | GND                | Ground          | Pin 20       |
| **Motor Driver (L298N)** | PWM                | GPIO 18         | Pin 12       |
|                          | DIR                | GPIO 23         | Pin 16       |
|                          | ENABLE             | GPIO 24         | Pin 18       |
|                          | Motor +/-          | Motor terminals |
|                          | VCC                | 5-12V external  |
|                          | GND                | Ground (shared) | Pin 14       |
| **2.8" Display**         | See display manual | SPI + Touch     |
|                          | Varies by model    | Multiple pins   |

## Component Details

### 1. Hall Effect Sensor (A3144 or similar)

**Purpose:** Detects tonearm position via magnet

```
Hall Sensor    Raspberry Pi
-----------    -------------
VCC      -->   3.3V (Pin 1)
GND      -->   Ground (Pin 6)
OUT      -->   GPIO 17 (Pin 11)
```

**Setup:**

- Mount sensor near tonearm rest position
- Attach small neodymium magnet to tonearm
- When tonearm is down (playing), magnet should be near sensor
- Sensor output goes LOW when magnet is detected

**Configuration:**

- Internal pull-up resistor enabled in software
- Active LOW (sensor pulls to ground when magnet present)

### 2. Rotary Encoder (KY-040 or similar)

**Purpose:** Volume control knob

```
Encoder        Raspberry Pi
-----------    -------------
CLK      -->   GPIO 5 (Pin 29)
DT       -->   GPIO 6 (Pin 31)
SW       -->   Not used (optional)
+        -->   3.3V (Pin 17)
GND      -->   Ground (Pin 20)
```

**Setup:**

- Encoder generates pulses when rotated
- CLK and DT signals determine rotation direction
- Software uses internal pull-up resistors
- No external resistors needed for basic operation

**Notes:**

- Do NOT connect encoder to 5V - use 3.3V only
- If encoder has built-in pull-ups for 5V, you may need to disable them or use level shifters

### 3. Motor Driver (L298N Module)

**Purpose:** Controls DC gear motor for turntable spinning

```
L298N Driver   Raspberry Pi / External
-----------    -----------------------
IN1 (PWM) -->  GPIO 18 (Pin 12)
IN2 (DIR) -->  GPIO 23 (Pin 16)
ENA       -->  GPIO 24 (Pin 18)
VCC       -->  5-12V external power supply
GND       -->  Ground (Pin 14 + external GND)
OUT1/OUT2 -->  DC Motor terminals
```

**Power Requirements:**

- L298N requires 5-12V for motor power (NOT from Pi!)
- Use external power supply (e.g., 9V/12V adapter)
- **Important:** Connect external GND to Pi GND for common ground
- Do NOT power motor from Pi's 5V - insufficient current

**Motor Specifications:**

- DC gear motor, 6-12V
- Target speed: ~33 RPM (adjustable via PWM)
- Gearbox ratio determines final RPM (e.g., 1:100 gearbox)

**Wiring Safety:**

- Use thick wires for motor power (at least 22 AWG)
- Add a flyback diode across motor terminals (optional, L298N usually has internal protection)
- Keep motor wires away from signal wires to reduce noise

### 4. Display (2.8" Round 480x480 Touch Display)

**Common Models:**

- Waveshare 2.8inch Touch Display (Round)
- Generic ST7789 / GC9A01 based displays

**Connection:**
Display typically uses SPI for screen and I2C/SPI for touch:

```
Typical SPI Display Pinout:
- VCC: 3.3V or 5V (check datasheet)
- GND: Ground
- DIN (MOSI): GPIO 10 (SPI0 MOSI)
- CLK (SCLK): GPIO 11 (SPI0 SCLK)
- CS: GPIO 8 (SPI0 CE0) or custom
- DC: GPIO 25 (or custom)
- RST: GPIO 27 (or custom)
- BL (Backlight): 3.3V or PWM

Touch Controller (varies):
- INT: GPIO 24 (or custom)
- Follow manufacturer wiring guide
```

**Important:**

- Follow your specific display's wiring diagram
- Some displays require software configuration (dtoverlay in /boot/config.txt)
- Install manufacturer's kernel modules if needed
- For pygame/SDL, framebuffer configuration may be required

**Configuration:**

- Enable SPI: `sudo raspi-config` → Interface Options → SPI → Enable
- May need to add dtoverlay to `/boot/config.txt` (check display docs)

## Wiring Tips

1. **Use color-coded wires:**
    - Red: Power (3.3V or external +)
    - Black: Ground
    - Yellow/Green: Signal lines

2. **Common Ground:**
    - All components must share a common ground with the Pi
    - External power supplies must have GND connected to Pi GND

3. **Cable Management:**
    - Keep signal wires short
    - Twist encoder and sensor signal wires with ground to reduce noise
    - Route motor power wires away from signal lines

4. **Testing:**
    - Test each component individually before final assembly
    - Use a multimeter to verify connections
    - Check for shorts before powering on

5. **Soldering:**
    - Solder connections for permanent installation
    - Use header pins for easy disconnection during development
    - Heat shrink tubing for exposed wire connections

## Power Considerations

- **Raspberry Pi:** 5V/2.5A minimum (use official adapter)
- **Display:** Check datasheet (typically 3.3V or 5V at 100-200mA)
- **Motor:** External power supply (e.g., 9V/12V at 1-2A depending on motor)
- **Sensors & Encoder:** Draw minimal current from 3.3V rail (<10mA total)

**Total System Power:**

- Pi + Display: ~5V/3A recommended
- Motor: Separate 9-12V supply based on motor specs

## Safety Checklist

- [ ] Double-check all GPIO pin numbers before connecting
- [ ] Verify power supply voltages (3.3V vs 5V vs external)
- [ ] Ensure common ground between all power supplies
- [ ] No shorts between power and ground
- [ ] Motor power NOT connected to Pi's 5V rail
- [ ] All connections secure and insulated
- [ ] Power off before making wiring changes

## Next Steps

After wiring, proceed to [assembly.md](assembly.md) for physical integration into the vinyl player housing.
