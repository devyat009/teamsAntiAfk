"""
Module: tray_app.py
System Tray Application for Teams Anti-AFK.
Manages the tray icon, state machine, menu options, idle detection loop, and hotkey binding.
"""

import sys
import time
import threading
from typing import Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item, Menu

from idle_tracker import get_idle_seconds
from afk_actions import perform_anti_afk_routine
from hotkey_manager import HotkeyManager


class AppState:
    ACTIVE = "active"
    PAUSED = "paused"
    RUNNING_ACTION = "running_action"


class TeamsAntiAfkTrayApp:
    def __init__(self):
        self.state = AppState.ACTIVE
        self.idle_threshold_seconds = 4 * 60  # Default 4 minutes (240s)
        self.notifications_enabled = True
        self.is_running = True

        self._action_stop_event = threading.Event()
        self._action_thread: Optional[threading.Thread] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Generate icons for different states
        self.icon_active = self._create_icon_image("#107C41", "active")       # Teams green
        self.icon_paused = self._create_icon_image("#D83B01", "paused")       # Alert red/orange
        self.icon_running = self._create_icon_image("#FFB900", "running")     # Warning amber

        # Initialize hotkey manager
        self.hotkey_mgr = HotkeyManager(callback=self.toggle_active_state)

        # Initialize pystray Icon
        self.tray_icon = pystray.Icon(
            name="TeamsAntiAfk",
            icon=self.icon_active,
            title=self._get_tooltip_text(),
            menu=self._build_menu()
        )

    def _create_icon_image(self, bg_color: str, mode: str) -> Image.Image:
        """Generates a smooth 64x64 RGBA icon with badge/symbol."""
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Outer rounded circle
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=bg_color,
            outline=(255, 255, 255, 220),
            width=3
        )

        # Center glyphs
        if mode == "active":
            # Stylized 'A' or Play triangle
            points = [(26, 18), (26, 46), (46, 32)]
            draw.polygon(points, fill=(255, 255, 255, 255))
        elif mode == "paused":
            # Pause bars '||'
            draw.rectangle([22, 20, 28, 44], fill=(255, 255, 255, 255))
            draw.rectangle([36, 20, 42, 44], fill=(255, 255, 255, 255))
        elif mode == "running":
            # Pulse / Dot
            draw.ellipse([22, 22, 42, 42], fill=(255, 255, 255, 255))

        return image

    def _get_tooltip_text(self) -> str:
        threshold_mins = self.idle_threshold_seconds / 60.0
        if self.state == AppState.ACTIVE:
            return f"Teams Anti-AFK: Active (Idle > {threshold_mins:g}m)"
        elif self.state == AppState.RUNNING_ACTION:
            return "Teams Anti-AFK: Running Action..."
        else:
            return "Teams Anti-AFK: Paused (Win+Ctrl+Shift+F to resume)"

    def _build_menu(self) -> Menu:
        """Constructs the system tray context menu."""
        def is_threshold(seconds):
            return lambda item: self.idle_threshold_seconds == seconds

        def set_threshold(seconds):
            def handler(icon, item):
                self.idle_threshold_seconds = seconds
                self._update_ui()
                self._notify("Settings Updated", f"Idle timeout set to {seconds // 60} min(s).")
            return handler

        def toggle_notifs(icon, item):
            self.notifications_enabled = not self.notifications_enabled
            self._update_ui()

        return Menu(
            item(
                lambda text: f"Status: {'ACTIVE (Monitoring)' if self.state == AppState.ACTIVE else ('RUNNING ACTION' if self.state == AppState.RUNNING_ACTION else 'PAUSED')}",
                lambda icon, item: None,
                enabled=False
            ),
            Menu.SEPARATOR,
            item(
                lambda text: "Pause Anti-AFK (Win+Ctrl+Shift+F)" if self.state == AppState.ACTIVE else "Resume Anti-AFK (Win+Ctrl+Shift+F)",
                lambda icon, item: self.toggle_active_state()
            ),
            item(
                "Trigger Routine Now (Test)",
                lambda icon, item: self.trigger_action_manual()
            ),
            Menu.SEPARATOR,
            item(
                "Idle Timeout",
                Menu(
                    item("1 Minute (Quick Test)", set_threshold(60), checked=is_threshold(60), radio=True),
                    item("2 Minutes", set_threshold(120), checked=is_threshold(120), radio=True),
                    item("4 Minutes (Default)", set_threshold(240), checked=is_threshold(240), radio=True),
                    item("5 Minutes", set_threshold(300), checked=is_threshold(300), radio=True),
                    item("10 Minutes", set_threshold(600), checked=is_threshold(600), radio=True),
                )
            ),
            item(
                "Show Desktop Notifications",
                toggle_notifs,
                checked=lambda item: self.notifications_enabled
            ),
            Menu.SEPARATOR,
            item("Exit", lambda icon, item: self.quit())
        )

    def _update_ui(self):
        """Updates tray icon image, tooltip, and menu state."""
        if not self.tray_icon:
            return

        if self.state == AppState.ACTIVE:
            self.tray_icon.icon = self.icon_active
        elif self.state == AppState.RUNNING_ACTION:
            self.tray_icon.icon = self.icon_running
        else:
            self.tray_icon.icon = self.icon_paused

        self.tray_icon.title = self._get_tooltip_text()
        self.tray_icon.menu = self._build_menu()

    def _notify(self, title: str, message: str):
        """Sends a Windows tray notification if enabled."""
        if self.notifications_enabled and self.tray_icon:
            try:
                self.tray_icon.notify(message, title)
            except Exception as e:
                print(f"[Notification Error] {e}")

    def toggle_active_state(self):
        """Toggles between Active and Paused state. Triggered by Hotkey or Tray."""
        with self._lock:
            if self.state == AppState.ACTIVE or self.state == AppState.RUNNING_ACTION:
                # Pause/Stop
                self.state = AppState.PAUSED
                self._action_stop_event.set()
                print(">>> [State Change] Anti-AFK PAUSED / STOPPED")
                self._notify("Teams Anti-AFK", "Anti-AFK Paused.\nPress Win + Ctrl + Shift + F to resume.")
            else:
                # Resume/Active
                self.state = AppState.ACTIVE
                self._action_stop_event.clear()
                print(">>> [State Change] Anti-AFK ACTIVE")
                self._notify("Teams Anti-AFK", f"Anti-AFK Resumed.\nMonitoring for {self.idle_threshold_seconds // 60}m idle.")

        self._update_ui()

    def trigger_action_manual(self):
        """Manually runs the Anti-AFK action."""
        if self._action_thread and self._action_thread.is_alive():
            self._notify("Teams Anti-AFK", "Action is already running.")
            return

        threading.Thread(target=self._run_action_sequence, kwargs={"manual": True}, daemon=True).start()

    def _run_action_sequence(self, manual: bool = False):
        """Worker executing the anti-afk routine and managing state."""
        with self._lock:
            prev_state = self.state
            self.state = AppState.RUNNING_ACTION
            self._action_stop_event.clear()

        self._update_ui()
        if manual:
            self._notify("Teams Anti-AFK", "Starting Anti-AFK Routine...")
        else:
            self._notify("Teams Anti-AFK", f"Idle for {self.idle_threshold_seconds // 60}m detected. Simulating activity...")

        success = perform_anti_afk_routine(
            stop_event=self._action_stop_event,
            log_callback=lambda msg: print(f"[Log] {msg}")
        )

        with self._lock:
            # If user didn't pause during the action, revert to previous state or ACTIVE
            if self.state == AppState.RUNNING_ACTION:
                self.state = prev_state if prev_state != AppState.RUNNING_ACTION else AppState.ACTIVE

        self._update_ui()
        if success:
            print("[Action Completed] Routine finished successfully.")
        else:
            print("[Action Aborted] Routine was canceled or encountered an issue.")

    def _monitor_loop(self):
        """Background thread monitoring system idle time."""
        print("[Monitor] Idle detection loop started.")
        last_action_time = 0.0

        while self.is_running:
            try:
                time.sleep(2.0)

                with self._lock:
                    current_state = self.state
                    threshold = self.idle_threshold_seconds

                if current_state != AppState.ACTIVE:
                    continue

                now = time.time()
                # Ensure at least threshold seconds elapse between automated actions
                if now - last_action_time < threshold:
                    continue

                # Check idle time
                idle_sec = get_idle_seconds()

                if idle_sec >= threshold:
                    # Check if action is already running
                    if self._action_thread and self._action_thread.is_alive():
                        continue

                    print(f"[Monitor] Idle time ({idle_sec:.1f}s) exceeded threshold ({threshold}s). Launching action.")
                    last_action_time = time.time()
                    self._action_thread = threading.Thread(
                        target=self._run_action_sequence,
                        kwargs={"manual": False},
                        daemon=True
                    )
                    self._action_thread.start()
                    # Wait for action thread to finish before next check
                    self._action_thread.join()
                    last_action_time = time.time()
                    time.sleep(3.0)

            except Exception as e:
                print(f"[Monitor Error] {e}")
                time.sleep(5.0)

    def run(self):
        """Starts the tray application, hotkey manager, and monitor loop."""
        print("Starting Teams Anti-AFK Tray Application...")
        print("Hotkey: Win + Ctrl + Shift + F (Stop / Resume)")
        print(f"Default Idle Threshold: {self.idle_threshold_seconds // 60} minutes")

        # Start hotkey listener
        self.hotkey_mgr.start()

        # Start background idle monitor loop
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        # Run tray icon mainloop (blocking on main thread)
        self.tray_icon.run()

    def quit(self):
        """Clean shutdown of tray app and threads."""
        print("Shutting down Teams Anti-AFK...")
        self.is_running = False
        self._action_stop_event.set()
        self.hotkey_mgr.stop()
        if self.tray_icon:
            self.tray_icon.stop()


if __name__ == "__main__":
    app = TeamsAntiAfkTrayApp()
    app.run()
