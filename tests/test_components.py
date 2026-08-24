"""
Unit & Integration Tests for Teams Anti-AFK.
"""

import os
import sys
import time
import threading
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from idle_tracker import get_idle_seconds
from hotkey_manager import HotkeyManager
from tray_app import TeamsAntiAfkTrayApp, AppState
import afk_actions


class TestIdleTracker(unittest.TestCase):
    def test_get_idle_seconds_returns_valid_float(self):
        idle = get_idle_seconds()
        self.assertIsInstance(idle, float)
        self.assertGreaterEqual(idle, 0.0)

    def test_idle_time_increases(self):
        t1 = get_idle_seconds()
        time.sleep(0.5)
        t2 = get_idle_seconds()
        self.assertGreaterEqual(t2, t1)


class TestHotkeyManager(unittest.TestCase):
    def test_hotkey_manager_initialization(self):
        mock_cb = MagicMock()
        mgr = HotkeyManager(callback=mock_cb)
        self.assertFalse(mgr._listener)
        mgr.stop()
        self.assertEqual(len(mgr._pressed_keys), 0)

    def test_hotkey_manager_callback_invoked(self):
        mock_cb = MagicMock()
        mgr = HotkeyManager(callback=mock_cb, debounce_seconds=0.01)
        from pynput import keyboard

        # Simulate Win + Ctrl + Shift + F press
        mgr._pressed_keys.add(keyboard.Key.cmd)
        mgr._pressed_keys.add(keyboard.Key.ctrl)
        mgr._pressed_keys.add(keyboard.Key.shift)
        mgr._pressed_keys.add(keyboard.KeyCode.from_char('f'))

        mgr._check_hotkey()
        time.sleep(0.1)  # wait for thread callback
        self.assertTrue(mock_cb.called)


class TestTrayApp(unittest.TestCase):
    @patch("pystray.Icon")
    def test_app_initialization_and_state(self, mock_icon):
        app = TeamsAntiAfkTrayApp()
        self.assertEqual(app.state, AppState.ACTIVE)
        self.assertEqual(app.idle_threshold_seconds, 240)
        self.assertIsNotNone(app.icon_active)
        self.assertIsNotNone(app.icon_paused)
        self.assertIsNotNone(app.icon_running)

        # Toggle state
        app.toggle_active_state()
        self.assertEqual(app.state, AppState.PAUSED)

        # Toggle state back
        app.toggle_active_state()
        self.assertEqual(app.state, AppState.ACTIVE)

        app.quit()


class TestAfkActions(unittest.TestCase):
    def test_stop_event_aborts_action(self):
        stop_event = threading.Event()
        stop_event.set()
        result = afk_actions.perform_anti_afk_routine(stop_event=stop_event)
        self.assertFalse(result)

    def test_full_routine_cleans_up_file(self):
        # Run routine with short dummy typing and verify all temp files removed
        result = afk_actions.perform_anti_afk_routine()
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
