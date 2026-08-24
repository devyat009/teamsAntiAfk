"""
Module: hotkey_manager.py
Manages global hotkeys (e.g. Win + Ctrl + Shift + F) to toggle or stop Anti-AFK.
"""

import time
import threading
from typing import Callable, Optional
from pynput import keyboard


class HotkeyManager:
    """
    Listens for the global shortcut: Win + Ctrl + Shift + F (or Ctrl + Shift + Alt + F fallback).
    Thread-safe and debounced to prevent duplicate activations.
    """

    def __init__(self, callback: Callable[[], None], debounce_seconds: float = 0.5):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self._last_triggered_time = 0.0
        self._pressed_keys = set()
        self._lock = threading.Lock()
        self._listener: Optional[keyboard.Listener] = None

    def start(self):
        """Starts listening for global key combinations in a background thread."""
        if self._listener and self._listener.is_alive():
            return

        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        """Stops the global hotkey listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None
        with self._lock:
            self._pressed_keys.clear()

    def _on_press(self, key):
        with self._lock:
            self._pressed_keys.add(key)
            self._check_hotkey()

    def _on_release(self, key):
        with self._lock:
            self._pressed_keys.discard(key)

    def _check_hotkey(self):
        now = time.time()
        if now - self._last_triggered_time < self.debounce_seconds:
            return

        # Check for Win / Cmd key
        has_win = any(
            k in self._pressed_keys
            for k in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r)
        )

        # Check for Ctrl key
        has_ctrl = any(
            k in self._pressed_keys
            for k in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r)
        )

        # Check for Shift key
        has_shift = any(
            k in self._pressed_keys
            for k in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r)
        )

        # Check for Alt key (optional fallback)
        has_alt = any(
            k in self._pressed_keys
            for k in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr)
        )

        # Check for 'F' or 'f'
        has_f = False
        for k in self._pressed_keys:
            if isinstance(k, keyboard.KeyCode):
                if k.char and k.char.lower() == 'f':
                    has_f = True
                    break
                elif k.vk in (70, 102):  # Virtual key code for 'F'
                    has_f = True
                    break

        # Primary requested hotkey: Win + Ctrl + Shift + F
        # Secondary fallback: Ctrl + Shift + Alt + F
        is_primary = has_win and has_ctrl and has_shift and has_f
        is_fallback = has_ctrl and has_shift and has_alt and has_f

        if is_primary or is_fallback:
            self._last_triggered_time = now
            # Run callback in a separate thread to avoid blocking the keyboard hook
            threading.Thread(target=self.callback, daemon=True).start()


if __name__ == "__main__":
    def on_stop_hotkey():
        print(">>> [HOTKEY TRIGGERED] Win + Ctrl + Shift + F detected! Stopping Anti-AFK.")

    print("Listening for Win + Ctrl + Shift + F (Press Ctrl+C in terminal to exit)...")
    manager = HotkeyManager(callback=on_stop_hotkey)
    manager.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
        print("Stopped hotkey listener.")
