# 🎵 Vinyl Spotify Player

> A custom-built Spotify player designed to look and behave like a classic turntable. A real vinyl record rotates around a fixed circular display that shows the current album artwork. Playback is controlled using a mechanical tonearm, similar to a real record player.

---

## Overview

The Vinyl Spotify Player was developed as a school technology project.

While researching ideas, we discovered a similar concept on social media. Instead of recreating the original design, we decided to completely redesign and reinterpret the concept using our own hardware, software, and mechanical solutions.

The result is a unique Spotify player that combines modern streaming technology with the aesthetics of a traditional record player.

---

## Features

- Spotify music playback
- Circular 2.8" IPS touchscreen display
- Rotating album artwork
- Touchscreen controls
- Custom 3D-printed enclosure
- Automatic playback using a tonearm mechanism
- Optional motorized vinyl rotation system
- Fully documented development process

---

## Hardware

### Main Components

| Component | Purpose |
|------------|------------|
| Raspberry Pi Zero 2 W | Main controller |
| 2.8" Circular IPS Touchscreen | Album artwork display and controls |
| USB Audio Interface | Audio output |
| Audio Amplifier | Speaker amplification |
| Hall Effect Sensor | Tonearm position detection |
| Neodymium Magnet | Trigger for automatic playback |
| JGA25-370 Geared Motor | Optional vinyl rotation |
| Motor Controller | Motor control |
| Bearings | Smooth mechanical movement |
| Rubber Belt | Vinyl drive mechanism |

---

## How It Works

The circular display shows the current Spotify album artwork.

A vinyl record with a center cutout is placed around the display, creating the illusion that the artwork is part of the record itself.

The user can:

- Start and pause music
- Control playback through the touchscreen
- View album artwork
- Interact with the tonearm

When the tonearm is moved into the playback position, a neodymium magnet attached to the arm passes over a Hall Effect sensor located underneath the platter. The system detects this position and automatically starts playback.

The motorized platter system was designed during development but remained optional due to time constraints.

---

## Design & Manufacturing

The entire enclosure was designed from scratch in Onshape.

All parts were:

- Designed by the team
- Prototyped and tested
- 3D printed using Bambu Lab printers available at school

No pre-made enclosure or mechanical design was used.

---

## Software Development

Several software approaches were evaluated during development.

### Prototype 1
A Raspotify-based implementation focused on Spotify Connect functionality.

### Prototype 2
A Kiosk Mode implementation focused on displaying album artwork and touchscreen interaction.

The final system combines lessons learned from both prototypes.

---

## Challenges

During development we encountered several challenges:

- Long shipping times for components
- The original display failed to arrive and had to be reordered
- Limited project timeline
- Integration of hardware and software systems
- Balancing school work with project development

Because of these delays, a significant amount of work was completed outside of school.

---

## Team

### Kaan
Project planning, hardware sourcing, software development, GitHub management, enclosure design, testing and integration.

### Marc
Software development, prototype implementation, testing and troubleshooting.

### Lennard
Mechanical construction, 3D design support, assembly and prototyping.

---

## Documentation

- [Project Documentation](README.md)
- [Kaan's Development Log](docs/kaan.md)
- [Marc's Development Log](docs/marc.md)
- [Lennard's Development Log](docs/lennard.md)

---

## Repository

GitHub Repository:

https://github.com/kaanreal/vinyl-spotify-player

---

## Project Timeline

Project Start:

**14 April 2026**

Project developed during the 2026 school technology project period.

---

## License

This project was created for educational purposes as part of a school technology project.
