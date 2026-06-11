# Kaan – Development Documentation

## Role

Project Lead

Responsibilities:

- Initial project idea
- Project planning
- Hardware research
- Component sourcing
- GitHub repository management
- Software testing
- Raspberry Pi setup
- 3D enclosure design
- Final integration

---

## Personal Contribution

The project started when I came across a similar concept online.

Instead of recreating the original design, I wanted to build a completely different version with our own design, hardware choices, and software implementation.

I developed the initial project concept and created the first project plan.

After defining the requirements, I:

- Created the GitHub repository
- Researched suitable hardware
- Ordered all project components
- Planned the system architecture
- Designed the enclosure in Onshape
- Tested multiple software approaches
- Integrated hardware and software

---

## Development Timeline

### Week 1
14 April 2026

- Project idea created
- Initial research
- Team discussion
- Feature planning

### Week 2

- Hardware research
- Component selection
- Cost estimation
- Ordering process started

### Week 3

- GitHub repository created
- Development environment prepared
- Raspberry Pi testing started

### Week 4

- First enclosure concepts in Onshape
- Mechanical layout planning
- Component placement design

### Week 5

- First software prototype
- Raspotify implementation
- Spotify testing

### Week 6

- Display shipment delayed
- Alternative solutions evaluated
- Continued software development

### Week 7

- Display reordered
- Additional hardware testing
- System architecture improvements

### Week 8

- Enclosure redesign
- Preparation for final assembly
- Documentation updates

### Week 9

- Hardware integration
- Touchscreen testing
- Audio system testing

### Week 10

- Final debugging
- GitHub documentation
- Presentation preparation

---

## Useful Commits

Key commits I made to this repository (excluding documentation-only changes):

| Commit | Description |
|--------|-------------|
| [`c018dc2`](https://github.com/kaanreal/vinyl-spotify-player/commit/c018dc2) | **Add web UI, Spotify integration & token refresher** — Introduced the first functional web frontend (`index.html`, `style.css`, `script.js`, `spotify.js`, `update.js`), Spotify control flow, OAuth token refresh via `refresh.py`, startup scripts (`start.sh`, `start.bat`), and a static HTTP server setup. This was the foundation for all Spotify playback. |
| [`fed0709`](https://github.com/kaanreal/vinyl-spotify-player/commit/fed0709) | **Add vinyl UI, touch swipe, and playback sync** — Added a vinyl-style player UI with swipe gestures (next/previous/pause), vinyl rotation animation, improved Spotify response handling (`parseJsonSafe`, `checkisPlaying`), album art on vinyl label, and periodic playback state polling. |
| [`574dd75`](https://github.com/kaanreal/vinyl-spotify-player/commit/574dd75) | **Refactor UI to round-screen, remove touch handler** — Replaced the vinyl-style markup with a simpler round-screen layout matching the circular 2.8" hardware display. Removed `handle_touch.js`, adjusted CSS for round-screen styling, reset rotation after track changes, and cleaned up logging. |
| [`878c5db`](https://github.com/kaanreal/vinyl-spotify-player/commit/878c5db) | Rename 3D model STL for clarity |
| [`0b2fb53`](https://github.com/kaanreal/vinyl-spotify-player/commit/0b2fb53) | README update with full Bill of Materials |
| [`f575cb3`](https://github.com/kaanreal/vinyl-spotify-player/commit/f575cb3) | Initial detailed project README |

---

## Lessons Learned

This project taught me:

- Hardware planning
- Raspberry Pi development
- GitHub project management
- 3D CAD design with Onshape
- Electronics integration
- Troubleshooting complex systems
- Managing deadlines and logistics

---

## Reflection

The most challenging part was coordinating hardware delivery times with a limited project schedule.

Despite several delays, the team successfully developed a functional prototype and gained valuable experience in software development, electronics, mechanical design, and project management.

The project represents a complete end-to-end product development process, from idea to prototype.
