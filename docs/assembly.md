# Assembly Guide

This guide covers the physical assembly and integration of components into the Vinyl Spotify Player.

## Overview

The Vinyl Spotify Player combines electronic components with a physical vinyl-style interface. This guide assumes you've completed the [wiring](wiring.md) and are ready for physical assembly.

## Materials Needed

### Electronic Components

- Raspberry Pi Zero 2 W (wired per wiring.md)
- 2.8" round 480x480 touch display
- Hall effect sensor
- Rotary encoder with knob
- DC gear motor + driver
- Power supplies

### Mechanical Components

- Vinyl record or circular disc (for display mount)
- Tonearm (salvaged from old turntable, or 3D printed)
- Small neodymium magnet (5-10mm diameter)
- Turntable platter or circular rotating platform
- Motor mount bracket
- Drive belt or friction wheel (to connect motor to platter)
- Enclosure/case (wood, 3D printed, or acrylic)

### Hardware & Tools

- M2.5 or M3 screws and standoffs for Pi mounting
- Double-sided adhesive tape or mounting putty
- Hot glue gun
- Drill with bits
- Screwdriver set
- Wire management clips/ties

## Assembly Steps

### 1. Prepare the Enclosure

**Option A: Custom Wooden Box**

1. Cut or purchase a wooden box approximately 200mm x 200mm x 80mm
2. Drill hole in top for display (circular cutout matching display size)
3. Drill holes for:
    - Tonearm pivot point
    - Encoder knob
    - Power cable entry
    - Ventilation

**Option B: 3D Printed Case**

1. Design or download a case model
2. Ensure mounting points for:
    - Display
    - Pi Zero
    - Motor
    - Encoder
    - Tonearm

**Option C: Acrylic Layers**

1. Laser-cut multiple acrylic sheets
2. Stack and secure with standoffs
3. Top layer has display cutout
4. Bottom layer holds Pi and motor

### 2. Mount the Display

1. **Test fit** the display in the top panel cutout
2. **Secure display** using:
    - Hot glue around edges (be careful not to cover screen)
    - Small screws if display has mounting holes
    - 3D printed retention ring/bezel
3. **Route display cables** to where Pi will be mounted
4. **Optional:** Add a clear acrylic circle over display if using actual vinyl record around it

### 3. Install the Tonearm

1. **Position tonearm** so it can swing from rest position to "playing" position over display
2. **Mount pivot point** using:
    - Small bearing or simple screw pivot
    - Ensure smooth swing motion
3. **Attach hall sensor** near tonearm rest position:
    - Mount sensor with hot glue or bracket
    - Sensor should be 1-5mm from magnet when tonearm is at rest (UP position)
4. **Attach magnet to tonearm**:
    - Use hot glue to fix small magnet to tonearm
    - Position so magnet is NOT near sensor when tonearm is down (playing position)

**Hall Sensor Logic:**

- Tonearm UP (resting): Magnet NEAR sensor → Play
- Tonearm DOWN (over record): Magnet FAR from sensor → Pause

**Note:** You may need to experiment with magnet/sensor positioning. The logic can be inverted in software if needed.

### 4. Install Rotary Encoder

1. **Drill hole** in enclosure side or top for encoder shaft
2. **Mount encoder** from inside:
    - Use encoder's threaded nut to secure
    - Ensure encoder is stable and doesn't rotate with knob
3. **Attach knob** to encoder shaft
4. **Route wires** to Pi mounting area

### 5. Mount the Motor & Turntable

**Motor Setup:**

1. **Create motor mount** (wood block, 3D printed bracket, or metal L-bracket)
2. **Position motor** so its shaft can drive the platter
3. **Secure motor** with screws or hot glue

**Turntable Platter:**

1. **Create or adapt platter:**
    - Old vinyl record
    - 3D printed disc
    - Lazy Susan bearing with circular platform
