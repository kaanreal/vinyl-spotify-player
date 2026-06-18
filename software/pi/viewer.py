#!/usr/bin/env python3
"""Jukebox — pygame/SDL2 vinyl record viewer. Hardware-accelerated, lightweight."""

import json
import logging
import os
import signal
import threading
import time
from io import BytesIO
from urllib.request import Request, urlopen

import pygame

logging.basicConfig(
    filename='/tmp/jukebox-viewer.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
log = logging.getLogger('viewer')

UI_PORT = os.environ.get('UI_PORT', '8080')
BASE = f'http://localhost:{UI_PORT}'
GROOVE_COUNT = 42
LABEL_RATIO = 0.22
SPIN_DEG_PER_MS = 360.0 / 12_000.0

state = {
    'active': False,
    'paused': True,
    'art_url': '',
    'art_mtime': 0.0,
    'art_surf': None,
    'angle': 0.0,
    'spinning': False,
}
_state_lock = threading.Lock()

_pending_art_url = None
_art_ready = threading.Event()
_toggle_pending = False
_toggle_target_paused = True
_toggle_ts = 0.0
_TOGGLE_TIMEOUT = 6.0

# ── Network helpers ──────────────────────────────────────────────────────────

def fetch(path):
    try:
        return urlopen(Request(f'{BASE}{path}', headers={'Cache-Control': 'no-cache'}), timeout=2).read()
    except Exception:
        return None

def load_status():
    data = fetch('/status')
    if data is None:
        return
    try:
        return json.loads(data)
    except (json.JSONDecodeError, ValueError):
        return None

def load_art():
    data = fetch('/art')
    if data is None:
        return None
    try:
        buf = BytesIO(data)
        img = pygame.image.load(buf)
        if img.get_width() <= 2 and img.get_height() <= 2:
            return None
        return img.convert_alpha()
    except Exception:
        return None

# ── Recording compositing ────────────────────────────────────────────────────

def make_grooves(size):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((20, 20, 20))
    cx = cy = size // 2
    max_r = size // 2 - 1
    for i in range(GROOVE_COUNT):
        r = int(max_r - (max_r * (1 - LABEL_RATIO) * i / GROOVE_COUNT))
        if r < 2:
            break
        alpha = max(8, int(20 * (1 - i / GROOVE_COUNT)))
        pygame.draw.circle(surf, (0, 0, 0, alpha), (cx, cy), r, 1)
    lr = int(max_r * LABEL_RATIO)
    pygame.draw.circle(surf, (0, 0, 0, 12), (cx, cy), lr, 1)
    return surf

def make_record(art_surf, grooves, size):
    record = grooves.copy()
    if art_surf:
        s = size / max(art_surf.get_width(), art_surf.get_height())
        if abs(s - 1.0) > 0.01:
            art = pygame.transform.smoothscale(art_surf, (int(art_surf.get_width() * s), int(art_surf.get_height() * s)))
        else:
            art = art_surf
        if art.get_width() != size or art.get_height() != size:
            ps = pygame.Surface((size, size), pygame.SRCALPHA)
            ps.blit(art, ((size - art.get_width()) // 2, (size - art.get_height()) // 2))
            art = ps
        record.blit(art, (0, 0))
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
    record.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
    return record

def make_spindle(size):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    r = max(2, int(size * 0.04))
    pygame.draw.circle(s, (30, 30, 30, 255), (size // 2, size // 2), r)
    return s

# ── Background threads ───────────────────────────────────────────────────────

def poll_loop():
    global _pending_art_url, _toggle_pending, _toggle_target_paused
    while True:
        s = load_status()
        if s:
            with _state_lock:
                prev_active = state['active']
                prev_paused = state['paused']

                state['active'] = s.get('active', False)
                server_paused = s.get('paused', True)

                if _toggle_pending:
                    if server_paused == _toggle_target_paused:
                        _toggle_pending = False
                        state['paused'] = server_paused
                        state['spinning'] = state['active'] and not server_paused
                    elif time.time() - _toggle_ts > _TOGGLE_TIMEOUT:
                        _toggle_pending = False
                        state['paused'] = server_paused
                        state['spinning'] = state['active'] and not server_paused
                else:
                    state['paused'] = server_paused
                    state['spinning'] = state['active'] and not server_paused

                if state['active']:
                    new_mtime = s.get('art_mtime', 0)
                    if new_mtime and new_mtime != state.get('art_mtime', 0):
                        state['art_mtime'] = new_mtime
                        state['art_url'] = s.get('art_url', '')
                        _pending_art_url = s.get('art_url', '')
                        _art_ready.set()
                else:
                    state['art_url'] = ''
                    state['art_mtime'] = 0.0
                    state['art_surf'] = None
                    state['angle'] = 0.0
        time.sleep(0.4)

def art_loader_loop():
    global _pending_art_url
    while True:
        _art_ready.wait()
        url = None
        with _state_lock:
            url = _pending_art_url
            _pending_art_url = None
        if url:
            surf = load_art()
            if surf:
                with _state_lock:
                    state['art_surf'] = surf
        _art_ready.clear()

# ── SSE listener ─────────────────────────────────────────────────────────────

def sse_listener():
    """Connect to /events and push state updates immediately."""
    import http.client
    while True:
        try:
            conn = http.client.HTTPConnection('localhost', port=int(UI_PORT), timeout=30)
            conn.request('GET', '/events')
            resp = conn.getresponse()
            buf = ''
            while True:
                chunk = resp.read(1)
                if not chunk:
                    break
                buf += chunk.decode()
                if buf.endswith('\n\n'):
                    for line in buf.strip().split('\n'):
                        if line.startswith('data: '):
                            payload = line[6:]
                            if payload == 'heartbeat':
                                continue
                            try:
                                data = json.loads(payload)
                                with _state_lock:
                                    prev_active = state['active']
                                    prev_paused = state['paused']
                                    state['active'] = data.get('active', False)
                                    state['paused'] = data.get('paused', True)
                                    state['spinning'] = state['active'] and not state['paused']
                                    new_mtime = data.get('art_mtime', 0)
                                    if new_mtime and new_mtime != state.get('art_mtime', 0):
                                        state['art_mtime'] = new_mtime
                                        global _pending_art_url
                                        _pending_art_url = data.get('art_url', '')
                                        _art_ready.set()
                                    if not state['active']:
                                        state['art_surf'] = None
                                        state['angle'] = 0.0
                            except (json.JSONDecodeError, ValueError):
                                pass
                    buf = ''
            conn.close()
        except Exception as exc:
            log.warning('SSE connection error: %s', exc)
        time.sleep(3)

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    log.info('Starting pygame vinyl viewer')

    os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '0'
    pygame.display.init()
    pygame.mouse.set_visible(False)

    info = pygame.display.Info()
    size = min(info.current_w, info.current_h)
    log.info(f'Display: {info.current_w}x{info.current_h}, viewport: {size}')

    screen = pygame.display.set_mode((size, size), pygame.FULLSCREEN)
    pygame.display.set_caption('Jukebox')

    grooves = make_grooves(size)
    spindle = make_spindle(size)

    threading.Thread(target=poll_loop, daemon=True).start()
    threading.Thread(target=art_loader_loop, daemon=True).start()
    threading.Thread(target=sse_listener, daemon=True).start()

    time.sleep(0.5)

    clock = pygame.time.Clock()
    running = True
    surf_cache = {}
    idle_txt = None

    s0 = load_status()
    if s0:
        with _state_lock:
            state['active'] = s0.get('active', False)
            state['paused'] = s0.get('paused', True)
            state['spinning'] = state['active'] and not state['paused']
            if state['active']:
                url = s0.get('art_url', '')
                if url:
                    state['art_url'] = url
                    state['art_mtime'] = s0.get('art_mtime', 0)
                    art = load_art()
                    if art:
                        state['art_surf'] = art

    log.info('Main loop started')
    frame_count = 0
    while running:
        dt = clock.get_rawtime()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                global _toggle_pending, _toggle_target_paused, _toggle_ts
                with _state_lock:
                    if state['active']:
                        new_paused = not state['paused']
                        state['paused'] = new_paused
                        state['spinning'] = state['active'] and not new_paused
                        _toggle_pending = True
                        _toggle_target_paused = new_paused
                        _toggle_ts = time.time()
                threading.Thread(target=lambda: fetch('/toggle'), daemon=True).start()

        with _state_lock:
            s = dict(state)

        if s['spinning']:
            with _state_lock:
                state['angle'] = (state['angle'] + dt * SPIN_DEG_PER_MS) % 360

        art_surf = s['art_surf']

        try:
            if not s['active']:
                screen.fill((0, 0, 0))
                if idle_txt is None:
                    font = pygame.font.Font(None, int(size * 0.06))
                    idle_txt = font.render('Ready', True, (255, 255, 255, 50))
                if idle_txt:
                    ix = (size - idle_txt.get_width()) // 2
                    iy = (size - idle_txt.get_height()) // 2 - int(size * 0.04) - 8
                    screen.blit(idle_txt, (ix, iy))
            elif art_surf is None:
                screen.fill((0, 0, 0))
                screen.blit(grooves, (0, 0))
            else:
                ck = id(art_surf)
                if ck not in surf_cache:
                    rec = make_record(art_surf, grooves, size)
                    surf_cache[ck] = rec
                rec = surf_cache[ck]
                screen.fill((0, 0, 0))
                if s['spinning'] and s['angle'] != 0:
                    rot = pygame.transform.rotozoom(rec, s['angle'], 1.0)
                    screen.blit(rot, ((size - rot.get_width()) // 2, (size - rot.get_height()) // 2))
                else:
                    screen.blit(rec, (0, 0))

            screen.blit(spindle, (0, 0))
            pygame.display.flip()
        except Exception as e:
            log.exception(f'Render error: {e}')

        frame_count += 1
        if frame_count % 300 == 0:
            log.info('Running: %d frames, active=%s spinning=%s', frame_count, s['active'], s['spinning'])

        target_fps = 30 if s['spinning'] else 10
        clock.tick(target_fps)

    log.info('Main loop exited')
    pygame.quit()


def scale_to(surf, new_size):
    w, h = surf.get_size()
    s = new_size / max(w, h)
    if abs(s - 1.0) > 0.01:
        return pygame.transform.smoothscale(surf, (int(w * s), int(h * s)))
    return surf


if __name__ == '__main__':
    main()
