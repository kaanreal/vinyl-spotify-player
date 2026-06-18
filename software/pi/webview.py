#!/usr/bin/env python3
"""Jukebox — lightweight WebKit fullscreen viewer for the round display."""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
from gi.repository import Gtk, WebKit2, GLib
import os
import signal
import sys
import logging

logging.basicConfig(
    filename='/tmp/jukebox-webview.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)
log = logging.getLogger('webview')

UI_PORT = os.environ.get('UI_PORT', '8080')
URL = f'http://localhost:{UI_PORT}'

class JukeboxWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        log.info('Creating window')
        self.set_title('Jukebox')
        self.set_decorated(False)
        self.fullscreen()
        self.connect('destroy', Gtk.main_quit)
        self.connect('realize', self.on_realize)

        log.info('Creating WebView')
        webview = WebKit2.WebView()
        settings = webview.get_settings()
        settings.set_enable_media(True)
        settings.set_allow_universal_access_from_file_urls(True)
        webview.connect('load-changed', self.on_load_changed)
        webview.load_uri(URL)
        self.add(webview)
        self.show_all()
        log.info('Window shown')

    def on_realize(self, widget):
        log.info('Window realized (mapped to display)')

    def on_load_changed(self, webview, load_event):
        if load_event == WebKit2.LoadEvent.FINISHED:
            log.info('Page loaded successfully')
        elif load_event == WebKit2.LoadEvent.STARTED:
            log.info('Page load started')
        elif load_event == WebKit2.LoadEvent.COMMITTED:
            log.info('Page load committed')

    def run(self):
        log.info('Starting GTK main loop')
        Gtk.main()
        log.info('GTK main loop exited')

if __name__ == '__main__':
    log.info(f'Starting Jukebox WebView, URL={URL}')
    log.info(f'DISPLAY={os.environ.get("DISPLAY")}')
    log.info(f'WAYLAND_DISPLAY={os.environ.get("WAYLAND_DISPLAY")}')
    log.info(f'GDK_BACKEND={os.environ.get("GDK_BACKEND")}')
    log.info(f'XDG_RUNTIME_DIR={os.environ.get("XDG_RUNTIME_DIR")}')
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        win = JukeboxWindow()
        win.run()
    except Exception as e:
        log.exception('Unhandled exception')
        raise