2. **Mount platter** on bearing or simple pivot
3. **Connect motor to platter** using:
    - **Option A:** Rubber belt around motor shaft and platter edge
    - **Option B:** Friction wheel on motor shaft touching platter edge
    - **Option C:** Direct drive (if motor shaft extends through platter)

**Alignment:**

- Motor speed ~33 RPM can be achieved with:
    - PWM control (software adjustable)
    - Appropriate gear ratio
    - Drive wheel diameter ratio
- Fine-tune in software (`motor.target_rpm` in config.json)

### 6. Mount the Raspberry Pi

1. **Position Pi** inside enclosure:
    - Near display for short cables
    - Access to SD card slot
    - Good ventilation
2. **Secure Pi** using:
    - Standoffs and screws
    - Adhesive standoffs
    - 3D printed mounting bracket
3. **Connect all wired components:**
    - Display
    - Hall sensor
    - Encoder
    - Motor driver
4. **Double-check all connections** against wiring diagram

### 7. Wire Management

1. **Bundle wires** with zip ties or clips
2. **Route wires neatly** away from moving parts (tonearm, platter)
3. **Secure wires** to prevent strain on connections
4. **Label wires** for easier troubleshooting

### 8. Power Supply Integration

1. **Mount motor power supply** inside or outside enclosure
2. **Run power cables** through enclosure entry holes
3. **Use cable glands or grommets** to protect wires at entry points
4. **Optional:** Add power switch on enclosure for easy on/off

### 9. Final Assembly

1. **Close enclosure** (if multi-part)
2. **Secure all panels** with screws
3. **Add rubber feet** to bottom for stability
4. **Optional aesthetic touches:**
    - Paint or stain wood
    - Vinyl wrap
    - Label components
    - Add LED indicators

## Testing Checklist

Before final assembly:

- [ ] Display powers on and shows image
- [ ] Touch input responds to taps
- [ ] Tonearm motion triggers hall sensor (check logs)
- [ ] Encoder rotation detected (check logs)
- [ ] Motor spins when commanded
- [ ] Motor direction correct
- [ ] No loose wires or connections
- [ ] All screws tightened
- [ ] Enclosure closes properly

## Post-Assembly Configuration

1. **Calibrate motor speed:**
    - Run app and check if rotation speed feels right
    - Adjust `motor.target_rpm` in config.json if needed
    - Use phone stopwatch to measure actual RPM

2. **Test tonearm sensitivity:**
    - Lift and lower tonearm
    - Check if play/pause triggers correctly
    - Adjust magnet/sensor distance if needed

3. **Verify all controls:**
    - Touch tap → play/pause
    - Touch swipe → next/prev
    - Encoder → volume
    - Tonearm → play/pause + motor

## Troubleshooting Assembly

| Issue                          | Solution                                           |
| ------------------------------ | -------------------------------------------------- |
| Tonearm doesn't trigger sensor | Adjust magnet/sensor distance; check wiring        |
| Motor doesn't spin             | Check motor driver wiring; verify external power   |
| Encoder doesn't respond        | Check CLK/DT wiring; ensure 3.3V not 5V            |
| Display not working            | Verify SPI enabled; check display power and wiring |
| Motor too fast/slow            | Adjust PWM duty cycle or gear ratio                |
| Platter wobbles                | Check bearing alignment; balance weight            |

## Enhancements

- **Add weight to platter** for realistic inertia
- **Vinyl record decoration** around display
- **LED backlight** under platter
- **Action figure tonearm** for fun aesthetic
- **Album art printout** under clear acrylic platter
- **Classic wood finish** for vintage look

## Safety

- **No exposed live wires** - use heat shrink or electrical tape
- **Secure all moving parts** - ensure tonearm and platter can't catch wires
- **Ventilation** - Pi and motor driver need airflow
- **Stable base** - device should not tip over easily

## Next Steps

Once assembled, proceed to [troubleshooting.md](troubleshooting.md) if you encounter any issues, or see the main [README.md](../README.md) for usage instructions.

---

**Enjoy building your Vinyl Spotify Player!** 🎵🔧
